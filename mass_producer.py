import os
import json
import time
from engine.brain import DialogueEngine, CharacterPersona
from engine.voice import VoiceEngine
from engine.director import VideoDirector
from dotenv import load_dotenv

# Load API keys from the .env file (Security First!)
load_dotenv()

def safe_print(msg):
    """Prints ASCII-safe strings to prevent Windows terminal encoding crashes."""
    try:
        # We strip emojis and weird symbols that might crash a standard PowerShell window
        print(str(msg).encode('ascii', 'ignore').decode('ascii'))
    except:
        print("[Print Error] Could not display message")

def mass_produce_videos(niche: str, days: int = 7):
    """
    The Orchestration Hub. 
    Connects Brain -> Voice -> Director in a loop to create multiple videos.
    """
    safe_print(f"--- STARTING MASS PRODUCTION FOR NICHE: {niche} ---")
    
    # Initialize all three core engines
    brain = DialogueEngine(api_key=os.getenv("GROQ_API_KEY"))
    voice = VoiceEngine()
    director = VideoDirector()
    
    # Define the characters 'Alex' and 'Sarah'
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

    # 1. Mode Sensing: Are we using manual scripts or AI auto-generation?
    manual_folder = os.path.join("scripts", "scripts_to_render")
    if os.path.exists(manual_folder):
        manual_files = [f for f in os.listdir(manual_folder) if f.endswith(".json")]
    else:
        manual_files = []
    
    if manual_files:
        safe_print(f"--- Found {len(manual_files)} manual scripts. Switching to BULK MANUAL mode. ---")
        topics = manual_files 
        mode = "MANUAL"
    else:
        safe_print(f"--- No manual scripts found. Generating ideas from the AI Brain. ---")
        # Ask the AI to come up with interesting debate topics for the niche
        topics = brain.generate_content_plan(niche, days=days)
        mode = "AUTO"

    safe_print(f"--- Production Plan: {len(topics)} videos queued. ---")
    production_log = []

    # 2. Main Production Loop
    for i, topic in enumerate(topics):
        video_id = f"day_{i+1}_{niche.replace(' ', '_').lower()}"
        safe_print(f"--- Processing Day {i+1}/{len(topics)}: {topic} ---")
        
        try:
            # Step A: Get the Script (Load from file or generate from AI)
            if mode == "MANUAL":
                with open(os.path.join(manual_folder, topic), "r") as f:
                    script = json.load(f)
            else:
                script_data = brain.generate_debate(topic, alex, sarah)
                script = script_data.get("script", [])
            
            if not script:
                safe_print(f"--- Skip: No valid script found for {topic} ---")
                continue
                
            # Step B: Voice Generation (Resilient Hybrid Engine)
            # This generates the manifest and all audio assets
            manifest_path = voice.process_script(video_id, script)
            
            # Step C: Visual Rendering (Stable Director Engine)
            # This turns the manifest and audio into a final MP4
            video_path = director.create_video(manifest_path)
            
            # Record the success
            production_log.append({
                "day": i+1,
                "topic": topic,
                "status": "SUCCESS",
                "video_path": video_path
            })
            safe_print(f"--- DAY {i+1} COMPLETE: {video_path} ---")
            
        except Exception as e:
            # If one video fails, the log records it but the factory keeps moving to the next one
            import traceback
            traceback.print_exc()
            safe_print(f"--- DAY {i+1} FAILED: {e} ---")
            production_log.append({"day": i+1, "topic": topic, "status": "FAILED", "error": str(e)})

    # 3. Save the final Batch Report
    with open("production_log.json", "w") as f:
        json.dump(production_log, f, indent=4)
        
    safe_print(f"\n--- MASS PRODUCTION FINISHED! ---")

if __name__ == "__main__":
    # The entry point of the entire system
    manual_folder = os.path.join("scripts", "scripts_to_render")
    if os.path.exists(manual_folder):
        manual_files = [f for f in os.listdir(manual_folder) if f.endswith(".json")]
    else:
        manual_files = []
    
    if manual_files:
        # If we have scripts, run them!
        mass_produce_videos("Manual", days=len(manual_files))
    else:
        # Otherwise, ask the user for a new niche to explore
        niche_input = input("Enter Niche (e.g. AI, Crypto, Fitness): ") or "AI Debate"
        days_input = int(input("How many days? (1-30): ") or 7)
        mass_produce_videos(niche_input, days=days_input)
