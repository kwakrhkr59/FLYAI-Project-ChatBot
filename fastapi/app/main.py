from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from openai import AzureOpenAI

app = FastAPI()

azure_oai_endpoint = "YOUR_URL" # 대상 URL
azure_oai_key = "YOUR_AZURE_OPENAI_KEY" # 인증키1

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AzureOpenAI(
        azure_endpoint = azure_oai_endpoint, 
        api_key=azure_oai_key,  
        api_version="YOUR_API_VERSION"
)
class RequestModel(BaseModel):
    model: str
    prompt: str

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: Message):
    prompt = message.message
    # 요청할 URL
    url = "http://host.docker.internal:11434/api/generate"
    # 요청에 포함할 데이터
    data = {
        "model": "llama3.2-kbo-v1.0:latest",
        "prompt": prompt
    }
    # 요청 헤더
    headers = {
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # 개별 JSON 객체로 분할
        json_objects = response.content.decode().strip().split("\n")
        # 각 JSON 객체를 Python 사전으로 변환
        data = [json.loads(obj) for obj in json_objects]
        res_text = ''
        # 변환된 데이터 출력
        for item in data:
            print(item)
            res_text += item['response']
    else:
        res_text = f"Error Code : {response.status_code}"
    return {"reply": res_text}

@app.post("/openai")
async def chat(message: Message):
    prompt = message.message
    response = client.chat.completions.create(
        model="o1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    generated_text = response.choices[0].message.content
    return {"reply": generated_text}