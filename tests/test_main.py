import pytest
import json
import os
import requests # 追加
from unittest.mock import patch, mock_open

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
    os.environ['NANDOKU_API_ENDPOINT'] = "https://test-api.example.com"
    yield
    del os.environ['NANDOKU_API_ENDPOINT']

# --- get_quiz_data関数のテスト ---

def test_get_quiz_data_success(set_api_endpoint, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"quiz": {"id": "1", "name": "札幌", "options": ["さっぽろ"], "correct_answer": "さっぽろ"}}
    mocker.patch('requests.get', return_value=mock_response)

    data = get_quiz_data(os.environ['NANDOKU_API_ENDPOINT'])
    assert data == {"quiz": {"id": "1", "name": "札幌", "options": ["さっぽろ"], "correct_answer": "さっぽろ"}}

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
    mock_quiz_data = {
        "quiz": {
            "id": "1",
            "name": "札幌",
            "options": ["さっぽろ", "さつぽろ", "さぶろ", "さごろ"],
            "correct_answer": "さっぽろ"
        }
    }
    mocker.patch('main.get_quiz_data', return_value=mock_quiz_data)

    mock_template_content = """
    <!DOCTYPE html>
    <html><body><h1>北海道難読地名クイズ</h1><div id="quiz-container"></div><script>const quizData = $quiz_data;</script></body></html>
    """
    mocker.patch('builtins.open', mock_open(read_data=mock_template_content))
    mocker.patch('os.path.exists', return_value=True)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'text/html'
    # HTMLボディ内のJavaScript変数quizDataが正しく設定されていることを確認
    expected_quiz_data_json = json.dumps(mock_quiz_data)
    assert f"const quizData = {expected_quiz_data_json};" in response['body']

def test_lambda_handler_get_api_fetch_failure(set_api_endpoint, base_event, mocker):
    mocker.patch('main.get_quiz_data', return_value=None)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "Failed to fetch quiz data" in response['body']

def test_lambda_handler_get_no_api_endpoint(base_event):
    if 'NANDOKU_API_ENDPOINT' in os.environ:
        del os.environ['NANDOKU_API_ENDPOINT']

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "NANDOKU_API_ENDPOINT is not set" in response['body']

def test_lambda_handler_post_correct_answer(set_api_endpoint, base_event, mocker):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    base_event['body'] = "quiz_id=1&answer=%E3%81%95%E3%81%A3%E3%81%BD%E3%82%8D" # さっぽろ

    mocker.patch('main.get_quiz_data', return_value={
        "id": "1",
        "name": "札幌",
        "options": ["さっぽろ", "さつぽろ", "さぶろ", "さごろ"],
        "correct_answer": "さっぽろ"
    })

    response = lambda_handler(base_event, None)
    response_body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert response_body['result'] == 'correct'

def test_lambda_handler_post_incorrect_answer(set_api_endpoint, base_event, mocker):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    base_event['body'] = "quiz_id=1&answer=%E3%81%95%E3%81%A4%E3%81%BD%E3%82%8D" # さつぽろ

    mocker.patch('main.get_quiz_data', return_value={
        "id": "1",
        "name": "札幌",
        "options": ["さっぽろ", "さつぽろ", "さぶろ", "さごろ"],
        "correct_answer": "さっぽろ"
    })

    response = lambda_handler(base_event, None)
    response_body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert response_body['result'] == 'incorrect'
    assert response_body['correct_answer'] == 'さっぽろ'

def test_lambda_handler_post_api_fetch_failure(set_api_endpoint, base_event, mocker):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    base_event['body'] = "quiz_id=1&answer=%E3%81%95%E3%81%A3%E3%81%BD%E3%82%8D"

    mocker.patch('main.get_quiz_data', return_value=None)

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "Failed to verify answer or invalid format" in response['body']

def test_lambda_handler_post_no_api_endpoint(base_event):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    base_event['body'] = "quiz_id=1&answer=%E3%81%95%E3%81%A3%E3%81%BD%E3%82%8D"

    if 'NANDOKU_API_ENDPOINT' in os.environ:
        del os.environ['NANDOKU_API_ENDPOINT']

    response = lambda_handler(base_event, None)

    assert response['statusCode'] == 500
    assert "NANDOKU_API_ENDPOINT is not set" in response['body']

def test_lambda_handler_post_missing_answer(set_api_endpoint, base_event, mocker):
    base_event['requestContext']['http']['method'] = 'POST'
    base_event['headers']['content-type'] = 'application/x-www-form-urlencoded'
    base_event['body'] = "quiz_id=1" # 回答が欠落

    mocker.patch('main.get_quiz_data', return_value={
        "id": "1",
        "name": "札幌",
        "options": ["さっぽろ"],
        "correct_answer": "さっぽろ"
    })

    response = lambda_handler(base_event, None)
    response_body = json.loads(response['body'])

    assert response['statusCode'] == 200 # 200を返す想定
    assert response_body['result'] == 'incorrect'
    assert response_body['correct_answer'] == 'さっぽろ'
