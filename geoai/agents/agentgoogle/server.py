from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from agent import GeoAgent

app = FastAPI(
    title="GeoAI Google Agent",
    description="A web backend for a geospatial agent using Google ADK and litellm.",
    version="0.1.0",
)

# Initialize the agent globally so it's created only once.
geo_agent = GeoAgent()

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, Any]] = []

@app.post("/chat", summary="Process a user query")
def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Receives a user's query and optional conversation history, processes it with the GeoAgent,
    and returns the JSON instruction for the mapping client.
    """
    result = geo_agent.ask(query=request.query, history=request.history)
    return result

@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"message": "GeoAI Google Agent is running."}
