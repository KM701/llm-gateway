import time
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from fastapi.responses import StreamingResponse

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

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        start = time.perf_counter()
        first_token = True
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    OLLAMA_URL,
                    json={"model": MODEL, "prompt": req.prompt, "stream": True},
                ) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        if first_token:
                            ttft = round((time.perf_counter() - start) * 1000)
                            yield f"data: {json.dumps({'ttft_ms': ttft})}\n\n"
                            first_token = False
                        yield f"data: {json.dumps({'token': chunk.get('response', '')})}\n\n"
                        if chunk.get("done"):
                            total = round((time.perf_counter() - start) * 1000)
                            yield f"data: {json.dumps({'done': True, 'total_ms': total})}\n\n"
                            break
        except httpx.HTTPError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")