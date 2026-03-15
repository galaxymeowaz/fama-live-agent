# Project Fama: Holistic Space & Retail Optimizer 🏛️✨

**Project Fama** is a premium, AI-driven spatial architect designed for the **Google Gemini Live Agent Challenge**. It leverages cutting-edge multimodal intelligence to transform physical environments into optimized, high-vibe, or high-ROI spaces—ranging from personal Zen dens and themed event venues to high-performance retail storefronts.

---

## 🚀 The Google Ecosystem Stack

Project Fama is built entirely on the **Google AI & Cloud Ecosystem**, utilizing specialized models for a seamless multimodal experience:

*   **Google Gemini 2.0 Flash (Multimodal Live API):** The "Brain" of Fama. It handles real-time voice interaction via WebSockets, allowing users to converse naturally while the agent analyzes their physical space.
*   **Vertex AI Imagen 3:** The "Architect." It generates photorealistic, high-fidelity architectural blueprints and transformations based on user vibes, uploaded photos, and refinement history.
*   **Google reCAPTCHA v3:** Enterprise-grade security to protect the API from bot abuse and ensure fair resource allocation.
*   **Vertex AI SDK for Python:** Orchestrates the complex interaction between vision analysis and image generation.

---

## ✨ Key Features

### 🎙️ Multimodal Live Agent
Interact with Fama via **Real-Time Voice**. The system uses a full-duplex WebSocket bridge to Google’s Multimodal Live API, enabling low-latency conversations and instant spatial feedback.

### 🖼️ Thematic Transformation (Blueprints)
Generate architectural renderings for your space across three primary modes:
*   **Personal:** Feng Shui, Astrology, and Ergonomically balanced home layouts.
*   **Events:** Total overhaul for specific themes (Wedding, Pirate, Space, Anime, etc.).
*   **B2B Commercial:** Retail psychology-driven layouts designed to maximize customer dwell-time and ROI.

### 📊 Space Diagnostics
Every generation includes a detailed diagnostic report:
*   **Flow Score:** Analysis of movement and spatial clutter.
*   **Lighting Score:** Circadian rhythm and mood optimization.
*   **Energy Score (Feng Shui):** Holistic balance and Chi alignment.

### 🛋️ Hand-Curated Affiliate Sourcing
Fama doesn't just design; it sources. Every blueprint comes with a **Good/Better/Best** tiered list of real-world products (Desks, Lighting, Seating) with direct links to improve your space immediately.

---

## 🛡️ Security & Zero Trust

Designed for public exposure, Fama implements several security layers:
*   **Zero-Trust Secret Management:** All API keys are handled via environment variables with strictly enforced startup checks.
*   **Rate Limiting:** IP-based sliding window quotas (15/hr for Judges, 10/hr for general testers).
*   **Passcode Gating:** Access is tiered via `JUDGE_PASSCODE` and `FRIEND_PASSCODE` for exclusive testing.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9+
*   Google Cloud Project with Vertex AI and Gemini Multi-modal Live API enabled.
*   A valid Google reCAPTCHA v3 Site/Secret key.

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/fama-live-agent.git
cd fama-live-agent
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
**Required Variables:**
*   `GEMINI_API_KEY`: Your Vertex AI / Google AI Studio Key.
*   `GOOGLE_APPLICATION_CREDENTIALS`: Path to your GCP Service Account JSON (if using Vertex).
*   `JUDGE_PASSCODE`: Set a secret code for evaluators.
*   `FRIEND_PASSCODE`: Set a secret code for casual testers.

### 5. Launch the Server
```bash
uvicorn backend.main:app --reload
```
The server will boot at `http://127.0.0.1:8000`. Open this URL in your browser to start optimizing your space!


---

## 📖 Journal & Development
Read the [JOURNAL.md](./JOURNAL.md) for a deep dive into the 30+ challenges overcome during development, from glassmorphic UI design to real-time audio pipeline buffering.

**Built for the Google Gemini Live Agent Challenge.** 🏆
