"""
Basic tests to demonstrate coverage of core functionality.
These tests focus on testing the core logic with proper mocking.
"""
import pytest
from unittest.mock import patch, MagicMock
import json
import handler
from src.prime_numbers_processing.prime_numbers_manager import PrimeNumberManager
from src.utils.aws_utils import AWSUtils


class TestCoverageBasic:
    """Basic test suite to achieve 85%+ coverage"""

    @patch('src.utils.aws_utils.AWSUtils.send_sqs_message')
    def test_prime_number_manager_basic_functionality(self, mock_send_sqs, mock_env):
        """Test basic prime number processing functionality"""
        mock_send_sqs.return_value = 200
        
        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([2, 3, 4, 5, 6])
        
        assert result == [2, 3, 5]
        assert manager.prime_numbers == [2, 3, 5]
        assert manager.non_prime_numbers == [4, 6]
        mock_send_sqs.assert_called_once()

    @patch('src.utils.aws_utils.AWSUtils.send_sqs_message')
    def test_prime_number_manager_no_primes(self, mock_send_sqs, mock_env):
        """Test prime number processing with no primes"""
        manager = PrimeNumberManager()
        result = manager.get_prime_numbers([4, 6, 8, 9])
        
        assert result == []
        assert manager.prime_numbers == []
        assert manager.non_prime_numbers == [4, 6, 8, 9]
        mock_send_sqs.assert_not_called()

    @patch('src.prime_numbers_processing.prime_numbers_manager.PrimeNumberManager.get_prime_numbers')
    def test_handler_basic_functionality(self, mock_get_primes, mock_env):
        """Test basic handler functionality"""
        mock_get_primes.return_value = [2, 3, 5]
        
        event = {
            "Records": [
                {
                    "messageId": "test-1",
                    "body": '{"Numbers": [2, 3, 4, 5]}',
                    "receiptHandle": "test-handle"
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
                    "receiptHandle": "test-handle"
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
                    "body": 'invalid json',
                    "receiptHandle": "test-handle"
                }
            ]
        }
        
        handler.prime_number_processing(event, None)
        
        captured = capfd.readouterr()
        assert "General Error:" in captured.out

    def test_prime_number_manager_context_manager(self):
        """Test PrimeNumberManager context manager"""
        manager = PrimeNumberManager()
        
        # Test __enter__
        with manager as ctx:
            assert ctx is manager
        
        # Test __exit__ without exception
        result = manager.__exit__(None, None, None)
        assert result is None
        
        # Test __exit__ with exception
        with pytest.capture_stdout() as captured:
            result = manager.__exit__(ValueError, ValueError("test"), None)
            assert result is None