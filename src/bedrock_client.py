import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import os
import json
import logging

logger = logging.getLogger(__name__)

class BedrockConnectionError(Exception):
    """Custom exception for Bedrock connection errors."""
    pass

class BedrockClient:
    """
    A client for interacting with the Amazon Bedrock API.
    """
    MODEL_ID = "anthropic.claude-haiku-4-5-20251001-v1:0"

    def __init__(self):
        """
        Initializes the Bedrock client.
        """
        retry_config = Config(
            connect_timeout=10,
            read_timeout=30,
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
        
        region_name = os.environ.get("AWS_DEFAULT_REGION", "ap-northeast-1")

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
            config=retry_config
        )

    def generate_options(self, city_name: str) -> list[str]:
        """
        Generates three incorrect options for a quiz question about a given city.

        :param city_name: The correct city name.
        :return: A list of three incorrect city names.
        """
        prompt = f"""
        日本の北海道の地名「{city_name}」の読み方クイズを作成しています。
        正解の選択肢「{city_name}」と非常によく似ていて、間違いやすい選択肢を3つだけ挙げてください。
        JSON形式で、"options"というキーに、文字列の配列として3つの選択肢を入れてください。
        例:
        {{
            "options": ["おしゃまんべ", "おさまんべ", "おしゃまべ"]
        }}
        """
        
        try:
            response = self.client.invoke_model(
                modelId=self.MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            content_string = response_body['content'][0]['text']
            options_json = json.loads(content_string)
            
            return options_json.get("options", [])

        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise BedrockConnectionError from e
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Bedrock response: {e}")
            raise BedrockConnectionError from e
