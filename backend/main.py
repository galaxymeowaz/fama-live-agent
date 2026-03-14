import os
import io
import json
import base64
import time
import asyncio
import collections
import urllib.request
import urllib.parse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from google import genai
from google.genai import types

# --- Fama Live AI Schemas ---
class ProductDetail(BaseModel):
    item: str
    price: str
    vendor: str
    pros: str
    cons: str
    url: str

class ProductCategory(BaseModel):
    category: str
    reasoning: str
    budget: ProductDetail
    mid_range: ProductDetail
    premium: ProductDetail

class SpaceMetrics(BaseModel):
    flow: str
    lighting: str
    energy: str

class SpaceBlueprint(BaseModel):
    message: str = Field(description="The Fama Agent's conversational response.")
    metrics: SpaceMetrics
    vendor_data: list[ProductCategory]

# ---------------------------------------------------------------------------
# In-Memory Rate Limiter
# ---------------------------------------------------------------------------
class RateLimiter:
    """Sliding-window IP rate limiter using only stdlib."""
    def __init__(self):
        self._windows: dict[str, collections.deque] = collections.defaultdict(collections.deque)

    def is_allowed(self, key: str, max_calls: int, window_seconds: int) -> bool:
        now = time.monotonic()
        dq = self._windows[key]
        while dq and dq[0] < now - window_seconds:
            dq.popleft()
        if len(dq) >= max_calls:
            return False
        dq.append(now)
        return True

rate_limiter = RateLimiter()

load_dotenv()

# ---------------------------------------------------------------------------
# Zero Trust Startup Validation
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
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

print("--- SYSTEM CHECK: All required secrets loaded. Server is authorised to boot. ---")

app = FastAPI(title="Project Fama - Holistic Space Optimizer API")

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    image_base64: str = ""
    conversation_history: list = None

def verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY:
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
        print(f"reCAPTCHA error: {e}")
        return False

# ---------------------------------------------------------------------------
# PHASE 2: INTERRUPTIBLE LIVE AGENT (WEBSOCKET)
# ---------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Edge Auth: Passcode via Query Params (e.g., ws://localhost:8000/ws?passcode=xyz)
    passcode = websocket.query_params.get("passcode")
    if passcode not in [JUDGE_PASSCODE, FRIEND_PASSCODE]:
        await websocket.close(code=1008, reason="Unauthorized. Valid passcode required.")
        return

    client_ip = websocket.client.host if websocket.client else "unknown"
    if not rate_limiter.is_allowed(f"ws:{client_ip}", max_calls=15, window_seconds=600):
        await websocket.close(code=1008, reason="Rate limit exceeded.")
        return
        
    await websocket.accept()
    print(f"Client connected to Live Agent WebSocket: {client_ip}")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 2. Configure Live API Modality (Strictly Audio In -> Audio Out)
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(parts=[types.Part.from_text(
    text="You are the Fama Holistic Space Optimizer. You act as a real-time, interruptible voice agent. "
         "Help the user design their room, analyze Feng Shui energy, or optimize their retail space. "
         "Keep your verbal responses extremely concise, conversational, and cite credible sources."
        )])
    )
    
    try:
        async with client.aio.live.connect(model='gemini-2.5-flash-native-audio-preview-12-2025', config=config) as session:
            print("Successfully bridged to Gemini Live API.")

            async def receive_from_frontend():
                try:
                    while True:
                        # Receive raw PCM audio bytes from user's microphone
                        data = await websocket.receive_bytes()
                        await session.send_realtime_input(
                            media=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                        )
                except WebSocketDisconnect:
                    print("Frontend disconnected.")
                except Exception as e:
                    print(f"Frontend Rx Error: {e}")

            async def receive_from_gemini():
                try:
                    async for response in session.receive():
                        server_content = response.server_content
                        if server_content is not None:
                            # Stream Gemini's audio voice back to the user's speakers
                            if server_content.model_turn is not None:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        await websocket.send_bytes(part.inline_data.data)
                                        
                            # Handle Interruptibility (Barge-in)
                            if server_content.interrupted:
                                # Tell frontend to instantly clear its audio playback buffer
                                await websocket.send_text(json.dumps({"action": "interrupt"}))
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"Gemini Rx Error: {e}")

            # 3. Run full-duplex streams concurrently using Asyncio
            task1 = asyncio.create_task(receive_from_frontend())
            task2 = asyncio.create_task(receive_from_gemini())
            
            await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
            
            task1.cancel()
            task2.cancel()
            
    except Exception as e:
        print(f"Live Session Error: {e}")
        try:
            await websocket.close(code=1011, reason="Gemini Live Connection Failed")
        except:
            pass

