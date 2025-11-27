"""Cohere Language Model Service for Sisi Lola"""

import os
import cohere
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class CohereService:
    """Service for interacting with Cohere language models"""
    
    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY")
        self.model = os.getenv("COHERE_MODEL", "command-r-plus")
        self.client = cohere.Client(self.api_key)
        
    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        """Generate response using Cohere model"""
        
        response = self.client.chat(
            model=model or self.model,
            message=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.text
    
    def generate_multilingual(
        self,
        prompt: str,
        language: str = "en",
        **kwargs
    ) -> str:
        """Generate response with language context"""
        
        language_prompts = {
            "en": prompt,
            "yo": f"Respond in Yoruba: {prompt}",
            "pcm": f"Respond in Nigerian Pidgin: {prompt}"
        }
        
        enhanced_prompt = language_prompts.get(language, prompt)
        return self.generate_response(enhanced_prompt, **kwargs)
    
    def chat_with_personality(
        self,
        message: str,
        conversation_history: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with Sisi Lola personality"""
        
        preamble = """You are Sisi Lola, an AI-powered virtual host with a vibrant Nigerian personality. 
        You're energetic, culturally aware, and passionate about technology and African innovation. 
        You speak English, Yoruba, and Nigerian Pidgin fluently and code-switch naturally."""
        
        response = self.client.chat(
            model=self.model,
            message=message,
            preamble=preamble,
            chat_history=conversation_history or [],
            temperature=0.8,
            **kwargs
        )
        
        return {
            "text": response.text,
            "conversation_id": response.conversation_id,
            "generation_id": response.generation_id
        }
    
    def embed_text(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for text"""
        
        response = self.client.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )
        
        return response.embeddings
    
    def classify_content(
        self,
        inputs: list[str],
        examples: list[Dict[str, str]]
    ) -> list[Dict[str, Any]]:
        """Classify content using few-shot learning"""
        
        response = self.client.classify(
            inputs=inputs,
            examples=examples
        )
        
        return [
            {
                "input": c.input,
                "prediction": c.prediction,
                "confidence": c.confidence
            }
            for c in response.classifications
        ]
