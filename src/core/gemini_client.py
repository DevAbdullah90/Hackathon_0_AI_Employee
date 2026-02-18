import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 8192

class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-flash-lite-latest"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name=model_name)
        
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate text content from a prompt"""
        if not self.api_key:
            return "Error: GEMINI_API_KEY not configured"
            
        try:
            # Configure the model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model
                
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return f"Error generating content: {str(e)}"

    def generate_structured_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured JSON output"""
        if not self.api_key:
            return {"error": "GEMINI_API_KEY not configured"}

        full_prompt = f"{prompt}\n\nIMPORTANT: Output ONLY valid JSON."
        
        try:
             # Configure the model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction,
                    generation_config={"response_mime_type": "application/json"}
                )
            else:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={"response_mime_type": "application/json"}
                )

            response = model.generate_content(full_prompt)
            
            # Try to parse the response as JSON
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback: try to find JSON block in text
                text = response.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != -1:
                    return json.loads(text[start:end])
                else:
                    return {"error": "Failed to parse JSON response", "raw_response": text}
                    
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {e}")
            return {"error": f"Error generating JSON: {str(e)}"}
