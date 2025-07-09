import uuid

import boto3
from botocore.exceptions import ClientError


class AWSUtils:
    @staticmethod
    def send_sqs_message(queue_url, body, attributes: dict, region="us-east-2"):
        """Sends a single message to the provided SQS url
        :param queue_url: aws address of the target SQS
        :param body: body of the message to be sent
        :param attributes: attributes of the given message
        :returns: True(200) if message was successfully sent, else raises an Exception
        """
        try:
            queue_client = boto3.client("sqs", region_name=region)

            response = queue_client.send_message(
                QueueUrl=queue_url,
                DelaySeconds=10,
                MessageAttributes=attributes,
                MessageBody=body,
            )
            return response["ResponseMetadata"]["HTTPStatusCode"]
        except ClientError as e:
            print(f"ClientError while sending sqs message to {queue_url}: {e}")
            raise e

    @staticmethod
    def send_batch_sqs_messages(
        queue_url, bodies, attributes: dict, region="us-east-2"
    ):
        """Sends a single message to the provided SQS url
        :param queue_url: aws address of the target SQS
        :param bodies: bodies of the messages to be sent
        :param attributes: attributes of the given messages
        :returns: True(200) if message was successfully sent, else raises an Exception
        """
        try:
            queue_client = boto3.client("sqs", region_name=region)
            messages = []

            for body, attribute in zip(bodies, attributes):
                messages.append(
                    {
                        "Id": str(uuid.uuid4()),
                        "MessageBody": body,
                        "MessageAttributes": attribute,
                    }
                )

            response = queue_client.send_message_batch(
                QueueUrl=queue_url, Entries=messages
            )

            return response["ResponseMetadata"]["HTTPStatusCode"]
        except ClientError as e:
            print(f"ClientError while sending sqs message to {queue_url}: {e}")
            raise e
