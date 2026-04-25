import os
import json
import time
from engine.brain import DialogueEngine, CharacterPersona
from engine.voice import VoiceEngine
from engine.director import VideoDirector
from dotenv import load_dotenv

load_dotenv()

def safe_print(msg):
    """Prints ASCII-safe strings to prevent Windows charmap crashes."""
    try:
        print(str(msg).encode('ascii', 'ignore').decode('ascii'))
    except:
        print("[Print Error] Could not display message")

def mass_produce_videos(niche: str, days: int = 7):
    """
    The Automated Content Factory.
    Generates a full week (or month) of videos from a single niche.
    """
    safe_print(f"--- STARTING MASS PRODUCTION FOR NICHE: {niche} ---")
    
    brain = DialogueEngine(api_key=os.getenv("GROQ_API_KEY"))
    voice = VoiceEngine()
    director = VideoDirector()
    
    # 1. Define Personas
    alex = CharacterPersona(
        name="Alex",
        description="Assertive, logical tech-cynic",
        traits=["cynical", "sharp"],
        voice_type="troy",
        speaking_style="direct"
    )
    sarah = CharacterPersona(
        name="Sarah",
        description="Intuitive, sharp tech-optimist",
        traits=["idealistic", "witty"],
        voice_type="diana",
        speaking_style="expressive"
    )

    # Path to your manually written scripts
    manual_folder = os.path.join("scripts", "scripts_to_render")
    manual_files = [f for f in os.listdir(manual_folder) if f.endswith(".json")]
    
    if manual_files:
        safe_print(f"--- Found {len(manual_files)} manual scripts. Switching to BULK MANUAL mode. ---")
        topics = manual_files # We'll use the filenames as 'topics'
        mode = "MANUAL"
    else:
        safe_print(f"--- No manual scripts found. Switching to AI AUTO mode. ---")
        topics = brain.generate_content_plan(niche, days=days)
        mode = "AUTO"

    safe_print(f"--- Production Plan: {len(topics)} videos queued. ---")

    production_log = []

    # 3. Mass Processing Loop
    for i, topic in enumerate(topics):
        video_id = f"day_{i+1}_{niche.replace(' ', '_').lower()}"
        safe_print(f"--- Processing Day {i+1}/{days}: {topic} ---")
        
        try:
            # Step A: Get Script
            if mode == "MANUAL":
                with open(os.path.join(manual_folder, topic), "r") as f:
                    script = json.load(f)
            else:
                script_data = brain.generate_debate(topic, alex, sarah)
                script = script_data.get("script", [])
            
            if not script:
                safe_print(f"--- Failed to generate script for {topic}. Skipping. ---")
                continue
                
            # Step B: Generate Voice & Manifest
            manifest_path = voice.process_script(video_id, script)
            
            # Step C: Render Video
            video_path = director.create_video(manifest_path)
            
            production_log.append({
                "day": i+1,
                "topic": topic,
                "status": "SUCCESS",
                "video_path": video_path
            })
            safe_print(f"--- DAY {i+1} COMPLETE: {video_path} ---")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            safe_print(f"--- DAY {i+1} FAILED: {e} ---")
            production_log.append({"day": i+1, "topic": topic, "status": "FAILED", "error": str(e)})

    # 4. Final Report
    with open("production_log.json", "w") as f:
        json.dump(production_log, f, indent=4)
        
    safe_print(f"\n--- MASS PRODUCTION FINISHED! Check production_log.json for details. ---")

if __name__ == "__main__":
    # Auto-sense: Check if we have manual scripts first
    manual_folder = os.path.join("scripts", "scripts_to_render")
    if os.path.exists(manual_folder):
        manual_files = [f for f in os.listdir(manual_folder) if f.endswith(".json")]
    else:
        manual_files = []
    
    if manual_files:
        # We have manual scripts, just run them!
        mass_produce_videos("Manual", days=len(manual_files))
    else:
        # No manual scripts, ask for niche
        niche_input = input("Enter your Niche (e.g. AI, Crypto, Fitness): ") or "AI and Jobs"
        days_input = int(input("How many days of content? (1-30): ") or 7)
        mass_produce_videos(niche_input, days=days_input)
