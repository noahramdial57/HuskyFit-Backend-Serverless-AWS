import json
import boto3
from botocore.exceptions import ClientError
import botocore
import boto3
from botocore.exceptions import ClientError
import botocore
import json

def lambda_handler(event, context):
    
     # Warmup our function!
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
        
    parse = event['path'].split("/") # ['', 'buckley', 'lunch']
    dining_hall = parse[1].capitalize()
    meal = parse[2].capitalize()
    date = json.loads(event['body'])['Date'] 

    date_parse = date.split('/')
    mm = date_parse[0]
    dd = date_parse[1]
    yyyy = date_parse[2]
    
    bucket = "dininghall-data-cache"
    key = "{}-{}-{}-{}-{}.json".format(dining_hall, meal, mm, dd, yyyy)

    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read()
        

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': content
    }