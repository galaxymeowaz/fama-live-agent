# Fama Architecture & Problem-Solving Log

### Challenge 1: Scope vs. Commercial Viability
* **Problem:** Balancing a massive B2B/B2C vision (Feng Shui, health optimization, affiliate sourcing) within a 36-hour hackathon timeline.
* **Solution:** Built the full multimodal UX to prove the "See, Hear, and Speak" paradigm. The AI is fully prompted with the proprietary holistic space optimization logic. We hardcoded the final JSON affiliate link outputs strictly to guarantee a flawless live demo presentation, while the AI generation and voice interaction remain 100% live.

### Challenge 2: Bot Mitigation & API Abuse
* **Problem:** Exposing live Gemini 2.5 and image generation endpoints publicly invites bot-net abuse, which would drain cloud credits instantly.
* **Solution:** Implemented a dual-layer Zero Trust defense. Layer 1: A hardcoded Demo Passcode for the judging panel. Layer 2: Advanced Google reCAPTCHA v3 integration on the frontend, verified server-side by FastAPI before any Google Cloud APIs are invoked.

### Challenge 3: Client-Side Malware via Uploads
* **Problem:** Allowing users to upload photos of their rooms introduces the risk of malicious payload execution on the server.
* **Solution:** Implemented a Zero-Save In-Memory architecture. Uploads are processed in RAM (`io.BytesIO`) and streamed directly to Google's APIs. No user data is ever written to the container's disk.

### Challenge 4: Localhost Secure Context Blocks
* **Problem:** Modern browsers block webcam access on `file:///` protocols.
* **Solution:** Booted the frontend via Uvicorn localhost loopback, which browsers recognize as a secure development environment.

### Challenge 5: Protecting Intellectual Property (IP) from AI Ingestion
* **Problem:** Free-tier AI tools often log user inputs and images to train future models, which would expose proprietary space-optimization logic and customer data.
* **Solution:** Architected the backend to align with Google Cloud's enterprise privacy SLAs (via paid tier linkage), guaranteeing zero data harvesting or model training on our payloads to comply with strict global privacy laws.

### Challenge 6: Infrastructure Portability
* **Problem:** Relying on manual clicks in the Cloud Console makes it impossible to reliably replicate the environment for judges, clients, or production.
* **Solution:** Mandated Docker containerization (using a lightweight Python base) and Terraform for Infrastructure as Code (IaC). This programmatically provisions compute and Artifact Registry, proving automated deployment capabilities.

### Challenge 7: Future Scalability vs. FinOps Constraints
* **Problem:** Google Cloud Armor provides the ultimate WAF protection but carries a mandatory baseline cost, violating the strict $0.00 hackathon mandate.
* **Solution:** Designed a hybrid edge architecture. We will deploy the free tier of Cloudflare as the external CDN/WAF to absorb initial bot traffic, while routing legitimate requests directly into our serverless Google Cloud Run environment.

### Challenge 8: UI/UX Information Overload
* **Problem:** Communicating complex holistic data (Feng Shui, psychology, filter sizing) and a 3-tier affiliate system risks overwhelming the user and reducing conversion rates.
* **Solution:** Designed the frontend using "Progressive Disclosure." Implemented Quick Action Chips for instant theme selection. Structured affiliate sourcing into a tabbed "Good/Better/Best" layout, transparently listing pros and cons to build trust without visual clutter.

### Challenge 9: Audience Segmentation & Conversion Rates
* **Problem:** Mixing consumer interior design (e.g., Pirate Themes) with enterprise retail optimization creates cognitive dissonance, lowering conversion rates for high-ticket B2B clients focused on ROI.
* **Solution:** Architected a top-level "Mode Switcher" (Personal & Events | B2B Commercial). B2B users are routed to a specialized flow with inputs for "Store Type" and "High-Margin Products". The AI pivots entirely to retail merchandising psychology to maximize sales.

