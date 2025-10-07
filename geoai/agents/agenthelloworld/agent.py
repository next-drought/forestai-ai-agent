import os
import json
from typing import Dict, Any, List

from litellm import completion
import tools

# Model and optional Ollama base URL
MODEL_NAME = os.environ.get("GEOAI_MODEL", "ollama/llama3.1")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST")


class HelloWorldAgent:
    """A simple agent that can greet people."""

    def __init__(self) -> None:
        self.tool_functions = {"greet": tools.greet}
        self.tool_specs: List[Dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "greet",
                    "description": "Generates a greeting for the given name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the person to greet.",
                            }
                        },
                        "required": ["name"],
                    },
                },
            }
        ]

    def ask(self, query: str) -> Dict[str, Any]:
        """Processes a user's query."""

        system_prompt = (
            "You are a friendly assistant. Use tools when appropriate; "
            "otherwise respond naturally."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            kwargs: Dict[str, Any] = {}
            if OLLAMA_BASE_URL:
                # litellm supports api_base for provider-specific base URLs
                kwargs["api_base"] = OLLAMA_BASE_URL

            response = completion(
                model=MODEL_NAME,
                messages=messages,
                tools=self.tool_specs,
                **kwargs,
            )

            response_message = response.choices[0].message
            tool_calls = getattr(response_message, "tool_calls", None)

            if not tool_calls:
                return {"response": response_message.content}

            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            raw_args = tool_call.function.arguments or "{}"
            try:
                tool_args = json.loads(raw_args)
            except Exception:
                tool_args = {}

            if tool_name in self.tool_functions:
                tool_function = self.tool_functions[tool_name]
                tool_result = tool_function(**tool_args)
                return {"response": tool_result}
            else:
                return {"response": f"Error: Tool '{tool_name}' not found."}

        except Exception as e:
            print(f"An error occurred: {e}")
            return {"response": f"Error: {str(e)}"}
