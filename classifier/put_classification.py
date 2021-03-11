import boto3


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
