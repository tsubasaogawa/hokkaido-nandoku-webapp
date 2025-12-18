from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random
import os
import httpx
from mangum import Mangum

from bedrock_client import BedrockClient, BedrockConnectionError
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")
bedrock_client = BedrockClient()

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
    correct_answer = city_info["name"] # APIの 'name' が正解の読み方と想定
    city_id = city_info.get("id")

    try:
        incorrect_options = bedrock_client.generate_options(city_info["name"])
    except BedrockConnectionError as e:
        logging.error(f"Bedrock connection error: {e}")
        incorrect_options = ["ダミー1", "ダミー2", "ダミー3"]

    options = [correct_answer] + incorrect_options
    # random.shuffle(options) # 正解が常に最初に来るように一旦コメントアウト

    return {
        "id": city_id,
        "name": city_info["name"],
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