import os
import json
import hashlib
from typing import List, Dict, Optional
from groq import Groq
from dataclasses import dataclass

@dataclass(frozen=True)
class CharacterPersona:
    name: str
    description: str
    traits: List[str]
    voice_type: str
    speaking_style: str

class DialogueEngine:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        
    def generate_debate(self, topic: str, char_a: CharacterPersona, char_b: CharacterPersona) -> Dict:
        """Generates a high-performance viral debate script using the Master Prompt."""
        # Using a raw string block to avoid linter confusion with f-string variables
        system_prompt = f"""
You are a high-performance script generator for a short-form AI video engine.
Your ONLY job is to generate a JSON array of dialogue lines for a 15-20 second debate video between two characters: {char_a.name} and {char_b.name}.

--- CRITICAL OUTPUT RULES ---
- Output MUST be valid JSON only.
- Do NOT include explanations, comments, or markdown.
- Output must be a single JSON array.

--- REQUIRED JSON SCHEMA ---
[
  {{
    "character": "{char_a.name} or {char_b.name}",
    "text": "[emotion] Dialogue line here",
    "emotion": "emotion_name"
  }}
]

--- CHARACTER RULES ---
- {char_a.name}: {char_a.description}. Style: {char_a.speaking_style}.
- {char_b.name}: {char_b.description}. Style: {char_b.speaking_style}.

--- CONTENT RULES ---
- Topic MUST clearly include a programming language or technology.
- Each line must be short (max 8-10 words).
- Total lines: 6 to 8.

--- EMOTION RULES ---
- Every line MUST include an emotion tag like [confident] or [mocking].
- The "emotion" field must match the tag exactly.

TOPIC: {topic}
"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}],
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)
            
            if isinstance(data, list):
                script = data
            elif isinstance(data, dict):
                # Handle cases where AI wraps the array in a key
                for key in ["turns", "dialogue", "script"]:
                    if key in data:
                        script = data[key]
                        break
                else:
                    # Fallback if it's just a dict of fields
                    script = [v for v in data.values() if isinstance(v, list)]
                    script = script[0] if script else []
            else:
                script = []

            return {
                "script": script,
                "metadata": {"usage": response.usage.total_tokens}
            }
        except Exception as e:
            print(f"Error: {e}")
            return {"script": [], "error": str(e)}

    def generate_content_plan(self, niche: str, days: int = 30) -> List[str]:
        prompt = f"Generate {days} controversial programming debate topics for {niche}. JSON format: {{\"topics\": []}}"
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": prompt}],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content).get("topics", [])
        except:
            return [f"{niche} Topic {i+1}" for i in range(days)]
