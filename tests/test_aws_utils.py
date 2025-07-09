import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from src.utils.aws_utils import AWSUtils


class TestAWSUtils:
    """Test suite for the AWSUtils class"""

    def test_send_sqs_message_success(self, mock_sqs_client):
        """Test successful SQS message sending"""
        client, queue_url = mock_sqs_client
        
        # Test data
        body = "test message"
        attributes = {
            "TestAttribute": {
                "DataType": "String",
                "StringValue": "test_value"
            }
        }
        
        # Mock the boto3 client
        with patch('boto3.client') as mock_boto_client:
            mock_boto_client.return_value = client
            
            result = AWSUtils.send_sqs_message(queue_url, body, attributes)
            
            # Should return 200 for successful send
            assert result == 200

    def test_send_sqs_message_with_custom_region(self):
        """Test SQS message sending with custom region"""
        queue_url = "https://sqs.us-west-2.amazonaws.com/123456789012/test-queue"
        body = "test message"
        attributes = {}
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_client.send_message.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            result = AWSUtils.send_sqs_message(queue_url, body, attributes, region="us-west-2")
            
            assert result == 200
            mock_boto_client.assert_called_with("sqs", region_name="us-west-2")

    def test_send_sqs_message_client_error(self, capfd):
        """Test SQS message sending with ClientError"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        body = "test message"
        attributes = {}
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            error = ClientError(
                error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
                operation_name='SendMessage'
            )
            mock_client.send_message.side_effect = error
            mock_boto_client.return_value = mock_client
            
            with pytest.raises(ClientError):
                AWSUtils.send_sqs_message(queue_url, body, attributes)
            
            captured = capfd.readouterr()
            assert "ClientError while sending sqs message" in captured.out

    def test_send_sqs_message_parameters(self):
        """Test that send_sqs_message calls with correct parameters"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        body = "test message body"
        attributes = {
            "TestAttr": {
                "DataType": "String",
                "StringValue": "test_value"
            }
        }
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_client.send_message.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            AWSUtils.send_sqs_message(queue_url, body, attributes)
            
            mock_client.send_message.assert_called_once_with(
                QueueUrl=queue_url,
                DelaySeconds=10,
                MessageAttributes=attributes,
                MessageBody=body
            )

    def test_send_batch_sqs_messages_success(self):
        """Test successful batch SQS message sending"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        bodies = ["message1", "message2", "message3"]
        attributes = [
            {"Attr1": {"DataType": "String", "StringValue": "value1"}},
            {"Attr2": {"DataType": "String", "StringValue": "value2"}},
            {"Attr3": {"DataType": "String", "StringValue": "value3"}}
        ]
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_client.send_message_batch.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            result = AWSUtils.send_batch_sqs_messages(queue_url, bodies, attributes)
            
            assert result == 200
            mock_client.send_message_batch.assert_called_once()

    def test_send_batch_sqs_messages_with_custom_region(self):
        """Test batch SQS message sending with custom region"""
        queue_url = "https://sqs.eu-west-1.amazonaws.com/123456789012/test-queue"
        bodies = ["message1"]
        attributes = [{"Attr1": {"DataType": "String", "StringValue": "value1"}}]
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_client.send_message_batch.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            result = AWSUtils.send_batch_sqs_messages(queue_url, bodies, attributes, region="eu-west-1")
            
            assert result == 200
            mock_boto_client.assert_called_with("sqs", region_name="eu-west-1")

    def test_send_batch_sqs_messages_client_error(self, capfd):
        """Test batch SQS message sending with ClientError"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        bodies = ["message1"]
        attributes = [{"Attr1": {"DataType": "String", "StringValue": "value1"}}]
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            error = ClientError(
                error_response={'Error': {'Code': 'InvalidParameterValue', 'Message': 'Invalid parameter'}},
                operation_name='SendMessageBatch'
            )
            mock_client.send_message_batch.side_effect = error
            mock_boto_client.return_value = mock_client
            
            with pytest.raises(ClientError):
                AWSUtils.send_batch_sqs_messages(queue_url, bodies, attributes)
            
            captured = capfd.readouterr()
            assert "ClientError while sending sqs message" in captured.out

    def test_send_batch_sqs_messages_message_format(self):
        """Test that batch messages are formatted correctly"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        bodies = ["msg1", "msg2"]
        attributes = [
            {"Attr1": {"DataType": "String", "StringValue": "val1"}},
            {"Attr2": {"DataType": "String", "StringValue": "val2"}}
        ]
        
        with patch('boto3.client') as mock_boto_client, \
             patch('uuid.uuid4') as mock_uuid:
            
            mock_uuid.side_effect = ["uuid1", "uuid2"]
            mock_client = MagicMock()
            mock_client.send_message_batch.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            AWSUtils.send_batch_sqs_messages(queue_url, bodies, attributes)
            
            # Check the call arguments
            call_args = mock_client.send_message_batch.call_args
            entries = call_args[1]['Entries']
            
            assert len(entries) == 2
            assert entries[0]['Id'] == 'uuid1'
            assert entries[0]['MessageBody'] == 'msg1'
            assert entries[0]['MessageAttributes'] == attributes[0]
            assert entries[1]['Id'] == 'uuid2'
            assert entries[1]['MessageBody'] == 'msg2'
            assert entries[1]['MessageAttributes'] == attributes[1]

    def test_send_batch_sqs_messages_empty_lists(self):
        """Test batch sending with empty lists"""
        queue_url = "https://sqs.us-east-2.amazonaws.com/123456789012/test-queue"
        bodies = []
        attributes = []
        
        with patch('boto3.client') as mock_boto_client:
            mock_client = MagicMock()
            mock_client.send_message_batch.return_value = {
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }
            mock_boto_client.return_value = mock_client
            
            result = AWSUtils.send_batch_sqs_messages(queue_url, bodies, attributes)
            
            assert result == 200
            # Should still call send_message_batch with empty entries
            call_args = mock_client.send_message_batch.call_args
            entries = call_args[1]['Entries']
            assert len(entries) == 0