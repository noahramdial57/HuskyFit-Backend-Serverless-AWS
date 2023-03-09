import json

def lambda_handler(event, context):

    with open('mock_data_lunch.json', 'r') as f:
        data = json.dumps(json.load(f))

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': data
    }
