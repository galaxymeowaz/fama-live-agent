import os
import io
import json
import base64
import time
import collections
import urllib.request
import urllib.parse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# In-Memory Rate Limiter (zero-cost, resets on restart — intentional)
# ---------------------------------------------------------------------------
class RateLimiter:
    """Sliding-window IP rate limiter using only stdlib."""
    def __init__(self):
        self._windows: dict[str, collections.deque] = collections.defaultdict(collections.deque)

    def is_allowed(self, key: str, max_calls: int, window_seconds: int) -> bool:
        now = time.monotonic()
        dq = self._windows[key]
        # Evict timestamps outside the window
        while dq and dq[0] < now - window_seconds:
            dq.popleft()
        if len(dq) >= max_calls:
            return False
        dq.append(now)
        return True

rate_limiter = RateLimiter()


load_dotenv()  # Load .env before accessing environment variables

# ---------------------------------------------------------------------------
# Zero Trust Startup Validation — server REFUSES to boot if secrets are missing
# ---------------------------------------------------------------------------
_REQUIRED_SECRETS = {
    "GEMINI_API_KEY":   os.getenv("GEMINI_API_KEY"),
    "JUDGE_PASSCODE":   os.getenv("JUDGE_PASSCODE"),
    "FRIEND_PASSCODE":  os.getenv("FRIEND_PASSCODE"),
}

_missing = [k for k, v in _REQUIRED_SECRETS.items() if not v]
if _missing:
    raise RuntimeError(
        f"\n\n[FAMA STARTUP FAILURE] The following required environment variables are not set:\n"
        f"  {', '.join(_missing)}\n\n"
        f"Copy .env.example to .env and fill in your real values before starting the server.\n"
    )

GEMINI_API_KEY  = _REQUIRED_SECRETS["GEMINI_API_KEY"]
JUDGE_PASSCODE  = _REQUIRED_SECRETS["JUDGE_PASSCODE"]
FRIEND_PASSCODE = _REQUIRED_SECRETS["FRIEND_PASSCODE"]

print("--- SYSTEM CHECK: All required secrets loaded. Server is authorised to boot. ---")

# Optional secrets (degraded-mode if missing, non-fatal)
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
GCP_PROJECT_ID       = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION         = os.getenv("GCP_LOCATION", "us-central1")

if not RECAPTCHA_SECRET_KEY:
    print("WARNING: RECAPTCHA_SECRET_KEY not set — reCAPTCHA verification will be skipped.")
if not GCP_PROJECT_ID:
    print("WARNING: GCP_PROJECT_ID not set — Vertex AI image generation will be mocked.")

# Optional Vertex AI import (assumes google-cloud-aiplatform is installed if fully executing)
try:
    import vertexai
    from vertexai.preview.vision_models import ImageGenerationModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

if VERTEX_AVAILABLE and GCP_PROJECT_ID:
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
    except Exception as e:
        print(f"Vertex AI Init Error: {e}")


app = FastAPI(title="Project Fama - Holistic Space Optimizer API")

# Serve the frontend/index.html as static files at the root
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Serve frontend — localhost:8000/ and /index.html will open index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/index.html")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

class BlueprintRequest(BaseModel):
    recaptcha_token: str
    passcode: str
    tier: str
    master_mode: str = "personal"
    vibe: str = ""
    store_type: str = ""
    high_margin_products: str = ""
    apply_feng_shui: bool = False
    apply_health_psychology: bool = False
    image_base64: str = "" # Optional initial room image
    conversation_history: list = None

def verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY:
        print("Skipping reCAPTCHA verification — RECAPTCHA_SECRET_KEY not configured.")
        return True

    url = "https://www.google.com/recaptcha/api/siteverify"
    data = urllib.parse.urlencode({
        "secret": RECAPTCHA_SECRET_KEY,
        "response": token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("success", False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Rate limit: 5 WebSocket connections per IP per 10 minutes
    client_ip = websocket.client.host if websocket.client else "unknown"
    if not rate_limiter.is_allowed(f"ws:{client_ip}", max_calls=5, window_seconds=600):
        await websocket.close(code=1008, reason="Rate limit exceeded. Please wait before reconnecting.")
        print(f"WebSocket rate limit hit for IP: {client_ip}")
        return
    await websocket.accept()
    print(f"Client connected to WebSocket: {client_ip}")
    
    # System Instructions for the agent enforcing the Fama Holistic Space Optimizer persona
    persona_instructions = """
    You are the Fama Holistic Space & Retail Optimizer.
    Domains:
    - Personal Spaces: Home design, Fengshui (positive/improvement-focused), Astrology.
    - Events: Thematic setups (Weddings, Proposals, Birthdays, Pirate, Anime).
    - B2B Commercial (Shop Optimization): Merchandising psychology, store layout flows to maximize customer spend, psychological lighting (e.g., cool vs. warm lighting for dwell time), strategic placement of high-margin items.
    Constraint: Cite credible sources for all health, airflow, Fengshui, and retail psychology recommendations.
    """
    
    try:
        while True:
            data = await websocket.receive_bytes()
            in_memory_stream = io.BytesIO(data)
            
            # Mock processing for WebSocket using strict In-Memory constraints
            response_data = {
                "message": "Assessing spatial layout for Fengshui and ergonomic improvements... (Persona: Fama Holistic Space Optimizer active)",
                "status": "success"
            }
            await websocket.send_text(json.dumps(response_data))
            
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error in WebSocket: {e}")

@app.post("/generate_blueprint")
async def generate_blueprint(req: BlueprintRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    # 0. Passcode validation — NO access without a valid code
    is_judge  = req.passcode == JUDGE_PASSCODE
    is_friend = req.passcode == FRIEND_PASSCODE
    if not is_judge and not is_friend:
        raise HTTPException(
            status_code=403,
            detail="Access denied. A valid passcode is required to use Fama."
        )

    # 0b. Rate limiting — judges: 15/hr | friends: 10/hr
    blueprint_limit = 15 if is_judge else 10
    if not rate_limiter.is_allowed(f"blueprint:{client_ip}", max_calls=blueprint_limit, window_seconds=3600):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit reached ({blueprint_limit} blueprints/hr). Please wait and try again."
        )

    # 1. Verify Google reCAPTCHA v3 token
    if not verify_recaptcha(req.recaptcha_token):
        raise HTTPException(status_code=403, detail="reCAPTCHA verification failed")
        
    # 3. Call Vertex AI imagen-3.0-fast-generate-001
    generated_image_b64 = ""
    try:
        if VERTEX_AVAILABLE:
            model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")
            # Build prompt with iterative refinement
            if req.conversation_history:
                # Use last user refinement as edit instruction
                last_refine = req.conversation_history[-1]["content"] if isinstance(req.conversation_history[-1], dict) else str(req.conversation_history[-1])
                if req.master_mode == "b2b":
                    prompt = f"Edit the previous commercial space blueprint for a {req.store_type}. User refinement: '{last_refine}'. Adjust layout, products, or lighting as requested."
                else:
                    prompt = f"Edit the previous room blueprint. Vibe/Theme: {req.vibe}. User refinement: '{last_refine}'. Adjust layout, products, or lighting as requested."
            else:
                if req.master_mode == "b2b":
                    prompt = f"Interior design of a {req.store_type} commercial space. Focus on highlighting these high-margin products: {req.high_margin_products}. High quality, retail merchandising architectural rendering."
                    if req.apply_feng_shui:
                        prompt += " Integrate Feng Shui principles for optimal flow and energy."
                    if req.apply_health_psychology:
                        prompt += " Utilize psychological lighting and layout factors that promote mental health and reduce stress."
                else:
                    theme = req.vibe or "modern minimalist"
                    # Theme-specific decoration lookup for prompt adherence
                    theme_items = {
                        "wedding": "white floral arches, rose petal aisle, ivory draped fabric, candlelit centrepieces, fairy-light canopy",
                        "birthday": "colourful balloon arch, festive streamers, party banner, tiered cake table, confetti floor",
                        "proposal": "rose petal trail, warm candles, soft red silk fabric, intimate fairy lights, champagne setting",
                        "pirate": "treasure chests, ship wheel, hanging rope nets, lanterns, parchment maps, cannon props",
                        "space": "holographic galaxy projections, metallic silver furniture, floating planet decorations, LED star ceiling, zero-gravity pod chairs",
                        "feng shui": "bamboo plants, water feature, natural wood elements, clear unobstructed pathways, warm earth tones",
                    }
                    decorations = theme_items.get(theme.lower().strip(), f"{theme}-inspired decorative elements, matching colour palette, thematic props")
                    prompt = (f"INTERIOR DESIGN TRANSFORMATION: Transform this room into a stunning {theme} venue. "
                              f"MANDATORY decorative elements: {decorations}. "
                              f"Maintain the original room dimensions and structure but completely overhaul all aesthetics. "
                              f"Photorealistic, high-resolution 16:9 architectural rendering. "
                              f"Every surface, fixture, and furnishing must reflect the {theme} theme.")
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9"
            )
            if response.images:
                img_bytes = response.images[0]._image_bytes
                generated_image_b64 = base64.b64encode(img_bytes).decode('utf-8')
        else:
            print("Vertex AI SDK not available or configured. Using mock Base64 image.")
            generated_image_b64 = "MOCK_BASE64_IMAGE_DATA"
    except Exception as e:
        print(f"Imagen generation error: {e}")
        generated_image_b64 = "MOCK_BASE64_IMAGE_DATA_ERROR"
        
    # 4. Return data based on Business Tier
    
    tier = req.tier.lower()
    
    # Base mocked vendor data structured into 3 pricing tiers
    vendor_data = [
        {
            "category": "Workspace Foundation",
            "reasoning": "Improves posture and aligns with health optimization goals.",
            "budget": {
                "item": "Flexispot E1 Basic Sit-Stand Desk",
                "price": "$199.00",
                "vendor": "Flexispot Official",
                "pros": "Entry-level electric standing desk, stable frame.",
                "cons": "Single motor, limited height range.",
                "url": "https://www.flexispot.com/electric-height-adjustable-standing-desk-e1"
            },
            "mid_range": {
                "item": "Uplift V2 Standing Desk",
                "price": "$549.00",
                "vendor": "Uplift Desk",
                "pros": "Industry-leading stability, 5-year warranty.",
                "cons": "Shipping time can be lengthy.",
                "url": "https://www.upliftdesk.com/uplift-v2-standing-desk-v2"
            },
            "premium": {
                "item": "Herman Miller Motia Sit-to-Stand",
                "price": "$1,295.00",
                "vendor": "Herman Miller",
                "pros": "Whisper-quiet dual motors, 12-year warranty.",
                "cons": "Very high upfront investment.",
                "url": "https://www.hermanmiller.com/products/tables/sit-to-stand-tables/motia-sit-to-stand-tables/"
            }
        },
        {
            "category": "Circadian Lighting",
            "reasoning": "Adjustable colour temperature syncs with circadian rhythms. [Source: Sleep Foundation]",
            "budget": {
                "item": "TP-Link Tapo Smart Bulb L530",
                "price": "$12.99",
                "vendor": "Amazon",
                "pros": "Easy setup, full RGB + tunable white.",
                "cons": "Requires 2.4GHz Wi-Fi.",
                "url": "https://www.amazon.com/dp/B08LYS1XSK"
            },
            "mid_range": {
                "item": "Govee Floor Lamp (RGBIC)",
                "price": "$89.99",
                "vendor": "Govee Official",
                "pros": "Multi-colour segments, 16 million colours, app-controlled.",
                "cons": "Requires Govee Home app.",
                "url": "https://www.govee.com/products/govee-floor-lamp-2"
            },
            "premium": {
                "item": "Philips Hue Gradient Signe Floor Lamp",
                "price": "$259.99",
                "vendor": "Philips Hue",
                "pros": "Entertainment sync, highest CRI, Matter compatible.",
                "cons": "Requires Hue Bridge.",
                "url": "https://www.philips-hue.com/en-us/p/hue-white-and-color-ambiance-gradient-signe-floor-lamp/4080148U7"
            }
        }
    ]

    # Iterative refinement: mock product swap if user requests
    if req.conversation_history:
        last_refine = req.conversation_history[-1]["content"] if isinstance(req.conversation_history[-1], dict) else str(req.conversation_history[-1])
        # Example: swap desk for cheaper one
        if "swap desk for a cheaper" in last_refine.lower() or "budget desk" in last_refine.lower():
            vendor_data[0]["premium"] = vendor_data[0]["budget"]
            vendor_data[0]["mid_range"] = vendor_data[0]["budget"]
        if "change the lighting to warm white" in last_refine.lower():
            vendor_data[1]["budget"]["item"] = "Warm White LED Bulb"
            vendor_data[1]["budget"]["pros"] = "Simple warm white, easy on eyes."
            vendor_data[1]["mid_range"]["item"] = "Yeelight Warm White Bulb"
            vendor_data[1]["mid_range"]["pros"] = "Smart warm white, reliable."
            vendor_data[1]["premium"]["item"] = "Philips Hue Warm White Kit"
            vendor_data[1]["premium"]["pros"] = "Premium warm white, highest CRI."
    
    # Customize payload based on tier
    if tier == "free":
        vendor_data = vendor_data[:1] # 1 category for free tier
        metrics = {
            "flow": "Flow Score: 62/100 — Moderate. One pathway partially blocked.",
            "lighting": "Lighting Score: 70/100 — Adequate. Recommend warmer hue for relaxation zones.",
            "energy": "Energy Score: 55/100 — Neutral Chi. Desk faces auspicious direction."
        }
    elif tier == "silver":
        vendor_data.append({
            "category": "Air Quality / Flow",
            "reasoning": "Optimal airflow placement and filtration. [Source: WHO Air Quality Guidelines]",
            "budget": {
                "item": "Levoit Core 300 Air Purifier",
                "price": "$99.99",
                "vendor": "Amazon",
                "pros": "Compact, quiet 360° air intake, True HEPA.",
                "cons": "Small room coverage up to 219 sq ft.",
                "url": "https://www.amazon.com/dp/B07VVK39F7"
            },
            "mid_range": {
                "item": "Xiaomi Smart Air Purifier 4",
                "price": "$180.00",
                "vendor": "Xiaomi Official",
                "pros": "Excellent CADR, real-time AQI tracking.",
                "cons": "Frequent filter replacements.",
                "url": "https://www.mi.com/global/product/xiaomi-smart-air-purifier-4"
            },
            "premium": {
                "item": "Dyson Purifier Cool TP07",
                "price": "$549.99",
                "vendor": "Dyson Direct",
                "pros": "Bladeless fan + HEPA + captures VOCs.",
                "cons": "High upfront and filter cost.",
                "url": "https://www.dyson.com/air-treatment/purifiers/dyson-purifier-cool/dyson-purifier-cool-tp07-white-silver"
            }
        })
        metrics = {
            "flow": "Flow Score: 78/100 — Good. Chi energy is unobstructed from main entrance.",
            "lighting": "Lighting Score: 82/100 — Strong. Cross-ventilation and natural light maximized.",
            "energy": "Energy Score: 80/100 — Positive. Fengshui element balance is near optimal."
        }
    elif tier == "diamond":
        vendor_data.append({
            "category": "Ergonomic Seating",
            "reasoning": "Spinal alignment and prolonged comfort. [Source: Mayo Clinic]",
            "budget": {
                "item": "Sihoo M57 Ergonomic Chair",
                "price": "$149.00",
                "vendor": "Amazon",
                "pros": "Adjustable lumbar support, breathable mesh.",
                "cons": "Basic armrest adjustment.",
                "url": "https://www.amazon.com/dp/B08CG6BLQT"
            },
            "mid_range": {
                "item": "ErgoTune Supreme V3",
                "price": "$499.00",
                "vendor": "ErgoTune Official",
                "pros": "11 adjustment points, Singapore-designed for Asian frames.",
                "cons": "Styling may not suit all aesthetics.",
                "url": "https://ergotune.com/products/ergotune-supreme"
            },
            "premium": {
                "item": "Herman Miller Aeron (Size B)",
                "price": "$1,445.00",
                "vendor": "Herman Miller",
                "pros": "Gold standard in ergonomics, PostureFit SL, 12-year warranty.",
                "cons": "Requires professional fitting for best results.",
                "url": "https://store.hermanmiller.com/office-chairs-aeron/aeron-chair/2195348.html"
            }
        })
        metrics = {
            "flow": "Flow Score: 95/100 — Excellent. Full spatial harmony achieved.",
            "lighting": "Lighting Score: 93/100 — Optimised. Circadian lighting schedule active.",
            "energy": "Energy Score: 97/100 — Peak Chi. Diamond-grade holistic optimisation complete."
        }
    else:
        metrics = {}

    if req.master_mode == "b2b":
        email_ctx = f"{req.store_type} commercial space"
    else:
        email_ctx = f"{req.vibe} workspace"

    response_payload = {
        "status": "success",
        "message": f"Blueprint generation complete for {tier} tier.",
        "image_base64": generated_image_b64,
        "vendor_data": vendor_data,
        "metrics": metrics,
        "email_template": f"Hello Vendor, I am interested in these items to implement my {email_ctx} optimization blueprint generated by Fama. Could you let me know if they are in stock?",
        "conversation_history": req.conversation_history or []
    }
    
    return response_payload
