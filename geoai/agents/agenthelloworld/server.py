from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

from agent import HelloWorldAgent

app = FastAPI(
    title="Hello World ADK Agent",
    description="A minimal example of a web backend for an agent using Google ADK.",
    version="0.1.0",
)

# Initialize the simple agent
hello_agent = HelloWorldAgent()

class ChatRequest(BaseModel):
    query: str

@app.post("/chat", summary="Process a user query")
def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Receives a user's query, processes it with the HelloWorldAgent,
    and returns the text response.
    """
    result = hello_agent.ask(query=request.query)
    return result

@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"message": "Hello World ADK Agent is running."}
