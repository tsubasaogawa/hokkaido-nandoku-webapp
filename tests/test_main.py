from fastapi.testclient import TestClient
from src.main import app
from src.bedrock_client import BedrockConnectionError
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import time

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
def mock_dynamodb_table():
    """DynamoDB Tableをモック化するフィクスチャ"""
    with patch('src.main.table') as mock_table:
        yield mock_table

@pytest.fixture
def mock_httpx_client():
    """httpx.AsyncClientをモック化するフィクスチャ"""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
async def test_read_root_cache_miss(mock_bedrock_client, mock_httpx_client, mock_dynamodb_table):
    """キャッシュミス時の動作テスト: Bedrockが呼ばれ、キャッシュに保存される"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"id": "sapporo", "name": "札幌", "yomi": "さっぽろ"})
    mock_httpx_client.get.return_value = mock_response
    
    # キャッシュミスをシミュレート
    mock_dynamodb_table.get_item.return_value = {}

    response = client.get("/")
    
    assert response.status_code == 200
    
    # Bedrockが呼ばれたことを確認
    mock_bedrock_client.generate_options.assert_called_once_with("札幌")
    
    # キャッシュに保存されたことを確認
    mock_dynamodb_table.put_item.assert_called_once()
    args, kwargs = mock_dynamodb_table.put_item.call_args
    item = kwargs['Item']
    assert item['cache_key'] is not None
    assert item['options'] == ["ダミー1", "ダミー2", "ダミー3"]
    assert item['expires_at'] > time.time()

@pytest.mark.asyncio
async def test_read_root_cache_hit(mock_bedrock_client, mock_httpx_client, mock_dynamodb_table):
    """キャッシュヒット時の動作テスト: Bedrockが呼ばれず、キャッシュから値が返される"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"id": "sapporo", "name": "札幌", "yomi": "さっぽろ"})
    mock_httpx_client.get.return_value = mock_response
    
    # キャッシュヒットをシミュレート（ASCII文字列を使用してエスケープ問題を回避）
    cached_options = ["CacheOption1", "CacheOption2", "CacheOption3"]
    mock_dynamodb_table.get_item.return_value = {'Item': {'options': cached_options}}

    response = client.get("/")
    
    assert response.status_code == 200
    
    # Bedrockが呼ばれていないことを確認
    mock_bedrock_client.generate_options.assert_not_called()
    
    # PutItemも呼ばれていないことを確認
    mock_dynamodb_table.put_item.assert_not_called()
    
    # レスポンスにキャッシュされたオプションが含まれているか確認
    response_text = response.text
    assert "CacheOption1" in response_text

@pytest.mark.asyncio
async def test_check_answer_correct():
    """正解の場合のテスト"""
    response = client.post(
        "/",
        data={"correct_answer": "さっぽろ", "answer": "さっぽろ"}
    )
    assert response.status_code == 200
    assert response.json() == {"result": "correct", "correct_answer": "さっぽろ"}

@pytest.mark.asyncio
async def test_check_answer_incorrect():
    """不正解の場合のテスト"""
    response = client.post(
        "/",
        data={"correct_answer": "さっぽろ", "answer": "まちがい"}
    )
    assert response.status_code == 200
    assert response.json() == {"result": "incorrect", "correct_answer": "さっぽろ"}