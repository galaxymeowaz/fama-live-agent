# Project: Fama (Holistic Space Optimizer)
# Target: Google Gemini Live Agent Hackathon Submission (Targeting Category 1: Live Agents)

## 1. Core Architecture & DevSecOps (Hackathon Compliance)
* **Mandatory SDK:** The Python backend MUST exclusively use the official `google-genai` SDK for Gemini Live API connections.
* **Hosting Container:** Docker (multi-stage build for a lightweight image).
* **Cloud Infrastructure (Terraform):** Google Artifact Registry to store the Docker image, and Google Cloud Run (Serverless) for compute. This fulfills the mandatory Google Cloud service requirement.
* **Security (Bot Mitigation):** Cloudflare WAF routing to Google Cloud Run. Frontend utilizes Google reCAPTCHA v3.
* **Security (Data Protection):** Strict In-Memory processing. NO files are ever saved to the disk.
* **Authentication:** Hardcoded `DEMO_PASSCODE` required for MVP judging access.

## 2. The AI Agent Persona (Category 1 Focus: Interruptible Live Agent)
* **Role:** You are the Fama Holistic Space & Retail Optimizer. You engage in real-time, interruptible voice conversations using the user's live camera feed. 
* **Domains:** * **Personal & Events:** Home design, Fengshui, Astrology. Thematic setups (Birthday Parties, Weddings, Proposals, Pirate, Space, Anime).
  * **B2B Commercial (Shop Optimization):** Merchandising psychology, layout flows to maximize customer spend, psychological lighting, strategic placement of high-margin items. Optional integration of Fengshui and Health psychology if requested.
* **Constraint:** Cite credible sources for all health, airflow, Fengshui, and retail psychology recommendations. Gracefully handle user voice interruptions and instantly pivot the conversation context.

## 3. Frontend UI & Business Logic (Progressive Disclosure & Trust)
The UI must remain uncluttered, utilizing Progressive Disclosure and strict Audience Segmentation:
* **Mobile-First Responsiveness:** The entire UI must utilize Tailwind's responsive breakpoints (`md:`, `lg:`) to ensure seamless scaling. All flex/grid layouts must collapse gracefully on mobile screens, ensuring no horizontal scrolling, overlapping text, or layout glitches.
* **Master Mode Switcher:** 2 distinct tabs: [Personal & Events] | [B2B Commercial].
  * *Personal & Events Mode:* Shows "Desired Vibe" input and Quick Action Chips (Birthday, Wedding, Proposal, Pirate, Space, Feng Shui).
  * *B2B Commercial Mode:* Shows inputs for "Store Type" and "High-Margin Products". Includes **"Advanced Holistic Toggles"** (Feng Shui / Health Psychology) defaulting to OFF.
* **Iterative Refinement Loop (Post-Generation):** Once a blueprint is generated, a contextual chat input appears below the results. It includes small UI tips. Users can type refinement requests to update the image or the product links without losing previous context.
* **Business Tiers (3-Way Toggle):**
  * Free Tier: Heavy Fama watermarks, generic Google Ads, max 5 product links. Local device storage only.
  * Silver Tier: Fengshui/Psychology metrics, detailed airflow/retail citation reports, extensive sourcing links. Local device storage only.
  * Diamond Tier: Zero ads, secure Cloud Storage integration for cross-device access, 1-click export.
* **Trust & ROI Shield (UI Banner):** A dedicated visual section explaining the Fama Promise: "Zero AI Model Training," "100% On-Device Data," and "Data-Driven ROI & Productivity Boosts for Business." Friendly but professional tone.
* **Value Prop Tooltips:** Minimalist UI elements explaining holistic/retail benefits.

## 4. Execution Pipeline (/generate_blueprint)
1. Verify Google reCAPTCHA v3 token and DEMO_PASSCODE.
2. **Context Awareness:** The endpoint must accept an optional `conversation_history` array to process follow-up refinements.
3. Call Vertex AI `imagen-3.0-fast-generate-001` using the vibe text, image context, and refinement instructions.
4. Return the generated Base64 image and a structured JSON list of affiliate products.
5. **Product Sourcing & JIT Verification Logic:** * The system executes Just-In-Time (JIT) logic: at the moment of generation, the AI is instructed to only return products assumed to be currently in-stock, avoiding background scraping costs.
   * The mocked JSON structures products into three pricing tiers:
     * **Budget:** Cheap, highly functional, specific tradeoffs (e.g., "Shorter lifespan").
     * **Mid-Range:** Balanced aesthetics and durability, slight cost increase.
     * **Premium:** High-end, maximum benefits, premium price.

## 5. Infrastructure as Code & Containerization Tasks
* **Dockerfile:** Create a production-ready `Dockerfile` that runs the FastAPI Uvicorn server on port 8000.
* **Terraform:** Create a `terraform/main.tf` file that configures the Google provider, creates a Google Artifact Registry repository, and provisions a Google Cloud Run service.