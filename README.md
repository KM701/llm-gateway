
# LLM Gateway

A backend gateway that sits between applications and LLMs, handling routing,
caching, rate limiting, and failure recovery in one place.

## Features
- [x] `/chat` endpoint forwarding to a local model (Ollama, Llama 3.2 1B)
- [ ] Streaming responses (SSE)
- [ ] Redis caching for repeated prompts
- [ ] API key auth and per-key rate limiting
- [ ] Multi-provider fallback with retries and timeouts
- [ ] Token and latency tracking
- [ ] Load testing results

## Tech stack
Python, FastAPI, httpx, Ollama (Redis, Postgres, Docker planned)

## Run locally
1. Install [Ollama](https://ollama.com) and run `ollama pull llama3.2:1b`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. Open http://localhost:8000/docs

## Results
_Benchmarks will be added as features are built._
