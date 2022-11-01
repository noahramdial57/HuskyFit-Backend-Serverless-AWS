import json


def hello(event, context):
    body = "Go Serverless v3.0! Your function executed successfully!"

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps(body)
    }
