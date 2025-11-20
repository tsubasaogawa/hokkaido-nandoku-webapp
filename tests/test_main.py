from fastapi.testclient import TestClient
from src.main import app, CITIES_DATA, bedrock_client
from src.bedrock_client import BedrockConnectionError
import pytest
from unittest.mock import patch, MagicMock
import random

client = TestClient(app)

@pytest.fixture
def mock_bedrock_client():
    """BedrockClientをモック化するフィクスチャ"""
    with patch('src.main.bedrock_client', autospec=True) as mock_client:
        yield mock_client

def test_read_root_success(mock_bedrock_client):
    """ルートエンドポイントが正常にHTMLを返すテスト"""
    mock_bedrock_client.generate_options.return_value = ["ダミー1", "ダミー2", "ダミー3"]
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']
    assert "北海道難読地名クイズ" in response.text

def test_get_quiz_success(mock_bedrock_client):
    """クイズエンドポイントが正常にクイズデータを返すテスト"""
    mock_bedrock_client.generate_options.return_value = ["ダミー1", "ダミー2", "ダミー3"]
    city_id = random.choice(list(CITIES_DATA.keys()))
    response = client.get(f"/quiz/{city_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == city_id
    assert data['name'] == CITIES_DATA[city_id]['name']
    assert data['correct_answer'] == CITIES_DATA[city_id]['yomi']
    assert len(data['options']) == 4
    assert CITIES_DATA[city_id]['yomi'] in data['options']
    mock_bedrock_client.generate_options.assert_called_once_with(CITIES_DATA[city_id]['name'])

def test_get_quiz_not_found(mock_bedrock_client):
    """存在しない都市IDの場合に404を返すテスト"""
    mock_bedrock_client.generate_options.return_value = ["ダミー1", "ダミー2", "ダミー3"]
    response = client.get("/quiz/nonexistent_city")
    assert response.status_code == 404
    assert response.json() == {"detail": "City not found"}

def test_get_quiz_bedrock_error_fallback(mock_bedrock_client):
    """Bedrockエラー時にフォールバックするテスト"""
    mock_bedrock_client.generate_options.side_effect = BedrockConnectionError("Bedrock connection failed")
    city_id = random.choice(list(CITIES_DATA.keys()))
    response = client.get(f"/quiz/{city_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == city_id
    assert data['name'] == CITIES_DATA[city_id]['name']
    assert data['correct_answer'] == CITIES_DATA[city_id]['yomi']
    assert len(data['options']) == 4
    assert CITIES_DATA[city_id]['yomi'] in data['options']
    assert "ダミー1" in data['options'] # フォールバックのダミー選択肢が含まれることを確認
    mock_bedrock_client.generate_options.assert_called_once_with(CITIES_DATA[city_id]['name'])

def test_check_answer_correct():
    """正解の場合のテスト"""
    city_id = random.choice(list(CITIES_DATA.keys()))
    correct_answer = CITIES_DATA[city_id]['yomi']
    response = client.post(
        "/answer",
        json={
            "quiz_id": city_id,
            "answer": correct_answer,
            "correct_answer": correct_answer
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": "correct", "correct_answer": None}

def test_check_answer_incorrect():
    """不正解の場合のテスト"""
    city_id = random.choice(list(CITIES_DATA.keys()))
    correct_answer = CITIES_DATA[city_id]['yomi']
    response = client.post(
        "/answer",
        json={
            "quiz_id": city_id,
            "answer": "間違った答え",
            "correct_answer": correct_answer
        }
    )
    assert response.status_code == 200
    assert response.json() == {"result": "incorrect", "correct_answer": correct_answer}