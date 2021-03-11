import os
import boto3
from s3_url import S3Url
from image_classification import classify
import time
from datetime import datetime,timezone
import subprocess
import requests
import json
#Define AWS Region
aws_region='us-east-1'
#SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue'

try:
  run_cont =  os.environ['RUN_CONTINUOUSLY']
except:
  print("Did not find RUN_CONTINUOUSLY environment variable. Defaulting to False.")
  run_cont = False

try:
  shutdown_after = os.environ['SHUTDOWN_AFTER']
except:
  print("Did not find SHUTDOWN_AFTER environment variable. Defaulting to False.")
  shutdown_after = False

#Instantiate Clients
sqs = boto3.client('sqs', region_name=aws_region)
s3 = boto3.client('s3')
ec2 = boto3.client('ec2', region_name=aws_region)
dynamodb = boto3.resource('dynamodb',region_name=aws_region,endpoint_url='https://dynamodb.us-east-1.amazonaws.com')
#Obtain Instance ID of instance
r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = r.text

def get_num_messages_available():
    """ Returns the number of messages in the queue """
    response = sqs.get_queue_attributes(QueueUrl=queue_url,AttributeNames=['ApproximateNumberOfMessages'])
    messages_available = response['Attributes']['ApproximateNumberOfMessages']
    return int(messages_available)

def get_num_messages_visible():
    """ Returns the number of messages visible in the queue """
    response = sqs.get_queue_attributes(QueueUrl=queue_url,AttributeNames=['ApproximateNumberOfMessagesNotVisible'])
    messages_available = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
    return int(messages_available)

def get_latest_message():
    """ Gets the first available message in queue """
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    print(type(receipt_handle))
#    receipt_handle = message['ReceiptHandle']
    s3_object_path = json.loads(response['Messages'][0]['Body'])
    bucket = s3_object_path['Records'][0]['s3']['bucket']['name']
    key = s3_object_path['Records'][0]['s3']['object']['key']
    print("s3://{}/{}".format(bucket,key))
    #print(s3_object_path)
#    return s3_object_path, receipt_handle

print(get_latest_message())
