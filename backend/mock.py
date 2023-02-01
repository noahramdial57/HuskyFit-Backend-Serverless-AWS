import json
# import os

def lambda_handler(event, context):

    meal = event['path'].split("/")[2] # ['', 'buckley', 'lunch']
    data = []

    # print(os.listdir(os.curdir))  #files and directories


    with open('mock_data_{}.json'.format(meal), 'r') as f:
        data = json.dumps(json.load(f))

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': data
    }

# event = {
#     "path": "/buckley/breakfast"
# }

# print(lambda_handler(event, 0)['body'])