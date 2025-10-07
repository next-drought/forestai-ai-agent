import os
import json
from typing import List, Dict, Any

from litellm import completion

from tools import MapTools

# Set up the model and optional base URL for providers like Ollama
MODEL_NAME = os.environ.get("GEOAI_MODEL", "ollama/llama3.1")
API_BASE = os.environ.get("OLLAMA_HOST")


class GeoAgent:
    """A geospatial agent that can control a map via function calling."""

    def __init__(self):
        self.map_tools = MapTools()
        # Tools available to the agent
        self.tools = {
            # Core navigation
            "fly_to": self.map_tools.fly_to,
            "zoom_to": self.map_tools.zoom_to,
            # Layer management
            "add_basemap": self.map_tools.add_basemap,
            "add_cog_layer": self.map_tools.add_cog_layer,
            "add_vector": self.map_tools.add_vector,
            "remove_layer": self.map_tools.remove_layer,
            "get_layer_names": self.map_tools.get_layer_names,
            # 3D and styling
            "set_terrain": self.map_tools.set_terrain,
            "remove_terrain": self.map_tools.remove_terrain,
            "set_pitch": self.map_tools.set_pitch,
            "set_opacity": self.map_tools.set_opacity,
        }

        # Minimal tool specs to guide function calling
        self.tool_specs: List[Dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "zoom_to",
                    "description": "Zoom the map to a specific level.",
                    "parameters": {
                        "type": "object",
                        "properties": {"zoom": {"type": "number"}},
                        "required": ["zoom"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_cog_layer",
                    "description": "Add a COG layer by URL.",
                    "parameters": {
                        "type": "object",
                        "properties": {"url": {"type": "string"}},
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fly_to",
                    "description": "Fly to longitude, latitude.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "longitude": {"type": "number"},
                            "latitude": {"type": "number"},
                        },
                        "required": ["longitude", "latitude"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_basemap",
                    "description": "Add a basemap by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_layer",
                    "description": "Remove a layer by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_layer_names",
                    "description": "Get the names of all layers.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_terrain",
                    "description": "Set terrain exaggeration.",
                    "parameters": {
                        "type": "object",
                        "properties": {"exaggeration": {"type": "number"}},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_terrain",
                    "description": "Remove terrain.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_pitch",
                    "description": "Set the map pitch.",
                    "parameters": {
                        "type": "object",
                        "properties": {"pitch": {"type": "number"}},
                        "required": ["pitch"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_opacity",
                    "description": "Set layer opacity.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "opacity": {"type": "number"},
                        },
                        "required": ["name", "opacity"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_vector",
                    "description": "Add a vector dataset.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "name": {"type": "string"},
                        },
                        "required": ["data"],
                    },
                },
            },
        ]

    def ask(self, query: str, history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
        """Processes a user's natural language query about a map."""

        system_prompt = (
            "You are a map control agent. Translate the user's request into a single tool call. "
            "Call ONE tool with MINIMAL parameters only."
        )

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        for message in history:
            messages.append(message)
        messages.append({"role": "user", "content": query})

        try:
            kwargs: Dict[str, Any] = {}
            if API_BASE:
                kwargs["api_base"] = API_BASE

            response = completion(
                model=MODEL_NAME,
                messages=messages,
                tools=self.tool_specs,
                **kwargs,
            )

            response_message = response.choices[0].message
            tool_calls = getattr(response_message, "tool_calls", None)
            if not tool_calls:
                return {
                    "action": "chat_response",
                    "payload": {"message": response.choices[0].message.content},
                }

            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            raw_args = tool_call.function.arguments or "{}"
            try:
                tool_args = json.loads(raw_args)
            except Exception:
                tool_args = {}

            if tool_name in self.tools:
                tool_function = self.tools[tool_name]
                return tool_function(**tool_args)
            else:
                return {"action": "error", "payload": {"message": f"Tool '{tool_name}' not found."}}

        except Exception as e:
            print(f"An error occurred: {e}")
            return {"action": "error", "payload": {"message": str(e)}}
