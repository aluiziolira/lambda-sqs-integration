import pytest
from unittest.mock import patch, MagicMock
from src.prime_numbers_processing.prime_numbers_manager import PrimeNumberManager
from src.utils.aws_utils import AWSUtils


class TestPrimeNumberManager:
    """Test suite for the PrimeNumberManager class"""

    def test_init(self):
        """Test PrimeNumberManager initialization"""
        manager = PrimeNumberManager()
        assert manager.prime_numbers == []
        assert manager.non_prime_numbers == []

    def test_context_manager_enter(self):
        """Test context manager __enter__ method"""
        manager = PrimeNumberManager()
        with manager as ctx:
            assert ctx is manager

    def test_context_manager_exit_no_exception(self):
        """Test context manager __exit__ method without exception"""
        manager = PrimeNumberManager()
        result = manager.__exit__(None, None, None)
        assert result is None

    def test_context_manager_exit_with_exception(self, capfd):
        """Test context manager __exit__ method with exception"""
        manager = PrimeNumberManager()
        exception_type = ValueError
        result = manager.__exit__(exception_type, ValueError("test"), None)
        
        captured = capfd.readouterr()
        assert "ValueError" in captured.out
        assert result is None

    def test_get_prime_numbers_with_primes(self, mock_env):
        """Test get_prime_numbers with numbers containing primes"""
        numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            # Expected primes: 2, 3, 5, 7, 11
            assert result == [2, 3, 5, 7, 11]
            assert manager.prime_numbers == [2, 3, 5, 7, 11]
            assert manager.non_prime_numbers == [4, 6, 8, 9, 10]
            
            # Verify SQS message was sent
            mock_send.assert_called_once()

    def test_get_prime_numbers_no_primes(self, mock_env):
        """Test get_prime_numbers with no prime numbers"""
        numbers = [4, 6, 8, 9, 10]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == []
            assert manager.prime_numbers == []
            assert manager.non_prime_numbers == [4, 6, 8, 9, 10]
            
            # SQS message should not be sent when no primes found
            mock_send.assert_not_called()

    def test_get_prime_numbers_single_prime(self, mock_env):
        """Test get_prime_numbers with single prime number"""
        numbers = [7]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == [7]
            assert manager.prime_numbers == [7]
            assert manager.non_prime_numbers == []
            
            mock_send.assert_called_once()

    def test_get_prime_numbers_single_non_prime(self, mock_env):
        """Test get_prime_numbers with single non-prime number"""
        numbers = [4]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == []
            assert manager.prime_numbers == []
            assert manager.non_prime_numbers == [4]
            
            mock_send.assert_not_called()

    def test_get_prime_numbers_empty_list(self, mock_env):
        """Test get_prime_numbers with empty list"""
        numbers = []
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == []
            assert manager.prime_numbers == []
            assert manager.non_prime_numbers == []
            
            mock_send.assert_not_called()

    def test_get_prime_numbers_sqs_message_attributes(self, mock_env):
        """Test that correct message attributes are sent to SQS"""
        numbers = [2, 3, 5]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            manager.get_prime_numbers(numbers)
            
            # Check that the correct arguments were passed
            args, kwargs = mock_send.call_args
            queue_url, message_body, attributes = args
            
            assert queue_url == 'https://sqs.us-east-2.amazonaws.com/123456789012/test-queue'
            assert message_body == '[2, 3, 5]'
            assert attributes == {
                "NumberOfPrimes": {
                    "DataType": "Number",
                    "StringValue": "3"
                }
            }

    def test_get_prime_numbers_sqs_success_message(self, mock_env, capfd):
        """Test success message is printed when SQS message is sent"""
        numbers = [2, 3]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            manager.get_prime_numbers(numbers)
            
            captured = capfd.readouterr()
            assert "Prime numbers sent to the target SQS!" in captured.out

    def test_get_prime_numbers_sqs_no_response(self, mock_env, capfd):
        """Test when SQS returns no response"""
        numbers = [2, 3]
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = None
            
            manager = PrimeNumberManager()
            manager.get_prime_numbers(numbers)
            
            captured = capfd.readouterr()
            assert "Prime numbers sent to the target SQS!" not in captured.out

    def test_get_prime_numbers_large_numbers(self, mock_env):
        """Test get_prime_numbers with larger numbers"""
        numbers = [97, 98, 99, 100, 101]  # 97 and 101 are prime
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == [97, 101]
            assert manager.prime_numbers == [97, 101]
            assert manager.non_prime_numbers == [98, 99, 100]

    def test_get_prime_numbers_edge_cases(self, mock_env):
        """Test get_prime_numbers with edge cases like 1 and 2"""
        numbers = [1, 2]  # 1 is not prime, 2 is prime
        
        with patch.object(AWSUtils, 'send_sqs_message') as mock_send:
            mock_send.return_value = 200
            
            manager = PrimeNumberManager()
            result = manager.get_prime_numbers(numbers)
            
            assert result == [2]
            assert manager.prime_numbers == [2]
            assert manager.non_prime_numbers == [1]