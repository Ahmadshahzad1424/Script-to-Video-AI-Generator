import os
import sys
from tests.voice_prototype import VoicePrototype

def run_test():
    proto = VoicePrototype(output_dir="tests/audio_test")
    input_file = "tests/test_input.wav"
    
    if not os.path.exists(input_file):
        print(f"FAILED: {input_file} not found.")
        return

    # 1. Test Emotions
    results = []
    for emotion in ["angry", "frustrated", "skeptical"]:
        print(f"Processing emotion: {emotion}...")
        path, config = proto.apply_emotion(input_file, emotion)
        
        # Trim for duration
        trimmed_path, duration = proto.trim_with_padding(path)
        
        results.append({
            "turn_id": len(results) + 1,
            "character": "Alex",
            "text": "Your AI stack is a digital house of cards.",
            "audio_metadata": {
                "file_path": trimmed_path,
                "trimmed_duration_ms": duration
            },
            "emotion_applied": {
                "label": emotion,
                "pitch_shift": config["pitch"],
                "speed_factor": config["speed"]
            }
        })

    # 2. Generate Manifest
    print("Generating manifest...")
    manifest_path = proto.generate_manifest("test_video_001", results)
    print(f"SUCCESS: Manifest generated at {manifest_path}")

if __name__ == "__main__":
    run_test()
