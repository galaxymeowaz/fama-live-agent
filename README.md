# Project Fama: Holistic Space & Retail Optimizer 🏛️✨

**Project Fama** is a premium, AI-driven spatial architect designed for the **Google Gemini Live Agent Challenge**. It leverages cutting-edge multimodal intelligence to transform physical environments into optimized, high-vibe, or high-ROI spaces—ranging from personal Zen dens to high-performance retail storefronts.

---

## 🚀 The Google Ecosystem Stack

Project Fama is built entirely on the **Google AI & Cloud Ecosystem**, utilizing specialized models for a seamless multimodal experience:

*   **Google Gemini 2.5 Flash (Multimodal Live API):** The "Brain" of Fama. It handles real-time voice and video interaction via WebSockets, allowing for natural, low-latency spatial analysis.
*   **Gemini 2.5 Flash Image:** The "Architect." It generates photorealistic, high-fidelity architectural blueprints and transformations while preserving the original structural geometry of your space.
*   **Google reCAPTCHA v3:** Enterprise-grade security to protect the API from bot abuse and ensure fair resource allocation.
*   **Vertex AI / Google AI SDK:** Orchestrates the complex interaction between vision analysis, persistent memory, and image generation.

---

## ✨ Key Features & Recent Improvements

### 🎙️ Multimodal Live Agent (Persistent & Stable)
*   **Voice-First Interaction:** Full-duplex WebSocket bridge to Google’s Multimodal Live API.
*   **IP-Based Memory:** Fama now remembers your conversation across WebSocket drops. The system re-injects the past 5 turns of context upon reconnection, ensuring a seamless consultation.
*   **Stability Overhaul:** Implemented 2.5s throttled reconnection logic and terminal error handling (1008/1011) to prevent infinite loops and CPU pegging.

### 🖼️ Precision Thematic Blueprinting
*   **Structural Integrity:** Utilizes image-to-image pipelines to ensure generated designs respect your room's actual walls, windows, and floor plan.
*   **Critical Proportion Rule:** Specialized prompt engineering ensures small items (like lamps or decor) are placed at a **realistic, true-to-life scale** rather than being enlarged to room-sized proportions.
*   **Refinement Loops:** Iterate on your design with follow-up voice commands to swap items or change themes.

### 🛋️ Guaranteed Affiliate Sourcing
*   **Zero-Failure Logic:** Implemented a robust Pydantic-validated fallback mechanism. If the AI fails to generate valid product JSON, Fama automatically serves a high-quality, 3-category curated catalog.
*   **3-Tier Pricing:** Every recommendation is split into **Budget, Mid-Range, and Premium** options.
*   **Direct Shopee Integration:** Clickable, high-converting links for immediate space upgrades.

### 📊 Advanced Space Diagnostics
Detailed, pun-infused reports on your space:
*   **Flow & Clarity:** Analysis of movement and spatial clutter.
*   **Circadian Lighting:** Optimized for mood and productivity.
*   **Feng Shui & Energy:** Holistic alignment and Chi balance.

---

## 🛠️ Stability & UX Polishing

*   **AI Thought Filtering:** Implemented aggressive regex sanitization to strip "internal monologue" tokens from the agent's responses, keeping the chat log clean and professional.
*   **Mic-Camera Sync:** Intelligently shuts down the camera feed whenever the microphone is toggled off to ensure user privacy and reduce bandwidth.
*   **Auto-Restart Recognition:** Fixed browser timeouts by auto-reinitializing speech recognition during active streams, ensuring your spoken words are always captured.
*   **Local Demo Bypass:** Streamlined testing by allowing a blank passcode for local development environments while maintaining strict security for production.

---

## 🛡️ Security & Architecture

*   **Zero-Trust Identity:** IP-based rate limiting and SHA-256 hashed passcode verification.
*   **Zero-Save Memory:** Uploaded images are processed in-RAM and streamed directly to Google Cloud. No user data is ever written to disk.
*   **Async Performance:** Refactored backend to be fully asynchronous (FastAPI + `aio` SDK), eliminating event-loop deadlocks during live streaming.

---

## 🛠️ Installation

1.  **Clone & Setup:**
    ```bash
    git clone https://github.com/your-repo/fama-live-agent.git
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Configure `.env`:**
    ```env
    GEMINI_API_KEY=your_key_here
    JUDGE_PASSCODE=secret_hash_here
    RECAPTCHA_SECRET_KEY=optional_security
    ```
3.  **Run:**
    ```bash
    uvicorn backend.main:app --reload
    ```

---

## 📖 Development Log
For a deep dive into the 50+ technical challenges overcome—from ASGI deadlock fixes to merchandising psychology—read the [JOURNAL.md](./JOURNAL.md).

**Built for the Google Gemini Live Agent Challenge.** 🏆
