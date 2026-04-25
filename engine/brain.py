import os
from typing import List, Dict
from groq import Groq
from dataclasses import dataclass

@dataclass
class CharacterPersona:
    """Defines the personality and voice of a debate character."""
    name: str
    description: str
    traits: List[str]
    voice_type: str
    speaking_style: str

class DialogueEngine:
    """
    The 'Brain' of the system.
    Uses Groq's Llama-3 to generate high-tension, viral debate scripts.
    """
    def __init__(self, api_key: str):
        # Initialize the Groq client with your API key
        self.client = Groq(api_key=api_key)
        # We use Llama 3.3 70B for its high reasoning capabilities and speed
        self.model = "llama-3.3-70b-versatile"
        
    def generate_debate(self, topic: str, char_a: CharacterPersona, char_b: CharacterPersona) -> Dict:
        """Generates a structured JSON script for a 15-20 second debate."""
        
        # The System Prompt is the 'Master Instructions' for the AI
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

        --- CHARACTER TRAITS ---
        - {char_a.name}: {char_a.description} ({', '.join(char_a.traits)})
        - {char_b.name}: {char_b.description} ({', '.join(char_b.traits)})

        --- CONTENT RULES ---
        - The debate must be about: {topic}
        - Keep it fast-paced, aggressive, and witty.
        - Maximum 6-8 total dialogue lines (20 seconds max).
        """

        try:
            # Request the script from the LLM
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}],
                model=self.model,
                temperature=0.8, # Higher temperature for more creative/witty dialogue
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the JSON response
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error generating debate: {e}")
            return {"script": []}
