import os
import boto3
from s3_url import S3Url
from image_classification import classify
import time
from datetime import datetime,timezone
import subprocess
import requests

#Define AWS Region
aws_region='us-east-1'
#SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue.fifo'



#Instantiate Clients
sqs = boto3.client('sqs', region_name=aws_region)
s3 = boto3.client('s3')
ec2 = boto3.client('ec2', region_name=aws_region)

#Obtain Instance ID of instance
r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = r.text

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
    # Parse the path
    s = S3Url(s3_object_path)
    # Download the object to /tmp
    s3.download_file(s.bucket, s.key, f'/tmp/{s.key}')

    #Run classificaiton on image
    result = classify(f'/tmp/{s.key}')

    # Delete file
    os.remove(f'/tmp/{s.key}')

    #Write result as tag to original file

    put_tags_response = s3.put_object_tagging(
        Bucket=s.bucket,
        Key=s.key,    
        Tagging={
            'TagSet': [
                {
                    'Key': 'Image',
                    'Value': s.key
                },
                {
                    'Key': 'Classification',
                    'Value': result
                },
                {
                    'Key': 'ClassifiedBy',
                    'Value': instance_id
                },
                {
                    'Key': 'ClassifiedOn',
                    'Value': datetime.now(timezone.utc)
                }                               
            ]
        }
    )

while get_num_messages_available() > 0:
    print("Retrieving Image Link from SQS")
    s3_object_path, receipt_handle = get_latest_message()
    process_image(s3_object_path)
    delete_message(receipt_handle)
    print("Successfully Processed {}".format(s3_object_path))
    time.sleep(1)

print("Job Complete. Shutting Down")
ec2.stop_instances(InstanceIds=[instance_id])