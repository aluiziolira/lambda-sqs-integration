import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    with patch.dict(
        os.environ,
        {
            "SQS_PRIMES_TARGET": "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue",
            "AWS_REGION": "us-east-2",
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
        },
    ):
        yield


@pytest.fixture
def sample_sqs_event():
    """Sample SQS event for testing"""
    return {
        "Records": [
            {
                "messageId": "test-message-id-1",
                "receiptHandle": "test-receipt-handle",
                "body": '{"Numbers": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}',
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:test-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@pytest.fixture
def sample_sqs_event_no_numbers():
    """Sample SQS event with no numbers for testing"""
    return {
        "Records": [
            {
                "messageId": "test-message-id-2",
                "receiptHandle": "test-receipt-handle",
                "body": '{"Numbers": ""}',
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:test-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@pytest.fixture
def sample_sqs_event_invalid_json():
    """Sample SQS event with invalid JSON for testing"""
    return {
        "Records": [
            {
                "messageId": "test-message-id-3",
                "receiptHandle": "test-receipt-handle",
                "body": "invalid json",
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:test-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@pytest.fixture
def mock_sqs_client():
    """Mock SQS client for testing"""
    mock_client = MagicMock()
    mock_client.send_message.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }
    mock_client.send_message_batch.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }
    queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
    yield mock_client, queue_url
