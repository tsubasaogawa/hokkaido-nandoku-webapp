from fastapi.testclient import TestClient
from src.main import app
from src.bedrock_client import BedrockConnectionError
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os

client = TestClient(app)

@pytest.fixture(autouse=True)
def set_api_endpoint():
    """APIエンドポイントの環境変数を設定する"""
    os.environ['NANDOKU_API_ENDPOINT'] = "https://test-api.example.com"
    yield
    del os.environ['NANDOKU_API_ENDPOINT']

@pytest.fixture
def mock_bedrock_client():
    """BedrockClientをモック化するフィクスチャ"""
    with patch('src.main.bedrock_client', autospec=True) as mock_client:
        mock_client.generate_options.return_value = ["ダミー1", "ダミー2", "ダミー3"]
        yield mock_client

@pytest.fixture
def mock_httpx_client():
    """httpx.AsyncClientをモック化するフィクスチャ"""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
async def test_read_root_success(mock_bedrock_client, mock_httpx_client):
    """ルートエンドポイントが正常にHTMLを返すテスト"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"id": "sapporo", "name": "札幌", "yomi": "さっぽろ"})
    mock_httpx_client.get.return_value = mock_response
    
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']
    assert "北海道難読地名クイズ" in response.text
    mock_httpx_client.get.assert_called_once_with("https://test-api.example.com/random")

@pytest.mark.asyncio
async def test_get_quiz_success(mock_bedrock_client, mock_httpx_client):
    """クイズエンドポイントが正常にクイズデータを返すテスト"""
    city_id = "sapporo"
    city_data = {"id": city_id, "name": "札幌", "yomi": "さっぽろ"}
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=city_data)
    mock_httpx_client.get.return_value = mock_response

    response = client.get(f"/quiz/{city_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == city_id
    assert data['name'] == city_data['name']
    assert data['correct_answer'] == city_data['yomi']
    assert len(data['options']) == 4
    assert city_data['yomi'] in data['options']
    mock_bedrock_client.generate_options.assert_called_once_with(city_data['name'])
    mock_httpx_client.get.assert_called_once_with(f"https://test-api.example.com/{city_id}")

@pytest.mark.asyncio
async def test_get_quiz_api_not_found(mock_bedrock_client, mock_httpx_client):
    """APIが404を返す場合のテスト"""
    import httpx
    mock_httpx_client.get.side_effect = httpx.HTTPStatusError(
        "Not Found", request=httpx.Request("GET", "https://test-api.example.com/nonexistent_city"), response=httpx.Response(404, request=httpx.Request("GET", "https://test-api.example.com/nonexistent_city"))
    )
    
    response = client.get("/quiz/nonexistent_city")
    assert response.status_code == 404
    assert response.json() == {"detail": "City not found"}

@pytest.mark.asyncio
async def test_get_quiz_bedrock_error_fallback(mock_bedrock_client, mock_httpx_client):
    """Bedrockエラー時にフォールバックするテスト"""
    city_id = "sapporo"
    city_data = {"name": "札幌", "yomi": "さっぽろ"}
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=city_data)
    mock_httpx_client.get.return_value = mock_response
    
    mock_bedrock_client.generate_options.side_effect = BedrockConnectionError("Bedrock connection failed")
    
    response = client.get(f"/quiz/{city_id}")
    assert response.status_code == 200
    data = response.json()
    assert "ダミー1" in data['options']

def test_check_answer_correct():
    """正解の場合のテスト"""
    response = client.post(
        "/answer",
        json={"quiz_id": "sapporo", "answer": "さっぽろ", "correct_answer": "さっぽろ"}
    )
    assert response.status_code == 200
    assert response.json() == {"result": "correct", "correct_answer": None}

def test_check_answer_incorrect():
    """不正解の場合のテスト"""
    response = client.post(
        "/answer",
        json={"quiz_id": "sapporo", "answer": "まちがい", "correct_answer": "さっぽろ"}
    )
    assert response.status_code == 200
    assert response.json() == {"result": "incorrect", "correct_answer": "さっぽろ"}