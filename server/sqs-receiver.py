import boto3
import os

#get client
client = boto3.client('sqs', region_name='us-east-1',
                      aws_access_key_id="ACCESS_KEY_HERE",
                      aws_secret_access_key="SECRET_KEY_HERE")

#SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue.fifo'

#get first available message in queue
response = client.receive_message(
    QueueUrl=queue_url,
    AttributeNames=['SentTimestamp'],
    MaxNumberOfMessages=1,
    MessageAttributeNames=['All'],
    VisibilityTimeout=10,
    WaitTimeSeconds=0
    )

message = response['Messages'][0]
receipt_handle = message['ReceiptHandle']

#Delete message from queue

# Delete message from queue
client.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
    )

print('Received message: %s' % message)

image_link_s3 = message['Body']
print(image_link_s3)
