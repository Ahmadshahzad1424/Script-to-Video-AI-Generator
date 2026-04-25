import os
import random
import json
import traceback
import gc
import re
import time
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_audioclips
from moviepy import vfx
from typing import List, Dict

class VideoDirector:
    """
    Elite Video Director - Stable Background Edition
    """
    
    def __init__(self, assets_dir=".", output_dir="data/videos"):
        self.assets_dir = assets_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Paths (Updated for Clean Structure)
        self.bg_dir = os.path.join(assets_dir, "assets", "background_videos")
        self.char_dir = os.path.join(assets_dir, "assets", "characters")
        self.WIDTH = 540
        self.HEIGHT = 960
        self.last_bg = None
        
    def _sanitize_text(self, text: str) -> str:
        text = text.replace('…', '...').replace('’', "'").replace('“', '"').replace('”', '"')
        return text.encode('ascii', 'ignore').decode('ascii')

    def _get_random_asset(self, folder: str, extension: str, avoid: str = None) -> str:
        random.seed(time.time_ns())
        files = [f for f in os.listdir(folder) if f.lower().endswith(extension)]
        if not files: return None
        
        if avoid and len(files) > 1:
            files = [f for f in files if f != avoid]
            
        choice = random.choice(files)
        print(f"--- SELECTED ASSET: {choice} ---")
        return os.path.join(folder, choice)

    def _create_char_clip(self, img_path, width, pos, start, duration):
        from PIL import Image
        import numpy as np
        with Image.open(img_path) as pil_img:
            pil_img = pil_img.convert("RGBA")
            aspect = pil_img.height / pil_img.width
            new_height = int(width * aspect)
            pil_img = pil_img.resize((width, new_height), Image.Resampling.LANCZOS)
            img_array = np.array(pil_img)
        
        return (ImageClip(img_array).with_start(start).with_duration(duration).with_position(pos).with_effects([vfx.FadeIn(duration=0.2), vfx.FadeOut(duration=0.2)]))

    def create_video(self, manifest_path: str):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        video_id = manifest["video_id"]
        turns = manifest["turns"]
        print(f"--- Starting STABLE Production: {video_id} ---")
        
        clips_to_close = []
        try:
            # 1. Assets
            bg_video_path = self._get_random_asset(self.bg_dir, ".mp4", avoid=self.last_bg)
            if bg_video_path: self.last_bg = os.path.basename(bg_video_path)
            
            char_paths = {
                "Alex": self._get_random_asset(os.path.join(self.char_dir, "Alex"), ".png"),
                "Sarah": self._get_random_asset(os.path.join(self.char_dir, "Sarah"), ".png")
            }
            
            # 2. Audio
            audio_clips = [AudioFileClip(t["audio_path"]) for t in turns]
            clips_to_close.extend(audio_clips)
            final_audio = concatenate_audioclips(audio_clips)
            clips_to_close.append(final_audio)
            
            # 3. Background (STABLE VERSION)
            bg = VideoFileClip(bg_video_path)
            clips_to_close.append(bg)
            
            # Simple loop and resize (No speedup for stability)
            bg = (bg
                  .with_effects([vfx.Loop(duration=final_audio.duration)])
                  .resized(height=self.HEIGHT))
            
            # Center crop
            bg = bg.cropped(x_center=bg.w/2, y_center=bg.h/2, width=self.WIDTH, height=self.HEIGHT)
            
            clips = [bg]
            current_time = 0
            
            # 4. Turn Processing
            for turn in turns:
                audio_clip = AudioFileClip(turn["audio_path"])
                clips_to_close.append(audio_clip)
                duration = audio_clip.duration
                speaker = turn["character"]
                listener = "Sarah" if speaker == "Alex" else "Alex"
                
                clips.append(self._create_char_clip(char_paths[speaker], 450, ("center", 180), current_time, duration))
                clips.append(self._create_char_clip(char_paths[listener], 220, (20, 560) if listener=="Alex" else (300, 560), current_time, duration))
                
                clean_text = self._sanitize_text(re.sub(r'\[.*?\]', '', turn["text"]).strip())
                txt = TextClip(
                    text=clean_text, font_size=55, color='yellow', font=r'C:\Windows\Fonts\arialbd.ttf',
                    method='caption', size=(460, None), stroke_color='black', stroke_width=2
                ).with_start(current_time).with_duration(duration).with_position(("center", 750))
                
                clips.append(txt.with_effects([vfx.FadeIn(duration=0.1)]))
                current_time += duration
            
            # 5. Render
            final_video = CompositeVideoClip(clips, size=(self.WIDTH, self.HEIGHT)).with_audio(final_audio)
            clips_to_close.append(final_video)
            
            output_path = os.path.join(self.output_dir, f"{video_id}_final.mp4")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", bitrate="1800k", threads=1, logger=None, ffmpeg_params=["-pix_fmt", "yuv420p"])
            return output_path

        finally:
            print("--- Cleanup ---")
            for clip in clips_to_close:
                try: clip.close()
                except: pass
            gc.collect()

if __name__ == "__main__":
    VideoDirector().create_video("data/audio/test_debate_001_manifest.json")
