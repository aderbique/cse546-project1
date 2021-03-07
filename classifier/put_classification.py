import boto3


def put_classification(image_key,classification,s3_location):
  dynamodb = boto3.resource('dynamodb',endpoint_url='https://dynamodb.us-east-1.amazonaws.com')

  table = dynamodb.Table('Classifications')
  response = table.put_item(
     Item={
          'ImageName': image_key,
          'Classification': classification,
          'S3Location':s3_location
      }
  )
  return response
