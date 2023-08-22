import json

from prime_numbers_processing.prime_numbers_manager import PrimeNumberManager


def prime_number_processing(event, context):
    print("Event received...\nProcessing prime numbers")
    try:
        for record in event["Records"]:
            event_data = json.loads(record["body"])
            numbers = event_data.get("Numbers", "")
            if numbers:
                pnm = PrimeNumberManager()
                prime_numbers = pnm.get_prime_numbers(numbers)
                print(f"Prime numbers found: {','.join(map(str, prime_numbers))}")
            else:
                print(
                    f"Message Id: {record['messageId']} didn't present any numbers to be processed."
                )

    except Exception as e:
        print(f"General Error: {e}")
