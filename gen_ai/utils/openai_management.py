import os

from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key=None):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable or provide the api_key argument.")
        
        self.openai_client = OpenAI(api_key=api_key)

    def get_chat_completion(self, model, messages, temperature, response_format=None):
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if response_format:
            params["response_format"] = {"type": response_format}
        
        completion = self.openai_client.chat.completions.create(**params)

        return completion.choices[0].message.content
    
