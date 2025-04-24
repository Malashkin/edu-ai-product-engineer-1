import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, name: str, role: str, temperature: float = 0.7):
        self.name = name
        self.role = role
        self.temperature = temperature
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
        })

    def get_response(self, prompt: str) -> str:
        """Get a response from the agent using OpenAI API."""
        self.add_message("user", prompt)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.conversation_history,
            temperature=self.temperature,
        )
        
        response_text = response.choices[0].message.content
        self.add_message("assistant", response_text)
        
        return response_text

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = [] 