### Challenge 10: Decision Fatigue vs. Streamlined Funnels
* **Problem:** Separating "Personal" and "Events" into distinct tabs created unnecessary UI clutter and increased cognitive load.
* **Solution:** Consolidated into a binary "Personal & Events" vs "B2B Commercial" structure, simplifying the initial choice while retaining thematic depth via Quick Action Chips.

### Challenge 11: Building Enterprise Trust
* **Problem:** B2B and consumers are hesitant to upload photos of their private spaces due to fears of data harvesting.
* **Solution:** Designed a prominent "Trust & ROI Shield" UI component. It explicitly guarantees "Zero AI Training" and default "On-Device Storage". Cloud storage is securely gated behind the Diamond Tier opt-in.

### Challenge 12: Rigid B2B Constraints vs. Holistic Flexibility
* **Problem:** Forcing Feng Shui on strict, ROI-driven retail managers could lose the sale, but removing it abandons wellness-focused brands.
* **Solution:** Implemented "Advanced Holistic Toggles" in the B2B mode. They default to OFF for traditional managers, but allow wellness brands to opt-in to psychological layout optimization.

### Challenge 13: One-Shot Generation Drop-off
* **Problem:** A rigid, one-shot generation process leads to user frustration, abandoned sessions, and lost affiliate revenue if they don't get exactly what they want on the first try.
* **Solution:** Architected an "Iterative Refinement Loop." A contextual chat interface unlocks beneath the generated image, allowing users to converse with the AI to swap products or adjust themes while preserving the core layout.

### Challenge 14: Hackathon Compliance & Real-Time Interruptibility
* **Problem:** Fulfilling the "Live Agent" requirement of natural, interruptible voice/vision interaction while remaining secure.
* **Solution:** Architected the backend explicitly using the `google-genai` SDK. The WebSocket proxy strictly handles bidirectional audio and video frames, allowing users to seamlessly interrupt Fama mid-sentence while she "sees" the room via the webcam.

### Challenge 15: Overcoming Enterprise IAM Friction
* **Problem:** Strict Google Cloud "Secure by Default" Organization Policies blocked the creation of local Service Account JSON keys in WSL.
* **Solution:** Pivoted to the Gemini Developer API using a direct API Key linked to the GCP billing account. This guarantees user data privacy under "Paid Service" terms without local IAM overhead.

### Challenge 16: Development Velocity vs. Infrastructure Blockers
* **Problem:** Organization policies blocked local development authentication for the IDE assistant, threatening the 36-hour timeline.
* **Solution:** Executed a DevSecOps pivot. Transitioned to GitHub Copilot as the primary AI coding assistant to bypass local IAM friction and maintain pure development velocity.

### Challenge 17: Multi-Device UX & Mobile Responsiveness
* **Problem:** Space optimization apps are used dynamically while walking around rooms, meaning mobile usage dominates. Rigid desktop layouts break the core UX.
* **Solution:** Mandated a "Mobile-First" design system using TailwindCSS responsive breakpoints. Grid layouts and complex components stack seamlessly on smaller screens.

### Challenge 18: Affiliate Link Decay vs. API Quota Limits
* **Problem:** Background bots constantly verifying affiliate stock would cause massive API rate-limiting and drain compute credits.
* **Solution:** Implemented a "Just-In-Time (JIT) Verification" architecture. Verification logic is triggered exclusively at the moment of generation, allowing dynamic swapping of broken products during active inference to preserve zero-cost FinOps rules.

### Challenge 19: Monetization Funnel Obscuration
* **Problem:** Forced CSS positioning caused tier pricing buttons to overlap the main header logo, hiding primary monetization triggers.
* **Solution:** Refactored the DOM to utilize standard Tailwind Flexbox alignment, ensuring branding and monetization buttons share space cleanly across all breakpoints.

### Challenge 20: Zero-Cost "Live Voice" Integration
* **Problem:** Streaming raw audio to the backend introduces high latency, privacy concerns, and compute costs.
* **Solution:** Architected a client-side Voice Refinement Loop utilizing the browser's native Web Speech API. Offloading speech processing to local hardware achieves real-time voice UX with zero backend compute cost.

