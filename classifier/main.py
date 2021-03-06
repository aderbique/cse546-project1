import os
import boto3
from s3_url import S3Url

#get client
sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3')

#SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue.fifo'

def get_num_messages_available():
    """ Returns the number of messages in the queue """
    response = sqs.get_queue_attributes(QueueUrl=queue_url,AttributeNames=['ApproximateNumberOfMessages'])
    messages_available = response['Attributes']['ApproximateNumberOfMessages']
    return int(messages_available)

def get_latest_message():
    """ Gets the first available message in queue """
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )    
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']
    s3_object_path = message['Body']
    return s3_object_path, receipt_handle

def delete_message(receipt_handle):
    """ Deletes the SQS message that matches the specified handle """
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

def process_image(s3_object_path):
    """ Retrieves image from s3, classifiess the image, and then writes the result to S3 """
    s = S3Url(s3_object_path)
    s3_resource.Object(s.bucket, s.key).download_file(f'/tmp/{s.key}')


#while get_num_messages_available() > 0:
    #print("Time to process an image")
