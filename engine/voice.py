import os
import json
import hashlib
import time
import asyncio
from groq import Groq
from typing import List, Dict
from dotenv import load_dotenv
import edge_tts

load_dotenv()

class VoiceEngine:
    def __init__(self, output_dir="data/audio"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Premium Model (Groq)
        self.model = "canopylabs/orpheus-v1-english"
        self.premium_voices = {
            "Alex": "troy",
            "Sarah": "diana" 
        }
        
        # Fallback Model (Edge TTS - Free & Unlimited)
        self.fallback_voices = {
            "Alex": "en-US-GuyNeural",
            "Sarah": "en-US-JennyNeural"
        }

    def _generate_fallback_audio(self, character: str, text: str, filepath: str):
        """
        Generates high-quality free audio using edge-tts as a fallback.
        """
        voice = self.fallback_voices.get(character, "en-US-GuyNeural")
        
        async def _save():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filepath)
            
        asyncio.run(_save())

    def generate_turn_audio(self, turn_id: int, character: str, text: str, emotion: str) -> Dict:
        """
        Generates a single turn of audio with automatic fallback logic.
        """
        import re
        clean_text = re.sub(r'\[.*?\]', '', text).strip()
        
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:10]
        # Base filename (we'll try .wav first, then .mp3 for fallback)
        filename = f"{character.lower()}_{emotion}_{text_hash}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        # 0. SMART CACHE: Check if this audio already exists to save tokens
        if os.path.exists(filepath):
            print(f"--- Using Cached Audio for {character} ---")
            return {
                "turn_id": turn_id,
                "character": character,
                "text": clean_text,
                "audio_path": filepath,
                "emotion": emotion,
                "engine": "cache"
            }
        
        # Also check for .mp3 (fallback version) in cache
        mp3_filepath = filepath.replace(".wav", ".mp3")
        if os.path.exists(mp3_filepath):
            print(f"--- Using Cached Fallback Audio for {character} ---")
            return {
                "turn_id": turn_id,
                "character": character,
                "text": clean_text,
                "audio_path": mp3_filepath,
                "emotion": emotion,
                "engine": "cache-fallback"
            }

        # 1. TRY PREMIUM (GROQ ORPHEUS)
        directed_text = f"[{emotion}] {clean_text}"
        voice = self.premium_voices.get(character, "troy")
        max_retries = 1 # Only 1 retry for premium to keep it fast
        
        for attempt in range(max_retries + 1):
            try:
                print(f"Generating Premium audio for {character}... (Attempt {attempt+1})")
                response = self.client.audio.speech.create(
                    model=self.model,
                    voice=voice,
                    input=directed_text,
                    response_format="wav"
                )
                response.write_to_file(filepath)
                return {
                    "turn_id": turn_id, "character": character, "text": clean_text,
                    "audio_path": filepath, "emotion": emotion, "engine": "groq"
                }
            except Exception as e:
                err_str = str(e).lower()
                if "rate_limit" in err_str or "429" in err_str:
                    print(f"[WARNING] Groq Limit Hit. Switching to Fallback Engine for {character}...")
                    break # Jump to fallback immediately
                
                print(f"Error on premium attempt {attempt+1}: {e}")
                if attempt < max_retries:
                    time.sleep(1)
        
        # 2. FALLBACK (EDGE TTS)
        try:
            print(f"Generating Fallback audio for {character} using Edge-TTS...")
            # Use .mp3 for edge-tts
            fallback_path = filepath.replace(".wav", ".mp3")
            
            self._generate_fallback_audio(character, clean_text, fallback_path)
            
            return {
                "turn_id": turn_id,
                "character": character,
                "text": clean_text,
                "audio_path": fallback_path,
                "emotion": emotion,
                "engine": "edge-tts"
            }
        except Exception as fallback_err:
            print(f"CRITICAL FAILURE: Both Premium and Fallback failed: {fallback_err}")
            return None

    def process_script(self, video_id: str, script: List[Dict]) -> str:
        results = []
        for i, turn in enumerate(script):
            res = self.generate_turn_audio(
                turn_id=i+1,
                character=turn["character"],
                text=turn["text"],
                emotion=turn["emotion"]
            )
            if res:
                results.append(res)
        
        manifest = {
            "video_id": video_id,
            "total_turns": len(results),
            "turns": results
        }
        
        manifest_path = os.path.join(self.output_dir, f"{video_id}_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)
            
        return manifest_path

if __name__ == "__main__":
    engine = VoiceEngine()
    test_script = [
        {"character": "Alex", "text": "This is a test of the hybrid fallback system.", "emotion": "confident"},
        {"character": "Sarah", "text": "It looks like we can generate 30 videos a day now!", "emotion": "happy"}
    ]
    path = engine.process_script("hybrid_test", test_script)
    print(f"SUCCESS: Manifest generated at {path}")
