from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import os
import httpx
from mangum import Mangum
import boto3
import hashlib
import time
import logging

from bedrock_client import BedrockClient, BedrockConnectionError

app = FastAPI()
templates = Jinja2Templates(directory="templates")
bedrock_client = BedrockClient()

# DynamoDB Cache Setup
# AWS_REGION environment variable is usually available in Lambda
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "hokkaido-nandoku-quiz-cache")
table = dynamodb.Table(TABLE_NAME)

def get_cached_options(text: str) -> list[str] | None:
    """DynamoDBからキャッシュされた選択肢を取得する"""
    key = hashlib.sha256(text.encode('utf-8')).hexdigest()
    try:
        response = table.get_item(Key={'cache_key': key})
        if 'Item' in response:
            return response['Item']['options']
    except Exception as e:
        logging.error(f"DynamoDB get error: {e}")
    return None

def cache_options(text: str, options: list[str]):
    """生成された選択肢をDynamoDBにキャッシュする"""
    key = hashlib.sha256(text.encode('utf-8')).hexdigest()
    expires_at = int(time.time()) + (7 * 4 * 24 * 60 * 60) # 4 weeks
    try:
        table.put_item(Item={
            'cache_key': key,
            'options': options,
            'expires_at': expires_at
        })
    except Exception as e:
        logging.error(f"DynamoDB put error: {e}")

class QuizResponse(BaseModel):
    id: str
    name: str
    options: list[str]
    correct_answer: str

class AnswerResponse(BaseModel):
    result: str
    correct_answer: str | None = None

async def fetch_random_city_data() -> dict:
    """APIからランダムな都市データを取得する"""
    api_endpoint = os.environ.get("NANDOKU_API_ENDPOINT")
    if not api_endpoint:
        raise HTTPException(status_code=500, detail="NANDOKU_API_ENDPOINT is not set")

    url = f"{api_endpoint}/random"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logging.error(f"API request failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch quiz data from external API.")

async def get_quiz_data(city_info: dict) -> dict:
    """都市情報からクイズデータを生成する"""
    correct_answer = city_info["yomi"] # 正解は「よみ」
    city_id = city_info.get("id")
    city_name = city_info["name"]

    cached_options = get_cached_options(city_name)
    if cached_options:
        incorrect_options = cached_options
    else:
        try:
            # Bedrockには「漢字」を渡して選択肢を生成させる
            incorrect_options = bedrock_client.generate_options(city_name)
            cache_options(city_name, incorrect_options)
        except BedrockConnectionError as e:
            logging.error(f"Bedrock connection error: {e}")
            incorrect_options = ["ダミー1", "ダミー2", "ダミー3"]

    options = [correct_answer] + incorrect_options
    random.shuffle(options) # 選択肢をシャッフル

    return {
        "id": city_id,
        "name": city_name, # 問題文は「漢字」
        "options": options,
        "correct_answer": correct_answer,
    }

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """ルートページ。ランダムなクイズを表示する"""
    try:
        city_info = await fetch_random_city_data()
        quiz_data = await get_quiz_data(city_info)
    except HTTPException as e:
        # エラーページをレンダリングするか、単純なエラーメッセージを返す
        return HTMLResponse(content=f"<h1>エラーが発生しました</h1><p>{e.detail}</p>", status_code=e.status_code)

    return templates.TemplateResponse("index.html", {"request": request, "quiz": quiz_data})


@app.post("/", response_class=JSONResponse)
async def check_answer(correct_answer: str = Form(...), answer: str = Form(...)):
    """
    ユーザーの回答をチェックし、正解/不正解と正解の選択肢を返す。
    """
    is_correct = (answer == correct_answer)
    return {
        "result": "correct" if is_correct else "incorrect",
        "correct_answer": correct_answer
    }

lambda_handler = Mangum(app)
