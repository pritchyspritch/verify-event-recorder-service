import os
import boto3
import json

from moto import mock_s3
from unittest import TestCase
from datetime import datetime
from testfixtures import LogCapture
from retrying import retry
import string
import random

from src import fraud_handler

S_INDEX = 'fraud-test-index'
TODAY = str(datetime.now())
LETTERS = string.ascii_lowercase
RANDOM_STRING = ''.join(random.choice(LETTERS) for i in range(8))
KEY = 'verify-fraud-events-{}-{}.log'.format(RANDOM_STRING, today)


@mock_s3
class FraudHandlerTest(TestCase):
    __s3_client = None

    @classmethod
    def setUpClass(cls):
        cls.connect()

    def setUp(self):
        self.__setup_stub_aws_config()

    def __setup_s3(self):
        self.__s3_client = boto3.client('s3')
        self.__s3_client.create_bucket(
            Bucket='key-bucket',
        )

    def __write_import_file_to_s3(self, messages):
        self.__write_to_s3(IMPORT_BUCKET_NAME, IMPORT_FILE_NAME, '\n'.join(messages))

    def __write_to_s3(self, bucket_name, filename, content):
        self.__s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=content
        )

    def __setup_stub_aws_config(self):
        os.environ = {
            'AWS_DEFAULT_REGION': 'eu-west-2',
            'AWS_ACCESS_KEY_ID': 'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY': 'AWS_SECRET_ACCESS_KEY'
        }

    def __create_fraud_event_string(self, event_id, session_id, fraud_event_id):
        return json.dumps({
            '_id': {
                '$oid': event_id
            },
            'document': {
                'eventId': event_id,
                'eventType': EVENT_TYPE,
                'timestamp': ISO3359_TIMESTAMP,
                'originatingService': ORIGINATING_SERVICE,
                'sessionId': session_id,
                'details': {
                    'session_event_type': FRAUD_SESSION_EVENT_TYPE,
                    'pid': PID,
                    'request_id': REQUEST_ID,
                    'idp_entity_id': IDP_ENTITY_ID,
                    'idp_fraud_event_id': fraud_event_id,
                    'gpg45_status': GPG45_STATUS
                }
            }
        })

    def __create_s3_event(self):
        return {
          "Records": [
            {
              "s3": {
                "bucket": {
                  "name": IMPORT_BUCKET_NAME,
                },
                "object": {
                  "key": IMPORT_FILE_NAME,
                }
              }
            }
          ]
        }
