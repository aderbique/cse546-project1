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

results_s3 = "cse546-project1-output"

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
    
    """ 
    print(json.loads(response['Messages'][0]['Body']))
    bucket = json.loads(response['Messages'][0]['Body'])['Records'][0]['s3']['bucket']['name']
    key = json.loads(response['Messages'][0]['Body'])['Records'][0]['s3']['object']['key']
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    s3_object_path = 's3://{}/{}'.format(bucket,key)
    return s3_object_path, receipt_handle
    """
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    s3_object_path = json.loads(response['Messages'][0]['Body'])
    bucket = s3_object_path['Records'][0]['s3']['bucket']['name']
    key = s3_object_path['Records'][0]['s3']['object']['key']
    s3_object_path = "s3://{}/{}".format(bucket,key)
    return s3_object_path, receipt_handle

def delete_message(receipt_handle):
    """ Deletes the SQS message that matches the specified handle """
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

def put_classification(image_key,classification,s3_location):

  table = dynamodb.Table('Classifications')
  response = table.put_item(
     Item={
          'ImageName': image_key,
          'Classification': classification,
          'S3Location':s3_location
      }
  )

  # Forced to put this in due to assignment requirements :( Dynamo or object tagging is far superior
  response = s3.put_object(
              Bucket=results_s3,
                  Key="{}_{}".format(image_key,classification).replace(" ", "_")
                  )
  return response

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
                    'Value': str(datetime.now(timezone.utc))
                }                               
            ]
        }
    )
    # Add to table entries
    put_classification(s.key,result,s3_object_path)


def run_job():
  while get_num_messages_available() > 0:
      try:
        print("Retrieving Image Link from SQS")
        s3_object_path, receipt_handle = get_latest_message()
        process_image(s3_object_path)
        delete_message(receipt_handle)
        print("Successfully Processed {}".format(s3_object_path))
        #time.sleep(1)
      except:
        print("No more messages available")
        time.sleep(2)

if run_cont: #Run forever
    while True:
        run_job()
        time.sleep(5) #poll every 5 seconds
else:
  run_job() #run once

if shutdown_after:
    print("Job Complete. Shutting Down")
    #ec2.stop_instances(InstanceIds=[instance_id])
else:
    print("Job Comlete. Quitting...")