# ---------------------------------------------------------------------------
# PHASE 1: GENERATE BLUEPRINT (IMAGE + FENG SHUI)
# ---------------------------------------------------------------------------
@app.post("/generate_blueprint")
async def generate_blueprint(req: BlueprintRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    is_judge  = req.passcode == JUDGE_PASSCODE
    is_friend = req.passcode == FRIEND_PASSCODE
    if not is_judge and not is_friend:
        raise HTTPException(status_code=403, detail="Access denied. Valid passcode required.")

    blueprint_limit = 15 if is_judge else 10
    if not rate_limiter.is_allowed(f"blueprint:{client_ip}", max_calls=blueprint_limit, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Rate limit reached.")

    if not verify_recaptcha(req.recaptcha_token):
        raise HTTPException(status_code=403, detail="reCAPTCHA verification failed")

    client = genai.Client(api_key=GEMINI_API_KEY)
        
# 1. Native Gemini Image Call (Nano Banana architecture)
    generated_image_b64 = ""
    try:
        print("Generating new space blueprint via Gemini Image...")
        if req.master_mode == "b2b":
            visual_prompt = f"Interior design of a {req.store_type} commercial space. Highlight products: {req.high_margin_products}. Photorealistic architectural rendering."
        else:
            visual_prompt = f"Interior design of a {req.vibe} themed room. Photorealistic, high-resolution 16:9 architectural rendering. Complete aesthetic overhaul."
            
        if req.conversation_history:
            last_refine = req.conversation_history[-1]["content"] if isinstance(req.conversation_history[-1], dict) else str(req.conversation_history[-1])
            visual_prompt += f" Modify the design strictly based on this user request: {last_refine}"

        # Native Gemini models use generate_content, not generate_images
        image_result = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=visual_prompt,
        )
        
        # Extract the binary image data from the multimodal response part
        if image_result.parts:
            for part in image_result.parts:
                if part.inline_data:
                    img_bytes = part.inline_data.data
                    generated_image_b64 = base64.b64encode(img_bytes).decode('utf-8')
                    print("Image generation successful.")
                    break
            
    except Exception as e:
        print(f"Image Generation Error: {e}")
        generated_image_b64 = ""

    # 2. Live Business Logic via Gemini 2.5 Flash
    tier = req.tier.lower()
    category_count = 1 if tier == "free" else (2 if tier == "silver" else 3)
    
    prompt_text = f"You are Fama, an expert Holistic Space Optimizer. "
    if req.master_mode == "b2b":
        prompt_text += f"The user is optimizing a {req.store_type} commercial space. Focus on these high margin products: {req.high_margin_products}. "
    else:
        prompt_text += f"The user is optimizing a {req.vibe} themed space. "
        
    prompt_text += f"Provide EXACTLY {category_count} product categories (e.g., Lighting, Seating). "
    prompt_text += "For each category, provide a Budget, Mid-Range, and Premium real-world product with realistic Shopee/Amazon URLs. "
    
    # FENG SHUI INJECTION
    prompt_text += "Also provide 3 metrics (flow, lighting, energy) out of 100. The 'energy' metric MUST strictly evaluate the Feng Shui Chi flow and elemental balance of the space. Do not use generic energy definitions; focus purely on Feng Shui principles. "
    
    if req.conversation_history:
        last_req = req.conversation_history[-1]["content"] if isinstance(req.conversation_history[-1], dict) else str(req.conversation_history[-1])
        prompt_text += f"USER REFINEMENT REQUEST: '{last_req}'. Adjust your recommendations to match this request."

    contents = [prompt_text]
    
    # Inject Vision if Image is provided (Camera is completely optional)
    if req.image_base64:
        try:
            b64_data = req.image_base64.split(",")[1] if "," in req.image_base64 else req.image_base64
            image_bytes = base64.b64decode(b64_data)
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        except Exception as e:
            print(f"Vision Decode Error: {e}")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SpaceBlueprint,
            ),
        )
        
        live_data = json.loads(response.text)
        vendor_data = live_data.get("vendor_data", [])
        metrics = live_data.get("metrics", {})
        agent_message = live_data.get("message", f"Blueprint generation complete for {tier} tier.")
        
    except Exception as e:
        print(f"Gemini Inference Error: {e}")
        vendor_data = []
        metrics = {"flow": "Error", "lighting": "Error", "energy": "Error"}
        agent_message = "I encountered a network anomaly while analyzing the space. Please retry."

    email_ctx = f"{req.store_type} commercial space" if req.master_mode == "b2b" else f"{req.vibe} space"

    response_payload = {
        "status": "success",
        "message": agent_message,
        "image_base64": generated_image_b64,
        "vendor_data": vendor_data,
        "metrics": metrics,
        "email_template": f"Hello Vendor, I am interested in these items to implement my {email_ctx} optimization blueprint generated by Fama. Could you let me know if they are in stock?",
        "conversation_history": req.conversation_history or []
    }
    
    return response_payload