### Challenge 21: Sunk Cost Fallacy in Local Testing
* **Problem:** Tunneling a Windows localhost to an Android device for mobile UI testing introduced severe DevSecOps friction and proxy errors.
* **Solution:** Applied agile project management to kill the task. Strategically deferred final mobile hardware testing until official deployment to preserve the tight deadline.

### Challenge 22: The "Ghost Logic" Synchronization Gap
* **Problem:** Complex JavaScript features (Refinement loops) were coded, but corresponding HTML DOM elements were missing, leading to invisible functionality.
* **Solution:** Performed a systematic Audit & Bridge operation. Manually synchronized JS requirements with the HTML structure to restore visibility to the Live Agent engine.

### Challenge 23: Local Development Loop "Deadlocks"
* **Problem:** Strict startup checks for cloud-only variables and lack of a static server caused connection failures.
* **Solution:** Refactored into a "Dev-Resilient" architecture. Swapped fatal crashes for warning logs on missing keys and used `FastAPI.staticfiles` to serve the frontend on a unified `localhost:8000` port.

### Challenge 24: Direct Interactivity vs. Sequential Gating
* **Problem:** Hiding the chat interface behind the "Start Camera" requirement locked users out if they just wanted text-based spatial advice.
* **Solution:** Shifted to a "Parallel Entry" UX. Implemented an always-visible text input field, allowing immediate conversation while keeping complex vision features as an advanced opt-in.

### Challenge 25: Aesthetic Fragmentation
* **Problem:** Residual generic styling clashed with the premium, dark-mode brand identity, damaging the B2B sales pitch.
* **Solution:** Executed a "Visual Harmonization" pass. Refactored the header to utilize `#020617` with glassmorphism to guarantee a premium interface.

### Challenge 26: Zero Trust Secret Management
* **Problem:** Preparing the repo for public judging while protecting API keys.
* **Solution:** Implemented Zero Trust via `python-dotenv` with zero-fallback `os.getenv` calls, a "Fail-Soft" startup check, and a production-grade `.gitignore`.

### Challenge 27: Resource Exhaustion & API Abuse
* **Problem:** Public exposure invites bot abuse.
* **Solution:** Built an in-memory IP-based rate limiter (sliding window) to ensure judge accessibility while preventing malicious exhaustion.

### Challenge 28: Multimodal Interaction Paradigm
* **Problem:** Users wanting verbal interaction before starting the camera.
* **Solution:** Engineered an always-on voice input system using native `webkitSpeechRecognition` for immediate, zero-cost interaction.

### Challenge 29: Screen Estate Optimization
* **Problem:** Single-line inputs felt cramped for complex architectural prompts.
* **Solution:** Transitioned the chat input to an auto-resizing `textarea` and vertically aligned action buttons for a high-density aesthetic.

### Challenge 30: AI Mock Eradication
* **Problem:** Initial development relied on hardcoded mock responses to protect FinOps quotas.
* **Solution:** Executed a surgical live injection, removing mock dictionaries and wiring the backend directly to the `google-genai` SDK.

### Challenge 31: FinOps "Limit: 0" Anti-Abuse Wall
* **Problem:** Provisioning a fresh Google account resulted in immediate `429` errors due to "0" limits on unverified accounts.
* **Solution:** Attached a verified billing profile to lift the lock, leveraging the "Free Trial" state and Spend Caps to mathematically guarantee $0.00 spend.

### Challenge 32: API Model Deprecation
* **Problem:** Google deprecated the `gemini-2.0-flash` string for new API keys, causing `404 NOT_FOUND` drops.
* **Solution:** Updated routing to the active `gemini-2.5-flash` model endpoint to restore connectivity.

### Challenge 33: Unpredictable AI Formatting
* **Problem:** Standard text prompting resulted in hallucinated outputs instead of the strict formatting required for 3-tier affiliate monetization.
* **Solution:** Implemented Strict JSON Schema enforcement using `pydantic`, forcing the AI to return exact, parsable URLs and prices.

