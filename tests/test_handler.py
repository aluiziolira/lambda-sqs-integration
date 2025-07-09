import json
import pytest
from unittest.mock import patch, MagicMock
import handler
from src.prime_numbers_processing.prime_numbers_manager import PrimeNumberManager


class TestPrimeNumberProcessing:
    """Test suite for the prime_number_processing Lambda function"""

    def test_prime_number_processing_success(self, sample_sqs_event, mock_env):
        """Test successful processing of prime numbers"""
        with patch.object(PrimeNumberManager, 'get_prime_numbers') as mock_get_primes:
            mock_get_primes.return_value = [2, 3, 5, 7, 11]
            
            # Should not raise an exception
            handler.prime_number_processing(sample_sqs_event, None)
            
            # Verify the method was called once
            mock_get_primes.assert_called_once()

    def test_prime_number_processing_no_numbers(self, sample_sqs_event_no_numbers, mock_env, capfd):
        """Test processing when no numbers are provided"""
        handler.prime_number_processing(sample_sqs_event_no_numbers, None)
        
        captured = capfd.readouterr()
        assert "didn't present any numbers to be processed" in captured.out
        assert "test-message-id-2" in captured.out

    def test_prime_number_processing_invalid_json(self, sample_sqs_event_invalid_json, mock_env, capfd):
        """Test processing with invalid JSON in message body"""
        handler.prime_number_processing(sample_sqs_event_invalid_json, None)
        
        captured = capfd.readouterr()
        assert "General Error:" in captured.out

    def test_prime_number_processing_multiple_records(self, mock_env):
        """Test processing multiple SQS records"""
        multi_record_event = {
            "Records": [
                {
                    "messageId": "msg-1",
                    "body": '{"Numbers": [2, 3, 4]}',
                    "receiptHandle": "handle-1"
                },
                {
                    "messageId": "msg-2", 
                    "body": '{"Numbers": [5, 6, 7]}',
                    "receiptHandle": "handle-2"
                }
            ]
        }
        
        with patch.object(PrimeNumberManager, 'get_prime_numbers') as mock_get_primes:
            mock_get_primes.return_value = [2, 3, 5, 7]
            
            handler.prime_number_processing(multi_record_event, None)
            
            # Should be called twice (once for each record)
            assert mock_get_primes.call_count == 2

    def test_prime_number_processing_exception_handling(self, mock_env, capfd):
        """Test exception handling in prime number processing"""
        event_with_error = {
            "Records": [
                {
                    "messageId": "error-msg",
                    "body": '{"Numbers": [2, 3]}',
                    "receiptHandle": "error-handle"
                }
            ]
        }
        
        with patch.object(PrimeNumberManager, 'get_prime_numbers') as mock_get_primes:
            mock_get_primes.side_effect = Exception("Test error")
            
            handler.prime_number_processing(event_with_error, None)
            
            captured = capfd.readouterr()
            assert "General Error: Test error" in captured.out

    def test_prime_number_processing_prints_event(self, sample_sqs_event, mock_env, capfd):
        """Test that the event is printed for debugging"""
        with patch.object(PrimeNumberManager, 'get_prime_numbers') as mock_get_primes:
            mock_get_primes.return_value = []
            
            handler.prime_number_processing(sample_sqs_event, None)
            
            captured = capfd.readouterr()
            assert "Event received" in captured.out
            assert "Processing prime numbers" in captured.out

    def test_prime_number_processing_with_primes_found(self, sample_sqs_event, mock_env, capfd):
        """Test output when prime numbers are found"""
        with patch.object(PrimeNumberManager, 'get_prime_numbers') as mock_get_primes:
            mock_get_primes.return_value = [2, 3, 5, 7]
            
            handler.prime_number_processing(sample_sqs_event, None)
            
            captured = capfd.readouterr()
            assert "Prime numbers found: 2,3,5,7" in captured.out