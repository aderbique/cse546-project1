import os
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.dynamodb.conditions import Key
import get_classifications
from natsort import natsorted



app = Flask(__name__)
#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_PATH'] = 'uploads'
app.config["S3_LOCATION"] = 's3://{}/'.format('cse546-project1')

sqs = boto3.client('sqs', region_name='us-east-1')

queue_url = 'https://sqs.us-east-1.amazonaws.com/170322465562/queue.fifo'

def upload_file_to_s3(file, bucket_name):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """

    s3 = boto3.client("s3")

    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(app.config["S3_LOCATION"], file.filename)


def get_output_from_dynamo():
    print("Getting items in DynamoDB Table...")
    results = get_classifications.get_classifications_dict()
    results_sorted = get_classifications.natsort_dict(results)
    return results_sorted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    for uploaded_file in request.files.getlist('file'):
        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                uploaded = upload_file_to_s3(uploaded_file, 'cse546-project1')

                # Get the queue. This returns an SQS.Queue instance
                sqs.send_message(QueueUrl=queue_url,MessageBody=uploaded, MessageGroupId='messageGroup1')
    return redirect(url_for('index'))
    
@app.route('/results', methods=['POST'])
def get_results():
    results = get_output_from_dynamo()
    print("Finished")
    return render_template('results.html', results=results)

app.run(
    host=os.getenv('LISTEN', '0.0.0.0'),
    port=int(os.getenv('PORT', '8080'))
)
