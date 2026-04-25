import os
import json
from engine.voice import VoiceEngine
from engine.director import VideoDirector

def run_full_pipeline(manual=False):
    """
    The Master Orchestrator. 
    Links Brain -> Voice -> Director.
    """
    video_id = "custom_debate_001"
    
    # 1. Get the Script
    if manual:
        print("--- Mode: MANUAL SCRIPT ---")
        if not os.path.exists("manual_script.json"):
            print("Error: manual_script.json not found!")
            return
        with open("manual_script.json", "r") as f:
            script = json.load(f)
    else:
        print("--- Mode: AI AUTO-GENERATE ---")
        # In a real run, we would call brain.generate_script() here
        # For now, we'll default to the manual one for your testing
        with open("manual_script.json", "r") as f:
            script = json.load(f)

    # 2. Generate Voice & Manifest
    voice = VoiceEngine()
    manifest_path = voice.process_script(video_id, script)
    
    # 3. Render Video
    director = VideoDirector()
    video_path = director.create_video(manifest_path)
    
    print(f"\n🚀 ALL SYSTEMS GO! Your video is ready at: {video_path}")

if __name__ == "__main__":
    # You can change this to False if you want to use the AI generator later
    run_full_pipeline(manual=True)
