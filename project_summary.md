# 🚀 Nexus Core: Resilient AI Debate Engine

## 1. Project Objective
A high-retention, fully automated AI video generation pipeline designed for mass-scale content production. Nexus Core writes, voices, and edits professional 15-20 second "Short" format tech debates (9:16 vertical) with zero manual intervention.

---

## 2. Technical Stack
- **Brain:** Groq API (`llama-3.3-70b-versatile`) with "Viral Master Prompt" technology.
- **Voice (Resilient Hybrid):** 
  - *Premium:* Groq Orpheus TTS for emotional, high-fidelity audio.
  - *Unlimited Fallback:* Microsoft Edge TTS (Microsoft Neural) for 24/7 high-volume scaling.
- **Video Engine:** MoviePy v2.2.1 (Ultra-Light Memory-Safe Configuration).
- **Imaging:** Pillow (PIL) for pre-rendering character assets and preserving transparency.
- **Resolution:** 540x960 (Mobile Industry Standard) for high-speed automated rendering.

---

## 3. Core Engine Architecture

### 🧠 Brain (`engine/brain.py`)
- **Viral Prompting:** Generates high-tension technology debates between curated personas (Alex & Sarah).
- **JSON Rigidity:** Strict schema enforcement ensures 100% compatibility with the rendering pipeline.

### 🎙️ Voice (`engine/voice.py`)
- **Failsafe Switching:** Automatically detects API rate limits and switches to free high-quality fallback voices.
- **ASCII Sterilization:** Built-in sanitization to prevent "â€¦" encoding glitches in captions and audio.
- **MD5 Caching:** Smart fingerprinting prevents redundant API costs for repeated content.

### 🎬 Director (`engine/director.py`)
- **Memory-Safe Rendering:** Uses single-threaded processing and PIL pre-resizing to prevent Windows RAM crashes.
- **Variety Engine:** Time-based randomization and "Memory logic" ensure backgrounds alternate every video.
- **Cinematic Aesthetics:** High-readability yellow captions and dynamic character scaling for viral retention.

### 🏭 Mass Producer (`mass_producer.py`)
- **Batch Orchestration:** Designed to process 13+ video batches in a single run.
- **Terminal Shield:** Safe-print technology prevents console crashes during long-term production.

---

## 4. Key Engineering Breakthroughs
- ✅ **The Rate-Limit Wall:** Solved via Hybrid TTS Fallback architecture.
- ✅ **Shadow People Bug:** Solved via PIL buffer conversion for transparency.
- ✅ **The encoding Glitch:** Solved via ASCII sterilization logic.
- ✅ **RAM Paging Error:** Solved via 540p downscaling and explicit memory flush loops.

---

## 5. Current Operational Status
- 🟢 **Batch Capacity:** Verified (Successfully shipped a 13-video batch).
- 🟢 **Stability:** High (Memory and terminal shielding active).
- 🟢 **Scaling:** Unlimited (Hybrid audio prevents production stoppages).

---

## 6. Roadmap (Phase 5)
1. **Audio Ducking:** Automatic background music balancing.
2. **Dynamic Pacing:** Randomized background speedup for higher retention.
3. **Cloud Integration:** Automated TikTok/YouTube Shorts API uploading.

---
**Handover Note:** Nexus Core is a production-ready Content Factory. It is engineered for stability, resilience, and maximum viral impact.
