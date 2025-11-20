from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import json
from string import Template
import os
import httpx

from .bedrock_client import BedrockClient, BedrockConnectionError

app = FastAPI()

bedrock_client = BedrockClient()

class QuizResponse(BaseModel):
    id: str
    name: str
    options: list[str]
    correct_answer: str

class AnswerRequest(BaseModel):
    answer: str
    quiz_id: str
    correct_answer: str

class AnswerResponse(BaseModel):
    result: str
    correct_answer: str | None = None

async def fetch_city_data(city_id: str) -> dict:
    """APIから都市データを取得する"""
    api_endpoint = os.environ.get("NANDOKU_API_ENDPOINT")
    if not api_endpoint:
        raise HTTPException(status_code=500, detail="NANDOKU_API_ENDPOINT is not set")

    url = f"{api_endpoint}/{city_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="City not found") from e
            else:
                raise HTTPException(status_code=500, detail="API request failed") from e
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="API request failed") from e

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """ルートページ。ランダムなクイズを表示する"""
    city_info = await fetch_city_data("random")
    quiz_data = await get_quiz_data(city_info)

    with open('templates/index.html', 'r', encoding='utf-8') as f:
        template = Template(f.read())
    
    html_content = template.safe_substitute(quiz_data=json.dumps(quiz_data))
    return HTMLResponse(content=html_content)

@app.get("/quiz/{city_id}", response_model=QuizResponse)
async def get_quiz(city_id: str):
    """指定されたIDのクイズを取得する"""
    city_info = await fetch_city_data(city_id)
    return await get_quiz_data(city_info)

async def get_quiz_data(city_info: dict) -> dict:
    """都市情報からクイズデータを生成する"""
    correct_answer = city_info["yomi"]
    city_id = city_info.get("id", city_info.get("name")) # APIがIDを返すことを想定

    try:
        incorrect_options = bedrock_client.generate_options(city_info["name"])
    except BedrockConnectionError:
        # フォールバック処理
        incorrect_options = ["ダミー1", "ダミー2", "ダミー3"]

    options = [correct_answer] + incorrect_options
    random.shuffle(options)

    return {
        "id": city_id,
        "name": city_info["name"],
        "options": options,
        "correct_answer": correct_answer,
    }

@app.post("/answer", response_model=AnswerResponse)
async def check_answer(request: AnswerRequest):
    if request.answer == request.correct_answer:
        return {"result": "correct", "correct_answer": None}
    else:
        return {"result": "incorrect", "correct_answer": request.correct_answer}