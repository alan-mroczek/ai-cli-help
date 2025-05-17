import os
import requests
from typing import List, Optional

import json

from utils import load_env

load_env()

_API_URL = "https://api.openai.com/v1/chat/completions"
_HEADERS  = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
             "Content-Type": "application/json"}

_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# System prompt used for all models
_SYSTEM_PROMPT = """
You are a Bash expert.

— Output exactly one valid Bash command, no code fences.
— No explanations, no extra text, no blank lines.
— If you are uncertain, output an empty string instead.
— If the additional *context* already contains a single-line Bash command
  that directly satisfies the request, return that command verbatim.
— Otherwise translate the user's pseudo command into a real command.

Example
User: list the ten largest files here
Assistant: du -ah . | sort -rh | head -n 10
"""

def _format_system_message(context: Optional[str]) -> str:
    """Return the system prompt, optionally extended with additional context."""
    system_message = _SYSTEM_PROMPT
    
    # If context is provided, add it to the system message
    if context:
        system_message += f"\n\nAdditional context: \n{context}"
    
    # User message is now just the prompt/request
    return system_message

def _openai_chat(prompt: str,
                 context: Optional[str],
                 max_suggestions: int,
                 model_name: str) -> List[str]:
    system_message = _format_system_message(context)
    
    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 150,
        "temperature": 0.2
    }

    r = requests.post(_API_URL, headers=_HEADERS, data=json.dumps(body), timeout=30)

    if r.status_code != 200:
        raise RuntimeError(f"OpenAI API request failed: {r.status_code} {r.text}")

    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    return [line.strip() for line in text.splitlines() if line.strip()][:max_suggestions]


def _ollama(prompt: str, context: Optional[str], max_suggestions: int, model_name: str) -> List[str]:
    """Call ollama via HTTP API using the chat endpoint."""
    
    ollama_api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/chat")
    
    # Extract model name from ollama/model-name format
    model = model_name.split("/", 1)[-1] if "/" in model_name else model_name
    
    # Use the same format_prompt function as OpenAI
    system_message = _format_system_message(context)
    
    # Create messages array with system and user messages
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.15, "top_p": 0.9, "stop": ["\n"]} # For now hard stop to reduce chattiness
    }
    
    try:
        response = requests.post(ollama_api_url, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API request failed: {response.status_code} {response.text}")
            
        response.raise_for_status()
        result = response.json()
        text = result.get("message", {}).get("content", "").strip()
        return [line.strip() for line in text.splitlines() if line.strip()][:max_suggestions]
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama API request failed: {str(e)}")


def _gemini(prompt: str, context: Optional[str], max_suggestions: int, model_name: str) -> List[str]:
    """Call Gemini API using direct HTTP requests to generate command suggestions."""
    
    # Check if API key is configured
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    
    # Extract model name from gemini/model-name format
    model = model_name.split("/", 1)[-1] if "/" in model_name else model_name
    
    # Format the system message and prompt
    system_message = _format_system_message(context)
    
    # Build the API URL with the model name
    api_url = f"{_GEMINI_API_URL}/{model}:generateContent?key={api_key}"
    
    # Build the request payload
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{system_message}\n\nUser: {prompt}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 300,
            "stopSequences": []
        }
    }
    
    try:
        # Make the HTTP request
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API request failed: {response.status_code} {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        # Extract text from response - handle Gemini's specific response structure
        text = ""
        try:
            # Navigate through the response structure to find the text
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        except (KeyError, IndexError):
            # If structure is unexpected, try to find text elsewhere or return empty
            text = str(result.get("text", "")).strip()
        
        # Split into lines and return the requested number
        return [line.strip() for line in text.splitlines() if line.strip()][:max_suggestions]
    
    except Exception as e:
        raise RuntimeError(f"Gemini API request failed: {str(e)}")


def get_suggestions(prompt: str, context: Optional[str], model_name: str, max_suggestions: int) -> List[str]:
    """Dispatch to provider based on model_name prefix."""
    model_name = model_name or "openai/gpt-4o-mini"
    if model_name.startswith("openai"):
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _, _, m = model_name.partition("/")
        return _openai_chat(prompt, context, max_suggestions, m)
    elif model_name.startswith("ollama"):
        return _ollama(prompt, context, max_suggestions, model_name)
    elif model_name.startswith("gemini"):
        return _gemini(prompt, context, max_suggestions, model_name)
    else:
        # Fallback: naive echo
        return [f"echo '{prompt}'"][:max_suggestions]
