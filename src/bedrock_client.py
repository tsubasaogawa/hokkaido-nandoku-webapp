import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import os
import json
import logging
import re

logger = logging.getLogger(__name__)

class BedrockConnectionError(Exception):
    """Custom exception for Bedrock connection errors."""
    pass

class BedrockClient:
    """
    A client for interacting with the Amazon Bedrock API.
    """
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
        選択肢は **ひらがな** のみ利用し、JSON形式で "options" というキーに、文字列の配列として3つの選択肢を入れてください。
        例:
        ```json
        {{
            "options": ["おしゃまんべ", "おさまんべ", "おしゃまべ"]
        }}
        ```
        """
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]

            response = self.client.converse(
                modelId=os.environ["BEDROCK_MODEL_ID"],
                messages=messages,
                inferenceConfig={
                    "maxTokens": 1000,
                }
            )

            response_body = response['output']['message']['content'][0]['text']
            logger.info(f"Raw Bedrock response body: {response_body}")

            # Extract JSON part from the response markdown
            json_match = re.search(r'```json\n(\{.*?\})\n```', response_body, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Fallback to finding the first JSON object if markdown is not present
                json_match = re.search(r'(\{.*?\})', response_body, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    logger.error("No JSON found in Bedrock response")
                    return []

            options_json = json.loads(json_str)
            
            return options_json.get("options", [])

        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise BedrockConnectionError from e
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse Bedrock response: {e}")
            raise BedrockConnectionError from e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise BedrockConnectionError from e

