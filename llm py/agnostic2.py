# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")
# agnostic.py - A model-agnostic client app that consumes OpenAI, Anthropic, and Google APIs, using an adapter pattern to normalize outputs.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

import requests
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Common output format
class ModelOutput:
    def __init__(self, state: str, payload: Any, metadata: Dict = None):
        self.state = state  # "tool_call", "answer", "clarification", "error"
        self.payload = payload
        self.metadata = metadata or {}

# Abstract adapter interface
class ModelAdapter(ABC):
    @abstractmethod
    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        pass

# OpenAI adapter
class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-2024-08-06",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema", "json_schema": schema}
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        choice = response_data["choices"][0]
        message = choice["message"]
        if message.get("tool_calls"):
            return ModelOutput("tool_call", message["tool_calls"], {"finish_reason": choice["finish_reason"]})
        elif message.get("content"):
            # Check for clarification (simplified heuristic)
            content = message["content"]
            state = "clarification" if "?" in content else "answer"
            return ModelOutput(state, content)
        elif message.get("refusal"):
            return ModelOutput("error", message["refusal"])

# Anthropic adapter
class AnthropicAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"

    def query(self, prompt: str, schema: Dict) -> ModelOutput:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        # Convert schema to Anthropic's tool format
        tools = [{"name": "tool", "input_schema": schema}] if schema else []
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            return ModelOutput("error", response_data["error"])

        content = response_data["content"]
        for block in content:
            if block["type"] == "tool_use":
                return ModelOutput("tool_call", block, {"stop_reason": response_data["stop_reason"]})
            elif block["type"] == "text":
                state = "clarification" if "?" in block["text"] else "answer"
                return ModelOutput(state, block["text"])

# Unified client
class ModelClient:
    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def query(self, prompt: str, schema: Optional[Dict] = None) -> ModelOutput:
        return self.adapter.query(prompt, schema)

# Example usage
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {"type": "array", "items": {"type": "object"}},
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    }
}

# Initialize adapters
openai_client = ModelClient(OpenAIAdapter(api_key="your_openai_key"))
anthropic_client = ModelClient(AnthropicAdapter(api_key="your_anthropic_key"))

# Query both providers
prompt = "Get weather in NYC"
openai_output = openai_client.query(prompt, schema)
anthropic_output = anthropic_client.query(prompt, schema)

print(f"OpenAI: {openai_output.state}, {openai_output.payload}")
print(f"Anthropic: {anthropic_output.state}, {anthropic_output.payload}")