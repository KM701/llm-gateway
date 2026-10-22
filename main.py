import time
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LLM Gateway")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"


class ChatRequest(BaseModel):
    prompt: str


@app.post("/chat")
async def chat(req: ChatRequest):
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": req.prompt, "stream": False},
            )
            r.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {e}")

    data = r.json()
    latency_ms = round((time.perf_counter() - start) * 1000)
    return {"response": data["response"], "model": MODEL, "latency_ms": latency_ms}