import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from src.bedrock_client import BedrockClient, BedrockConnectionError
import json

def test_generate_options_success():
    """Bedrock APIが正常に選択肢を返す場合のテスト"""
    client = BedrockClient()
    mock_bedrock_runtime = MagicMock()
    client.client = mock_bedrock_runtime

    expected_options = ["選択肢A", "選択肢B", "選択肢C"]
    mock_response_body = {
        "content": [
            {
                "text": json.dumps({"options": expected_options})
            }
        ]
    }
    mock_response = {
        'body': MagicMock(read=lambda: json.dumps(mock_response_body).encode('utf-8'))
    }

    mock_bedrock_runtime.invoke_model.return_value = mock_response

    city_name = "札幌"
    options = client.generate_options(city_name)

    assert options == expected_options
    mock_bedrock_runtime.invoke_model.assert_called_once()

def test_generate_options_client_error():
    """Bedrock APIがClientErrorを返す場合のテスト"""
    client = BedrockClient()
    mock_bedrock_runtime = MagicMock()
    client.client = mock_bedrock_runtime

    mock_bedrock_runtime.invoke_model.side_effect = ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}, 'InvokeModel')

    city_name = "札幌"
    with pytest.raises(BedrockConnectionError):
        client.generate_options(city_name)

def test_generate_options_json_decode_error():
    """Bedrock APIのレスポンスが不正なJSONの場合のテスト"""
    client = BedrockClient()
    mock_bedrock_runtime = MagicMock()
    client.client = mock_bedrock_runtime

    mock_response = {
        'body': MagicMock(read=lambda: b"invalid json")
    }

    mock_bedrock_runtime.invoke_model.return_value = mock_response

    city_name = "札幌"
    with pytest.raises(BedrockConnectionError):
        client.generate_options(city_name)

def test_generate_options_key_error():
    """Bedrock APIのレスポンスに'options'キーがない場合のテスト"""
    client = BedrockClient()
    mock_bedrock_runtime = MagicMock()
    client.client = mock_bedrock_runtime

    mock_response_body = {
        "content": [
            {
                "text": json.dumps({"wrong_key": ["選択肢A", "選択肢B", "選択肢C"]})
            }
        ]
    }
    mock_response = {
        'body': MagicMock(read=lambda: json.dumps(mock_response_body).encode('utf-8'))
    }

    mock_bedrock_runtime.invoke_model.return_value = mock_response

    city_name = "札幌"
    # This should return an empty list, not raise an error.
    options = client.generate_options(city_name)
    assert options == []
