import json
import os
import requests
import random
from string import Template
from urllib.parse import parse_qs
import base64

def get_quiz_data(api_endpoint):
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
        api_data = response.json()

        # APIレスポンスをアプリケーションの形式に変換
        correct_answer = api_data['yomi']
        options = [correct_answer, 'ダミー1', 'ダミー2', 'ダミー3']
        random.shuffle(options)

        return {
            "quiz": {
                "id": api_data['name'],
                "name": api_data['name'],
                "options": options,
                "correct_answer": correct_answer
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quiz data: {e}")
        return None

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
        
        html_content = template.safe_substitute(quiz_data=json.dumps(quiz_data))
        return {'statusCode': 200, 'headers': {'Content-Type': 'text/html'}, 'body': html_content}

    elif method == 'POST':
        # print(event) # デバッグ用にeventの内容を出力
        body_content = event['body']
        if event.get('isBase64Encoded', False):
            body_content = base64.b64decode(body_content).decode('utf-8')

        body = parse_qs(body_content)
        user_answer = body.get('answer', [None])[0]
        quiz_id = body.get('quiz_id', [None])[0]
        correct_answer_from_client = body.get('correct_answer', [None])[0]

        if not quiz_id or not user_answer or not correct_answer_from_client:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing quiz_id, answer, or correct_answer'})}

        if user_answer == correct_answer_from_client:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'correct'})}
        else:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'incorrect', 'correct_answer': correct_answer_from_client})}

    return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed'})}
