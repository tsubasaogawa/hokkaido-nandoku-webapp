import pytest
import json
import os
import requests # 追加
from unittest.mock import patch, mock_open
from urllib.parse import urlencode

# テスト対象のモジュールをインポート
from main import lambda_handler, get_quiz_data # main.pyのパスを修正

# Lambdaハンドラに渡されるイベントの基本構造
@pytest.fixture
def base_event():
    return {
        'requestContext': {
            'http': {
                'method': 'GET' # デフォルトはGET
            }
        },
        'headers': {
            'content-type': 'application/json'
        },
        'body': None
    }

# 環境変数NANDOKU_API_ENDPOINTを設定するフィクスチャ
@pytest.fixture
def set_api_endpoint():
    os.environ['NANDOKU_API_ENDPOINT'] = "https://test-api.example.com/random"
    yield
    del os.environ['NANDOKU_API_ENDPOINT']

# --- get_quiz_data関数のテスト ---

def test_get_quiz_data_success(set_api_endpoint, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "札幌", "yomi": "さっぽろ"} # APIの実際のレスポンス形式に合わせる
    mocker.patch('requests.get', return_value=mock_response)

    data = get_quiz_data(os.environ['NANDOKU_API_ENDPOINT'])
    assert data['quiz']['name'] == "札幌"
    assert data['quiz']['correct_answer'] == "さっぽろ"
    assert "さっぽろ" in data['quiz']['options']

def test_get_quiz_data_failure(set_api_endpoint, mocker):
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network error"))

    data = get_quiz_data(os.environ['NANDOKU_API_ENDPOINT'])
    assert data is None

def test_get_quiz_data_http_error(set_api_endpoint, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mocker.patch('requests.get', return_value=mock_response)

    data = get_quiz_data(os.environ['NANDOKU_API_ENDPOINT'])
    assert data is None

# --- lambda_handler関数のテスト ---

def test_lambda_handler_get_success(set_api_endpoint, base_event, mocker):
    mock_api_data = {"name": "札幌", "yomi": "さっぽろ"}
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: mock_api_data))

    mock_template_content = """
    <!DOCTYPE html>
    <html><body><h1>北海道難読地名クイズ</h1><div id="quiz-container"></div><script>const quizData = ${quiz_data};</script></body></html>
    """
    mocker.patch('builtins.open', mock_open(read_data=mock_template_content))
    mocker.patch('os.path.exists', return_value=True)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/html'
    # HTMLボディ内のJavaScript変数quizDataが正しく設定されていることを確認
    # get_quiz_dataの変換ロジックを考慮した期待値
    # optionsはランダムなので、含まれる要素を検証する
    response_body_json = json.loads(response['body'].split('const quizData = ')[1].split(';</script>')[0])
    assert response_body_json['quiz']['id'] == mock_api_data['name']
    assert response_body_json['quiz']['name'] == mock_api_data['name']
    assert response_body_json['quiz']['correct_answer'] == mock_api_data['yomi']
    assert mock_api_data['yomi'] in response_body_json['quiz']['options']
    assert len(response_body_json['quiz']['options']) == 4

def test_lambda_handler_get_api_fetch_failure(set_api_endpoint, base_event, mocker):
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network error"))

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "Failed to fetch quiz data" in response['body']

def test_lambda_handler_get_no_api_endpoint(base_event):
    if 'NANDOKU_API_ENDPOINT' in os.environ:
        del os.environ['NANDOKU_API_ENDPOINT']

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "NANDOKU_API_ENDPOINT is not set" in response['body']

def test_lambda_handler_post_correct_answer(set_api_endpoint, base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    # correct_answerをbodyに含める
    body_data = {
        "quiz_id": "札幌",
        "answer": "さっぽろ",
        "correct_answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    response = lambda_handler(base_event, None)
    response_body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert response_body['result'] == 'correct'

def test_lambda_handler_post_incorrect_answer(set_api_endpoint, base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    # correct_answerをbodyに含める
    body_data = {
        "quiz_id": "札幌",
        "answer": "さつぽろ", # 不正解
        "correct_answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    response = lambda_handler(base_event, None)
    response_body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert response_body['result'] == 'incorrect'
    assert response_body['correct_answer'] == 'さっぽろ'

def test_lambda_handler_post_missing_answer(set_api_endpoint, base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    # 回答が欠落
    body_data = {
        "quiz_id": "札幌",
        "correct_answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 400
    assert "Missing quiz_id, answer, or correct_answer" in response['body']

def test_lambda_handler_post_missing_quiz_id(set_api_endpoint, base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    # quiz_idが欠落
    body_data = {
        "answer": "さっぽろ",
        "correct_answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 400
    assert "Missing quiz_id, answer, or correct_answer" in response['body']

def test_lambda_handler_post_missing_correct_answer(set_api_endpoint, base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    # correct_answerが欠落
    body_data = {
        "quiz_id": "札幌",
        "answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 400
    assert "Missing quiz_id, answer, or correct_answer" in response['body']

def test_lambda_handler_post_no_api_endpoint(base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    body_data = {
        "quiz_id": "札幌",
        "answer": "さっぽろ",
        "correct_answer": "さっぽろ"
    }
    base_event['body'] = urlencode(body_data)

    if 'NANDOKU_API_ENDPOINT' in os.environ:
        del os.environ['NANDOKU_API_ENDPOINT']

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "NANDOKU_API_ENDPOINT is not set" in response['body']
