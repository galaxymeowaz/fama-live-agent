# Project Fama: AI-Powered Holistic Space Optimizer 🏛✨

**Project Fama** is a multimodal spatial intelligence agent built for the **Google Gemini Live Hackathon**. Designed in a 36-hour solo sprint, Fama bridges the gap between expensive architectural consulting and DIY guesswork by transforming physical environments into optimized spaces while actively driving e-commerce affiliate revenue.

---

## 🎯 What is Fama?
Fama operates on two core product loops designed to solve spatial clutter and layout inefficiencies for B2C consumers and B2B retailers:

1. **Product A (The Visualizer):** A generative design engine. Users upload an image of a room and a physical product. Fama scales the item, applies custom themes (e.g., "Minimalist Zen", "Pirate Cats"), and renders a photorealistic architectural mockup while analyzing the room's Feng Shui, physical flow, and lighting.
2. **Product B (The Live Agent):** A real-time multimodal consultant. Using WebSockets, users show physical clutter to their webcam. Fama visually identifies the item, verbally advises on space-efficient storage, and instantly injects actionable, targeted affiliate links into the chat interface.

### 💰 Monetization Architecture
Fama is built as a commercially viable SaaS MVP with three revenue streams:
* **Affiliate Marketing:** Automated Shopee link injection during Live Agent chats.
* **Sponsored Placements:** B2B hardware/furniture brands pay a $10/month/SKU fee to have their exact products heavily weighted and forced into user-generated mockups.
* **Tiered Access:** Free (Ad-supported, watermarked), Silver (High-res, Feng Shui metrics), and Diamond (Unlimited matching, Cloud backup).

---

## 🚀 The Stack & Google Ecosystem
* **Google Gemini 2.5 Flash (Native Audio):** The conversational brain. Handles real-time, interruptible voice and video processing via WebSockets.
* **Gemini 2.5 Flash Image:** The visualizer. Generates scale-aware architectural blueprints while preserving original room geometry.
* **FastAPI & Python:** High-concurrency backend routing and state-machine management.
* **TailwindCSS & Vanilla JS:** Lightweight, zero-dependency frontend multiplexing audio/video streams.

---

## 🧪 Reproducible Testing (For Judges)
To evaluate the core hackathon requirements, follow these exact test protocols:

### Test 1: Live Agent & Interruption Recovery (WebSocket)
1. Open the UI and click the **Microphone** button to connect to Fama.
2. **The Vision Test:** Turn on the camera, hold a physical item (e.g., a mug or book) up to the lens, and ask, "How should I store this?" Fama will identify the item and ask if you want a product link.
3. **The Affiliate Drop:** Reply "Yes". Fama will verbally confirm and push a clickable `https://sg.shp.ee/` link into the chat UI.
4. **The Interruption Test:** Ask Fama to explain Feng Shui. While she is speaking, interrupt her by saying, "Wait, change the topic." The LLM state-machine is engineered to halt audio playback instantly and pivot without deadlocking.

### Test 2: Generative Blueprint & FinOps Fallback (REST API)
1. Scroll down to the Generation Params.
2. Enter a custom vibe (e.g., "Cyberpunk Office").
3. Click **Generate Optimized Blueprint**.
4. **DevSecOps Fallback:** If the Free Tier API limits are exhausted, the backend mathematically guarantees a UI render by intercepting the `429` error, stripping LLM Markdown hallucinations, and forcing the sponsored product links into the dashboard.

---

## 🛠 The 36-Hour Sprint: Challenges & Architecture
Built entirely from scratch by a solo developer over 1.5 days, Fama required aggressive architectural pivots:

1. **API Exhaustion & FinOps:** Repeatedly hitting rate limits on generative models required engineering strict Spend Caps and building a pre-cached JSON fallback catalog to guarantee 100% demo uptime.
2. **WebSocket Deadlocks:** The Live AI initially froze when interrupted by natural human speech. I aggressively re-engineered the LLM `system_prompt` to reduce cognitive latency, forcing the agent into a fast, reactive conversational loop.
3. **Markdown Sanitization:** Generative models often wrap URLs in Markdown `[link](url)`, breaking frontend routing. I built Python Regex middleware to sanitize JSON payloads before Pydantic validation.

---

## 💻 Installation & Local Deployment

1. **Clone & Setup:**
    ```bash
    git clone [https://github.com/galaxymeowaz/fama-live-agent.git](https://github.com/galaxymeowaz/fama-live-agent.git)
    cd fama-live-agent
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Configure Environment:** Create a `.env` file in the root directory.
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    JUDGE_PASSCODE=your_custom_passcode
    FRIEND_PASSCODE=your_custom_passcode
    ```

3. **Run the FastAPI Server:**
    ```bash
    uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
    ```
4. Access the UI at `http://127.0.0.1:8000`. Leave the "Demo Passcode" blank if testing on localhost.

---
**Author:** Galaxymeow A Z (Joseph Tay)