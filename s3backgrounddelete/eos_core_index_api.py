import http.client, urllib.parse
import sys
import datetime
import json
import logging

from eos_list_index_response import EOSCoreListIndexResponse
from eos_core_client import EOSCoreClient
from eos_core_error_respose import EOSCoreErrorResponse
from eos_core_success_response import EOSCoreSuccessResponse

# EOSCoreIndexApi supports index REST-API's List & Put

class EOSCoreIndexApi(EOSCoreClient):

    _logger = None

    def __init__(self, config, logger = None):
        if (logger is None):
            self._logger = logging.getLogger("EOSCoreIndexApi")
        else:
            self._logger = logger
        self.config = config
        super(EOSCoreIndexApi, self).__init__(self.config, self._logger)

    def list(self, index):
        if index is None:
            self._logger.error("Index Id is required.")
            return None

        self._logger.info("Processing request in IndexAPI")
        request_uri = '/indexes/' + index
        try:
            response = super().get(request_uri)
        except Exception as ex:
            self._logger.error(str(ex))
            return None

        if response['status'] == 200:
            self._logger.info('Successfully listed Index details.')
            return True, EOSCoreListIndexResponse(response['body'])
        else:
            self._logger.info('Failed to list Index details.')
            return False, EOSCoreErrorResponse(response['status'], response['reason'], response['body'])

    def put(self, index):

        if index is None:
            self._logger.info("Index Id is required.")
            return None

        request_uri = '/indexes/' + index
        try:
            response = super().put(request_uri)
        except Exception as ex:
            self._logger.error(str(ex))
            return None

        if response['status'] == 201:
            self._logger.info('Successfully added Index.')
            return True, EOSCoreSuccessResponse(response['body'])
        else:
            self._logger.info('Failed to add Index.')
            return False, EOSCoreErrorResponse(response['status'], response['reason'], response['body'])