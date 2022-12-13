import json

def lambda_handler(event, context):

    meal = event['path'].split("/")[2] # ['', 'buckley', 'lunch']
    data = []

    with open('mock_data_{}.json'.format(meal), 'r') as f:
        data = json.dumps(json.load(f))

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': data
    }

    