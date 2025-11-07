import json
import os
import requests
import random
from string import Template
from urllib.parse import parse_qs

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
                "id": api_data['name'], # IDとして地名を使用
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
        body = parse_qs(event['body'])
        user_answer = body.get('answer', [None])[0]
        quiz_id = body.get('quiz_id', [None])[0] # quiz_idは地名

        # POSTリクエストではAPIを再度叩かず、正しい答えをどこかから取得する必要がある
        # ここでは簡単のため、再度APIを叩いて答えを取得する（非効率）
        quiz_data = get_quiz_data(api_endpoint)
        if not quiz_data:
            return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to verify answer or invalid format'})}

        correct_answer = quiz_data['quiz']['correct_answer']
        
        if user_answer == correct_answer:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'correct'})}
        else:
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'result': 'incorrect', 'correct_answer': correct_answer})}

    return {'statusCode': 405, 'body': json.dumps({'error': 'Method Not Allowed'})}
