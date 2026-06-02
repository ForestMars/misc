# constrain.py - Generate outputs with enforced schema.
__author__ = 'Forest Mars'
__version__ = '1.0.0' 
__all__ = []

from outlines import models, generate
import json

# Load fine-tuned model
model = models.transformers("./finetuned_model")

# Define JSON schema for outputs
schema = {
    "type": "object",
    "properties": {
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "function": {"type": "string"},
                    "arguments": {"type": "object"}
                },
                "required": ["function", "arguments"]
            }
        },
        "content": {"type": "string"},
        "clarification": {"type": "string"}
    },
    "additionalProperties": False,
    "oneOf": [
        {"required": ["tool_calls"]},
        {"required": ["content"]},
        {"required": ["clarification"]}
    ]
}

# Generate output
prompt = "Get the weather in NYC"
generator = generate.json(model, schema)
output = generator(prompt)
print(json.dumps(output, indent=2))
# Example output:
# {
#   "tool_calls": [
#     {
#       "function": "get_weather",
#       "arguments": {
#         "location": "NYC"
#       }
#     }
#   ]
# } 
