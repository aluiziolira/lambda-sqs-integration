"""
Basic tests to demonstrate coverage of core functionality.
These tests focus on testing the core logic with proper mocking.
"""

from unittest.mock import patch, MagicMock
import handler
from src.prime_numbers_processing.prime_numbers_manager import PrimeNumberManager


class TestCoverageBasic:
    """Basic test suite to achieve 85%+ coverage"""

    @patch("boto3.client")
    def test_prime_number_manager_basic_functionality(self, mock_boto_client, mock_env):
        """Test basic prime number processing functionality"""
        # Mock the boto3 client
        mock_client = MagicMock()
        mock_client.send_message.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        mock_boto_client.return_value = mock_client

        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([2, 3, 4, 5, 6])

        assert result == [2, 3, 5]
        assert manager.prime_numbers == [2, 3, 5]
        assert manager.non_prime_numbers == [4, 6]
        mock_client.send_message.assert_called_once()

    def test_prime_number_manager_no_primes(self, mock_env):
        """Test prime number processing with no primes"""
        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([4, 6, 8, 9])

        assert result == []
        assert manager.prime_numbers == []
        assert manager.non_prime_numbers == [4, 6, 8, 9]

    @patch(
        "prime_numbers_processing.prime_numbers_manager.PrimeNumberManager.get_prime_numbers"
    )
    def test_handler_basic_functionality(self, mock_get_primes, mock_env):
        """Test basic handler functionality"""
        mock_get_primes.return_value = [2, 3, 5]

        event = {
            "Records": [
                {
                    "messageId": "test-1",
                    "body": '{"Numbers": [2, 3, 4, 5]}',
                    "receiptHandle": "test-handle",
                }
            ]
        }

        # Should not raise an exception
        handler.prime_number_processing(event, None)
        mock_get_primes.assert_called_once()

    def test_handler_no_numbers(self, mock_env, capfd):
        """Test handler with no numbers"""
        event = {
            "Records": [
                {
                    "messageId": "test-2",
                    "body": '{"Numbers": ""}',
                    "receiptHandle": "test-handle",
                }
            ]
        }

        handler.prime_number_processing(event, None)

        captured = capfd.readouterr()
        assert "didn't present any numbers to be processed" in captured.out

    def test_handler_invalid_json(self, mock_env, capfd):
        """Test handler with invalid JSON"""
        event = {
            "Records": [
                {
                    "messageId": "test-3",
                    "body": "invalid json",
                    "receiptHandle": "test-handle",
                }
            ]
        }

        handler.prime_number_processing(event, None)

        captured = capfd.readouterr()
        assert "General Error:" in captured.out

    def test_prime_number_manager_context_manager(self, capfd):
        """Test PrimeNumberManager context manager"""
        manager = PrimeNumberManager()

        # Test __enter__
        with manager as ctx:
            assert ctx is manager

        # Test __exit__ without exception
        result = manager.__exit__(None, None, None)
        assert result is None

        # Test __exit__ with exception
        result = manager.__exit__(ValueError, ValueError("test"), None)
        assert result is None

        # Check that the exception type was printed
        captured = capfd.readouterr()
        assert "ValueError" in captured.out

    @patch("boto3.client")
    def test_prime_number_manager_with_sqs_response(
        self, mock_boto_client, mock_env, capfd
    ):
        """Test prime number manager with SQS response"""
        # Mock the boto3 client
        mock_client = MagicMock()
        mock_client.send_message.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        mock_boto_client.return_value = mock_client

        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([2, 3])

        assert result == [2, 3]
        captured = capfd.readouterr()
        assert "Prime numbers sent to the target SQS!" in captured.out

    @patch("boto3.client")
    def test_prime_number_manager_no_sqs_response(
        self, mock_boto_client, mock_env, capfd
    ):
        """Test prime number manager with no SQS response"""
        # Mock the boto3 client to return None response
        mock_client = MagicMock()
        mock_client.send_message.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": None}
        }
        mock_boto_client.return_value = mock_client

        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([2, 3])

        assert result == [2, 3]
        captured = capfd.readouterr()
        assert "Prime numbers sent to the target SQS!" not in captured.out
