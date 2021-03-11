import boto3
from natsort import natsorted


aws_region='us-east-1'

dynamodb = boto3.resource('dynamodb',region_name=aws_region,endpoint_url='https://dynamodb.us-east-1.amazonaws.com')


def get_classifications_dict():
  """ Returns a dictionary of images to classifications retrieved from DynamoDB """
  classifications = {}
  table = dynamodb.Table('Classifications')
  response = table.scan()
  for item in response['Items']:
    classifications[item['ImageName']] = item['Classification']
  return classifications.items()


def natsort_dict(dict):
  result = {}
  for key, value in natsorted(dict): # Note the () after items!
    result[key] = value
  return result

