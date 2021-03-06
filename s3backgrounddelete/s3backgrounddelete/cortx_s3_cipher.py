#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

#!/usr/bin/env python3

import argparse
import base64
import sys

from s3backgrounddelete.cortx_cluster_config import CORTXClusterConfig, CipherInvalidToken
from cortx.utils.security.cipher import Cipher

class CortxS3Cipher:

    def __init__(self, config = None, use_base64 = False, key_len = 20, const_key = "default"):
        """Load and initialise s3cipher."""
        self.use_base64 = use_base64
        self.key_len = key_len
        self.const_key = const_key
        self.config = config
        if (self.config is None):
            self.config = CORTXClusterConfig()

        try:
            self.cluster_id = self.config.get_cluster_id()
        except KeyError as err:
            print("Fail to parse cluster_id from config file")
            sys.exit(1)

    @staticmethod
    def encrypt(key: str, data: str):
        edata = Cipher.encrypt(bytes(key, 'utf-8'), bytes(data, 'utf-8'))
        return edata.decode("utf-8")

    @staticmethod
    def decrypt(key: str, data: str):
        ddata = Cipher.decrypt(bytes(key, 'utf-8'), bytes(data, 'utf-8'))
        return ddata.decode("utf-8")

    def generate_key(self):
        key = Cipher.generate_key(self.cluster_id, self.const_key)
        return key.decode("utf-8")

    def get_key(self):
        try:
            key = Cipher.generate_key(self.cluster_id, self.const_key)
        except Exception as err:
            raise CipherInvalidToken("Cipher generate key failed with error : {0}".format(err))

        if(self.use_base64):
            key = base64.b64encode(key, str.encode("AZ"))

        if(len(key) < self.key_len):
            while(len(key) < self.key_len):
                key = key * 2
            key = key[:self.key_len]
        elif(len(key) > self.key_len):
            key = key[:self.key_len]

        return key.decode("utf-8")

    def run(self):
        parser = argparse.ArgumentParser(description='S3Cipher tool used for obtaining encrypted keys',add_help=False)
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Show this help message and exit')
        parser.add_argument("--use_base64", help="Used to obtain alphanumeric base64 keys", action="store_true")
        parser.add_argument("--key_len", help="Key length to be obtained", type=int)
        parser.add_argument("--const_key", help="Constant key name to be used during encryption", type=str)
        parser.add_argument("--encrypt", help="encrypt provided bytes of data, with provided key", action="store_true")
        parser.add_argument("--decrypt", help="decrypt provided bytes of data, with provided key", action="store_true")
        parser.add_argument("--generate_key", help="generate key to encrypt or decrypt data with it, use '--const_key' option with this.", action="store_true")
        parser.add_argument("--key", help="key (in bytes) to be used in encrypting or decrypting bytes of data")
        parser.add_argument("--data", help="bytes which needs to be encrypted or decrypted using provided key", type=str)

        args = parser.parse_args()

        if args.use_base64:
            use_base64_flag = True
        else:
            use_base64_flag = False

        if args.key_len:
            key_len_flag = args.key_len
        else:
            key_len_flag = 0

        if args.const_key:
            const_key_flag = args.const_key
        else:
            const_key_flag = "default_key"

        if args.key:
            key = args.key
        if args.data:
            data = args.data

        s3_cipher = CortxS3Cipher(None, use_base64_flag, key_len_flag, const_key_flag)

        try:
            if args.encrypt:
                print(s3_cipher.encrypt(key, data))
            elif args.decrypt:
                print(s3_cipher.decrypt(key, data))
            elif args.generate_key:
                print(s3_cipher.generate_key())
            else:
                print(s3_cipher.get_key())
        except CipherInvalidToken as err:
            print("Cipher generate key failed with error : {0}".format(err))
            sys.exit(1)
