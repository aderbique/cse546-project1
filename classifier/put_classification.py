import boto3

dynamodb = boto3.resource('dynamodb',region_name='us-east-1',endpoint_url='https://dynamodb.us-east-1.amazonaws.com')

def put_classification(image_key,classification,s3_location):

  table = dynamodb.Table('Classifications')
  response = table.put_item(
     Item={
          'ImageName': image_key,
          'Classification': classification,
          'S3Location':s3_location
      }
  )
  return response
