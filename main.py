import json
import os

def lambda_handler(event, context):
    api_endpoint = os.environ.get("NANDOKU_API_ENDPOINT")
    if not api_endpoint:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'NANDOKU_API_ENDPOINT is not set'})
        }

    # TODO: Implement GET and POST handling
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
