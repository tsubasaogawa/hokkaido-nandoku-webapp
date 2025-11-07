import json
import os
import requests
from string import Template
from urllib.parse import parse_qs

def get_quiz_data(api_endpoint):
    # try:
    #     response = requests.get(api_endpoint)
    #     response.raise_for_status()
    #     return response.json()
    # except requests.exceptions.RequestException as e:
    #     print(f"Error fetching quiz data: {e}")
    #     return None
    return {
        "quiz": {
            "id": "1",
            "name": "札幌",
            "options": ["さっぽろ", "さつぽろ", "さぶろ", "さごろ"],
            "correct_answer": "さっぽろ"
        }
    }

def lambda_handler(event, context):
    api_endpoint = os.environ.get("NANDOKU_API_ENDPOINT")
    if not api_endpoint:
        return {'statusCode': 500, 'body': json.dumps({'error': 'NANDOKU_API_ENDPOINT is not set'})}

    method = event['requestContext']['http']['method']

    if method == 'GET':
        quiz_data = get_quiz_data(api_endpoint)
        if not quiz_data:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to fetch quiz data'})}

        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        html_content = template.substitute(quiz_data=json.dumps(quiz_data))
        return {'statusCode': 200, 'headers': {'Content-Type': 'text/html'}, 'body': html_content}

    elif method == 'POST':
        body = parse_qs(event['body'])
        user_answer = body.get('answer', [None])[0]
        quiz_id = body.get('quiz_id', [None])[0]

        quiz_data = get_quiz_data(api_endpoint)
        if not quiz_data:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to verify answer or invalid format'})}

        # Assuming quiz_data is directly the quiz object, not {'quiz': {...}}
        correct_answer = quiz_data['correct_answer']
        
        if user_answer == correct_answer:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'correct'})}
        else:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'incorrect', 'correct_answer': correct_answer})}

    return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed'})}
