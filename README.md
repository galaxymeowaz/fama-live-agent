# Project Fama: AI-Powered Holistic Space Optimizer 🏛✨

**Project Fama** is a multimodal spatial intelligence agent built for the **Google Gemini Live Hackathon**. Designed in a 36-hour solo sprint, Fama bridges the gap between expensive architectural consulting and DIY guesswork by transforming physical environments into optimized spaces while actively driving e-commerce affiliate revenue.

---

## 🎯 What is Fama?
Fama operates on two core product loops designed to solve spatial clutter and layout inefficiencies for B2C consumers and B2B retailers:

1. **Product A (The Visualizer):** A generative design engine. Users upload an image of a room and a physical product. Fama scales the item, applies custom themes, and renders a photorealistic architectural mockup while analyzing the room's Feng Shui, physical flow, and lighting.
2. **Product B (The Live Agent):** A real-time multimodal consultant. Using WebSockets, users show physical clutter to their webcam. Fama visually identifies the item, verbally advises on space-efficient storage, and instantly injects actionable, targeted affiliate links into the chat interface.

### 💰 Monetization Architecture
Fama is built as a commercially viable SaaS MVP with three revenue streams:
* **Affiliate Marketing:** Automated Shopee link injection during Live Agent chats.
* **Sponsored Placements:** B2B hardware brands pay a monthly SKU fee to have their exact products heavily weighted and forced into user-generated mockups.
* **Tiered Access:** Free (Ad-supported, watermarked), Silver (High-res, Feng Shui metrics), and Diamond (Unlimited matching, Cloud backup).

---

## ☁️ Cloud Architecture & The Stack
Fama evolved from a local script to a production-ready, serverless environment.

* **Infrastructure as Code (IaC):** HashiCorp Terraform
* **Containerization:** Docker (Debian/Python 3.11-slim)
* **Compute:** GCP Cloud Run (Serverless, Auto-scaling)
* **Backend:** Python (FastAPI, Uvicorn, WebSockets)
* **AI Integration:** Google Gemini 2.5 Flash (Native Audio) & Gemini 2.5 Flash Image
* **Frontend:** TailwindCSS & Vanilla JS

---

## 🔒 DevSecOps & Zero Trust
* **Secure by Design:** API keys and passcodes are strictly excluded from version control (`.gitignore`) and injected at runtime via GCP Environment Variables.
* **Rate Limiting:** In-memory request throttling to prevent DDoS and API billing spikes (FinOps).
* **Bot Mitigation:** Google reCAPTCHA v3 integrated for unauthenticated endpoint protection.
* **Access Control:** SHA-256 hashed passcode verification for premium AI tiers.

---

## 🛠 The 36-Hour Sprint: Challenges & Architecture
Built entirely from scratch by a solo developer over 1.5 days, Fama required aggressive architectural pivots:

1. **Serverless Containerization:** Overcame container crash loops by debugging Uvicorn port bindings and building graceful degradation fallbacks to ensure Cloud Run health checks pass even if secrets are delayed in the pipeline.
2. **API Exhaustion & FinOps:** Repeatedly hitting rate limits on generative models required engineering strict Spend Caps and building a pre-cached JSON fallback catalog to guarantee 100% demo uptime.
3. **WebSocket Deadlocks:** Aggressively re-engineered the LLM `system_prompt` to reduce cognitive latency, forcing the agent into a fast, reactive conversational loop to handle human interruption.
4. **Markdown Sanitization:** Built Python Regex middleware to sanitize JSON payloads before Pydantic validation to handle LLM markdown hallucinations.

---

## 💻 Deployment Pipelines

### Option A: Production Deployment (GCP)
The infrastructure is provisioned dynamically using Terraform, fetching the latest container image from Google Artifact Registry:
```bash
# 1. Build and push the container to Artifact Registry
docker build -t us-central1-docker.pkg.dev/[PROJECT_ID]/[REPO_NAME]/fama-app:latest .
docker push us-central1-docker.pkg.dev/[PROJECT_ID]/[REPO_NAME]/fama-app:latest

# 2. Provision Cloud Run services and IAM policies
terraform apply
```

### Option B: Local Development
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
    RECAPTCHA_SECRET_KEY=your_recaptcha_secret
    ```

3. **Run the FastAPI Server:**
    ```bash
    uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
    ```
    Access the UI at `http://127.0.0.1:8000`. Leave the "Demo Passcode" blank if testing on localhost.

---
**Author:** Galaxymeow A Z (Joseph Tay)
