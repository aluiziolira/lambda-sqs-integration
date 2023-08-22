import os
import sympy

from utils.aws_utils import AWSUtils


class PrimeNumberManager:
    def __init__(self):
        self.prime_numbers = []
        self.non_prime_numbers = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_type)
        return None

    def get_prime_numbers(self, numbers: list):
        """Processes the given numbers and enqueues the primes found to an SQS
        :param numbers: List of numbers provided by the SQS event that triggered the Lambda
        :returns: List with all prime numbers found
        """
        for number in numbers:
            if sympy.isprime(number):
                self.prime_numbers.append(number)
            else:
                self.non_prime_numbers.append(number)

        if self.prime_numbers:
            queue_url = os.environ["SQS_PRIMES_TARGET"]
            attributes = {
                "NumberOfPrimes": {
                    "DataType": "Number",
                    "StringValue": f"{len(self.prime_numbers)}",
                }
            }
            response = AWSUtils.send_sqs_message(
                queue_url, self.prime_numbers, attributes
            )
            if response:
                print("Prime numbers sent to the target SQS!")

        return self.prime_numbers
