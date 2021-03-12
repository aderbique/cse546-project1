import boto3
#Define AWS Region
aws_region='us-east-1'
#SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue'

sqs = boto3.client('sqs', region_name=aws_region)
s3 = boto3.resource('s3')
ec2 = boto3.client('ec2', region_name=aws_region)
dynamodb = boto3.client('dynamodb',region_name=aws_region,endpoint_url='https://dynamodb.us-east-1.amazonaws.com')

def delete_table(table_name):
    return dynamodb.delete_table(TableName=table_name)

def create_table(table_name):
    waiter = dynamodb.get_waiter('table_not_exists')
    waiter.wait(TableName=table_name)
    print("Creating Table {}".format(table_name))
    table = dynamodb.create_table(TableName=table_name,
        AttributeDefinitions= [
            {
                "AttributeName": "Classification",
                "AttributeType": "S"
            },
            {
                "AttributeName": "ImageName",
                "AttributeType": "S"
            }
        ],
        KeySchema=[
            {
                "KeyType": "HASH",
                "AttributeName": "ImageName"
            },
            {
                "KeyType": "RANGE",
                "AttributeName": "Classification"
            }
        ],
        ProvisionedThroughput= {
            "WriteCapacityUnits": 5,
            "ReadCapacityUnits": 5
        }
    )
#  waiter = dynamo

def reset():

  # Define and detele all objects in s3 input
  input_bucket = s3.Bucket("cse546-project1")
  input_bucket.objects.all().delete()

  # Purge Queue
  try:
    response = sqs.purge_queue(QueueUrl=queue_url)
  except:
    print("Resetting too quickly.")

  # Delete DynamoDB Table
  try:
    delete_table("Classifications")
  except:
    print("Table must be empty")

  # Create DynamoDB Table
  create_table("Classifications")

  output_bucket = s3.Bucket("cse546-project1-output")
  output_bucket.objects.all().delete()

