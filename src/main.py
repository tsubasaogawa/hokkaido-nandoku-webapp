from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import json
from string import Template

from .bedrock_client import BedrockClient, BedrockConnectionError

app = FastAPI()

# ダミーのクイズデータ。将来的にはデータベースなどから取得する。
CITIES_DATA = {
    "sapporo": {"name": "札幌", "yomi": "さっぽろ"},
    "hakodate": {"name": "函館", "yomi": "はこだて"},
    "otaru": {"name": "小樽", "yomi": "おたる"},
    "asahikawa": {"name": "旭川", "yomi": "あさひかわ"},
    "muroran": {"name": "室蘭", "yomi": "むろらん"},
    "kushiro": {"name": "釧路", "yomi": "くしろ"},
    "obihiro": {"name": "帯広", "yomi": "おびひろ"},
    "kitami": {"name": "北見", "yomi": "きたみ"},
    "yubari": {"name": "夕張", "yomi": "ゆうばり"},
    "iwamizawa": {"name": "岩見沢", "yomi": "いわみざわ"},
}

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


@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 最初のクイズの問題をランダムに選ぶ
    random_city_id = random.choice(list(CITIES_DATA.keys()))
    quiz_data = get_quiz_data(random_city_id)

    with open('templates/index.html', 'r', encoding='utf-8') as f:
        template = Template(f.read())
    
    html_content = template.safe_substitute(quiz_data=json.dumps(quiz_data))
    return HTMLResponse(content=html_content)


@app.get("/quiz/{city_id}", response_model=QuizResponse)
async def get_quiz(city_id: str):
    return get_quiz_data(city_id)

def get_quiz_data(city_id: str) -> dict:
    if city_id not in CITIES_DATA:
        raise HTTPException(status_code=404, detail="City not found")

    city_info = CITIES_DATA[city_id]
    correct_answer = city_info["yomi"]

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
        return {"result": "correct"}
    else:
        return {"result": "incorrect", "correct_answer": request.correct_answer}