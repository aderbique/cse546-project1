import boto3
import argparse
import csv

s3_bucket='cse546-project1'

results = {}

s3 = boto3.client('s3')

response = s3.list_objects_v2(
        Bucket=s3_bucket
)
print(response)