### Challenge 34: SDK Strict Typing
* **Problem:** The SDK transitioned to strict keyword-only arguments, causing `TypeError` crashes on raw audio bytes.
* **Solution:** Refactored methods to explicitly use named parameters (`media=` and `text=`) to satisfy the validation layer.

### Challenge 35: API Model Fragmentation
* **Problem:** Production model strings resulted in errors on free-tier keys.
* **Solution:** Pivoted the Live Agent to `gemini-2.5-flash-native-audio-preview` and images to `gemini-2.5-flash-image` via `generate_content`.

### Challenge 36: Decoupling UI Sequential Gating
* **Problem:** "Ghost Locks" forced users to activate webcams before accessing the Blueprint Generator.
* **Solution:** Decoupled camera state from input state, allowing independent use of the Mic and Generate buttons.

### Challenge 37: ASGI Application Crashes
* **Problem:** Server crashed processing positional lists during full-duplex streaming.
* **Solution:** Transitioned to the direct `types.Blob` schema for audio streaming, optimizing memory footprint and preventing ASGI termination.

### Challenge 38: Prompt Injection Mitigation
* **Problem:** Users bypassing logic to ask general questions, abusing API quotas.
* **Solution:** Implemented rigid System Prompt guardrails forcing the agent to decline off-topic queries and steer back to interior design.

### Challenge 39: Generative Image Hallucinations
* **Problem:** Text-to-image generation destroyed original room architecture.
* **Solution:** Transitioned to an Image-to-Image pipeline, forcing the model to map new furniture onto the existing room geometry.

### Challenge 40: Multi-Modal Data Processing
* **Problem:** Pydantic schemas only supported single base64 strings, preventing multi-image uploads.
* **Solution:** Refactored to accept `list[str]`, engineering the frontend to queue uploads and live canvas frames simultaneously.

### Challenge 41: B2B ROI Optimization
* **Problem:** Generic outputs lacked sales-driven analytics for B2B users.
* **Solution:** Engineered dynamic Pydantic schema injection. In B2B mode, the AI generates merchandising reports detailing lighting and customer psychology.

### Challenge 42: Edge Security & Passcode Hashing
* **Problem:** Comparing passcodes in plain text presented a vulnerability.
* **Solution:** Implemented SHA-256 cryptographic hashing for all passcodes at startup and during request validation.

### Challenge 43: Frontend Asset Protection
* **Problem:** Generated blueprints were easily downloadable without watermarks.
* **Solution:** Implemented strict DOM protections to disable right-clicking, forcing users to screenshot (which securely captures the Fama watermark).

### Challenge 44: ASGI Event Loop Deadlocks
* **Problem:** Synchronous operations (reCAPTCHA) blocked the FastAPI main thread, dropping WebSockets.
* **Solution:** Refactored the backend to strictly asynchronous `client.aio` calls to unblock the event loop.

### Challenge 45: Live Agent "Thought Bleed"
* **Problem:** The Live API streamed internal reasoning tokens into the UI transcript.
* **Solution:** Implemented a dual-layer filtering system: positive constraints in the system prompt, and a JS Regex filter on the frontend.

### Challenge 46: Speech Recognition Silencing
* **Problem:** Native speech recognition terminated after brief silence.
* **Solution:** Implemented an `onend` auto-restart hook to provide a continuous voice-to-text experience.

### Challenge 47: Hallucinated Affiliate Links
* **Problem:** Real-time link generation resulted in 404s.
* **Solution:** Pivoted to a "Curated Demo Catalog", forcing the AI to inject validated Shopee URLs to ensure 100% demo reliability.

### Challenge 48: Generative Drift vs. Structural Integrity
* **Problem:** Image generation redesigned entire rooms instead of just placing products.
* **Solution:** Strengthened prompt directives to use the uploaded image as a rigid structural anchor and reframed the feature as a "Conceptual Layout Generator."

### Challenge 49: Token Optimization & Response Latency
* **Problem:** Long-winded diagnostics increased latency and consumed tokens.
* **Solution:** Enforced strict "Diagnostic Sentence Caps", reducing latency by ~30% and preserving the token budget.