import json
import os
import requests

def get_quiz_data(api_endpoint):
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quiz data: {e}")
        return None

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
