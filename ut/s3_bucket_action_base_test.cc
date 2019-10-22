/*
 * COPYRIGHT 2019 SEAGATE LLC
 *
 * THIS DRAWING/DOCUMENT, ITS SPECIFICATIONS, AND THE DATA CONTAINED
 * HEREIN, ARE THE EXCLUSIVE PROPERTY OF SEAGATE TECHNOLOGY
 * LIMITED, ISSUED IN STRICT CONFIDENCE AND SHALL NOT, WITHOUT
 * THE PRIOR WRITTEN PERMISSION OF SEAGATE TECHNOLOGY LIMITED,
 * BE REPRODUCED, COPIED, OR DISCLOSED TO A THIRD PARTY, OR
 * USED FOR ANY PURPOSE WHATSOEVER, OR STORED IN A RETRIEVAL SYSTEM
 * EXCEPT AS ALLOWED BY THE TERMS OF SEAGATE LICENSES AND AGREEMENTS.
 *
 * YOU SHOULD HAVE RECEIVED A COPY OF SEAGATE'S LICENSE ALONG WITH
 * THIS RELEASE. IF NOT PLEASE CONTACT A SEAGATE REPRESENTATIVE
 * http://www.seagate.com/contact
 *
 * Original author:  Rajesh Nambiar  <rajesh.nambiar@seagate.com>
 * Original creation date: Oct-9-2019
 */

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "mock_s3_bucket_metadata.h"
#include "mock_s3_clovis_wrapper.h"
#include "mock_s3_factory.h"
#include "mock_s3_request_object.h"
#include "s3_bucket_action_base.h"

using ::testing::AtLeast;

#define CREATE_BUCKET_METADATA_OBJ                      \
  do {                                                  \
    action_under_test_ptr->bucket_metadata =            \
        action_under_test_ptr->bucket_metadata_factory  \
            ->create_bucket_metadata_obj(request_mock); \
  } while (0)

class S3BucketActionTestBase : public S3BucketAction {
 public:
  S3BucketActionTestBase(
      std::shared_ptr<S3RequestObject> req,
      std::shared_ptr<S3BucketMetadataFactory> bucket_meta_factory,
      bool check_shutdown, std::shared_ptr<S3AuthClientFactory> auth_factory,
      bool skip_auth)
      : S3BucketAction(req, bucket_meta_factory, check_shutdown, auth_factory,
                       skip_auth) {
    fetch_bucket_info_failed_called = 0;
    response_called = 0;
  };
  void fetch_bucket_info_failed() { fetch_bucket_info_failed_called = 1; }

  void send_response_to_s3_client() {
    response_called += 1;
  };

  int fetch_bucket_info_failed_called;
  int response_called;
};

class S3BucketActionTest : public testing::Test {
 protected:  // You should make the members protected s.t. they can be
             // accessed from sub-classes.
  S3BucketActionTest() {
    call_count_one = 0;
    evhtp_request_t *req = NULL;
    EvhtpInterface *evhtp_obj_ptr = new EvhtpWrapper();
    request_mock = std::make_shared<MockS3RequestObject>(req, evhtp_obj_ptr);
    mock_auth_factory = std::make_shared<MockS3AuthClientFactory>(request_mock);
    bucket_meta_factory =
        std::make_shared<MockS3BucketMetadataFactory>(request_mock);
    action_under_test_ptr = std::make_shared<S3BucketActionTestBase>(
        request_mock, bucket_meta_factory, true, mock_auth_factory, false);
  }

  std::shared_ptr<MockS3RequestObject> request_mock;
  std::shared_ptr<S3BucketActionTestBase> action_under_test_ptr;
  std::shared_ptr<MockS3BucketMetadataFactory> bucket_meta_factory;
  std::shared_ptr<MockS3AuthClientFactory> mock_auth_factory;
  int call_count_one;

 public:
  void func_callback_one() { call_count_one += 1; }
};

TEST_F(S3BucketActionTest, Constructor) {
  EXPECT_NE(0, action_under_test_ptr->number_of_tasks());
  EXPECT_TRUE(action_under_test_ptr->bucket_metadata_factory != nullptr);
}

TEST_F(S3BucketActionTest, FetchBucketInfo) {
  EXPECT_CALL(*(bucket_meta_factory->mock_bucket_metadata), load(_, _))
      .Times(AtLeast(1));
  action_under_test_ptr->fetch_bucket_info();
}

TEST_F(S3BucketActionTest, LoadMetadata) {
  EXPECT_CALL(*(bucket_meta_factory->mock_bucket_metadata), load(_, _))
      .Times(AtLeast(1));
  EXPECT_TRUE(action_under_test_ptr->bucket_metadata_factory != nullptr);
  action_under_test_ptr->load_metadata();
}

TEST_F(S3BucketActionTest, SetAuthorizationMeta) {
  action_under_test_ptr->clear_tasks();
  action_under_test_ptr->add_task(
      std::bind(&S3BucketActionTest::func_callback_one, this));
  action_under_test_ptr->bucket_metadata =
      action_under_test_ptr->bucket_metadata_factory
          ->create_bucket_metadata_obj(request_mock);
  action_under_test_ptr->set_authorization_meta();
  EXPECT_EQ(1, call_count_one);
}