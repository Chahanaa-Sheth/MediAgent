from typing import Dict, List, Any, Optional, AsyncGenerator
import os
from groq import Groq
from utils.exceptions import Logger, LLMError


class LLMService:
    """Service for LLM operations"""

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.logger = Logger("LLMService")
        self.model = "llama-3.1-8b-instant"

    async def stream_response(
        self,
        system_prompt: str,
        user_message: str,
        **context
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.logger.error("LLM streaming failed", error=str(e))
            raise LLMError(f"LLM streaming failed: {str(e)}")

    async def get_full_response(
        self,
        system_prompt: str,
        user_message: str,
        **context
    ) -> str:
        """Get full response from LLM (not streaming)"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return completion.choices[0].message.content

        except Exception as e:
            self.logger.error("LLM request failed", error=str(e))
            raise LLMError(f"LLM request failed: {str(e)}")
