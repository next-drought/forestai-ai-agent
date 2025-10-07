## AgentGoogle Backend Tech Brief

### What was broken
- Uvicorn failed to import the app due to package-relative imports when the container only copied this app directory.
- Container images previously copied the entire monorepo, unintentionally loading heavy `geoai` deps during startup.
- ADK decorators (`@agent`, `@tool`) depended on import paths not available as previously used. We removed that dependency and used a minimal Litellm function-calling flow instead.

### Key fixes applied
- Imports
  - `server.py`: use top-level import `from agent import GeoAgent`.
  - `agent.py`: import local tools via `from tools import MapTools`.
- Backend logic
  - Removed ADK decorators; implemented Litellm tool-calling with a minimal tool spec list and JSON arg parsing.
  - Supported `api_base` by reading `OLLAMA_HOST` so Ollama-based models work.
- Docker isolation
  - Dockerfile now copies only `geoai/agents/agentgoogle/` into `/app`.
  - Runs `uvicorn server:app` so imports resolve relative to `/app`.
- Dependencies
  - Trimmed `requirements.txt` to minimal deps needed by this service.

### Files changed
- `agent.py`: removed ADK decorators, added Litellm tool-calling and tool specs, JSON arg parsing, `API_BASE` support via `OLLAMA_HOST`.
- `server.py`: `from agent import GeoAgent` (top-level import) for container startup.
- `requirements.txt`: minimal runtime deps.
- `Dockerfile`: isolated build (copy only this app), run `uvicorn server:app`.

### Result
- Container starts and responds. Example:

```bash
curl -sS -X POST http://localhost:8082/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"zoom to level 5"}'
# => {"action":"zoom_to","payload":{"zoom":"5"}}
```

---

## How to build a similar backend service (using agentgoogle as an example)

### Minimal structure
- `agent.py`: Litellm function-calling logic
- `tools.py`: plain Python functions implementing actions
- `server.py`: FastAPI app exposing `/chat`
- `requirements.txt`: minimal runtime deps
- `Dockerfile`: copy only this directory; run `uvicorn server:app`

### agent.py (skeleton)
```python
import os, json
from typing import Dict, Any, List
from litellm import completion
import tools

MODEL_NAME = os.environ.get("GEOAI_MODEL", "ollama/llama3.1")
API_BASE = os.environ.get("OLLAMA_HOST")

class MyAgent:
    def __init__(self) -> None:
        self.tools = {"do_something": tools.do_something}
        self.tool_specs: List[Dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "do_something",
                    "description": "Does something minimal.",
                    "parameters": {
                        "type": "object",
                        "properties": {"param": {"type": "string"}},
                        "required": ["param"],
                    },
                },
            }
        ]

    def ask(self, query: str, history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
        sys_prompt = "Translate user requests into a single, minimal tool call."
        messages = [{"role": "system", "content": sys_prompt}, *history, {"role": "user", "content": query}]
        kwargs: Dict[str, Any] = {}
        if API_BASE:
            kwargs["api_base"] = API_BASE

        resp = completion(model=MODEL_NAME, messages=messages, tools=self.tool_specs, **kwargs)
        message = resp.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)
        if not tool_calls:
            return {"action": "chat_response", "payload": {"message": message.content}}

        call = tool_calls[0]
        name = call.function.name
        args = json.loads(call.function.arguments or "{}")
        if name in self.tools:
            return self.tools[name](**args)
        return {"action": "error", "payload": {"message": f"Tool '{name}' not found."}}
```

### tools.py (example)
```python
from typing import Dict, Any

def do_something(param: str) -> Dict[str, Any]:
    return {"action": "did_something", "payload": {"param": param}}
```

### server.py (FastAPI)
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from agent import MyAgent

app = FastAPI(title="My Agent", version="0.1.0")
agent = MyAgent()

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, Any]] = []

@app.post("/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    return agent.ask(query=req.query, history=req.history)

@app.get("/")
def health():
    return {"message": "OK"}
```

### requirements.txt (minimal)
```text
litellm
fastapi
uvicorn[standard]
python-dotenv
```

### Dockerfile (isolate the app)
```dockerfile
FROM mirror.gcr.io/library/python:3.11-slim
WORKDIR /app
COPY path/to/myagent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY path/to/myagent/ .
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Build and run
```bash
docker build -t my-agent -f path/to/myagent/Dockerfile .
docker run -d -p 8089:8080 \
  -e GEOAI_MODEL="ollama/llama3.2" \
  -e OLLAMA_HOST="http://host.docker.internal:11434" \
  --name my-agent-container my-agent

curl -sS -X POST http://localhost:8089/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"do something with foo"}'
```

### Common pitfalls to avoid
- Use top-level imports in `server.py` and `agent.py` because the app is copied to `/app` and run as a plain module.
- Copy only the app directory in the Dockerfile to avoid importing heavy modules from the monorepo.
- Keep `requirements.txt` minimal for the isolated service; add only what you need.
- When using Litellm with Ollama, set `api_base` via `OLLAMA_HOST`.
- If you do use Google ADK, import under the `google.adk` namespace and verify the module exists in the installed wheel.

### Using Vertex AI via Litellm
Set `GEOAI_MODEL` to a Vertex model and provide credentials via environment variables supported by Litellm:

```bash
# Example: Gemini 1.5 Flash on Vertex AI
export GEOAI_MODEL="vertex_ai/gemini-1.5-flash"
export VERTEXAI_PROJECT="your-gcp-project-id"
export VERTEXAI_LOCATION="us-central1"
# Service account key file path (mounted into the container)
export GOOGLE_APPLICATION_CREDENTIALS="/app/keys/sa.json"

docker run -d -p 8082:8080 \
  -e GEOAI_MODEL="$GEOAI_MODEL" \
  -e VERTEXAI_PROJECT="$VERTEXAI_PROJECT" \
  -e VERTEXAI_LOCATION="$VERTEXAI_LOCATION" \
  -e GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS" \
  -v /abs/path/to/sa.json:/app/keys/sa.json:ro \
  --name agentgoogle-vertex my-agent
```

Notes:
- The code auto-detects providers: it sets `api_base` only for `ollama/*` models. For `vertex_ai/*`, Litellm reads the above env vars.
- Litellm’s Vertex provider also works with default ADC if the container is running on GCE/GKE with appropriate scopes/Workload Identity.


