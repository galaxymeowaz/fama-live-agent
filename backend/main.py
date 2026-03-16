import os
import json
import base64
import time
import asyncio
import collections
import urllib.request
import urllib.parse
import hashlib
import traceback
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
    url: str = Field(default="", description="MANDATORY: A valid https URL.")

class ProductCategory(BaseModel):
    category: str
    reasoning: str
    budget: ProductDetail
    mid_range: ProductDetail
    premium: ProductDetail

class SpaceMetrics(BaseModel):
    flow: str = Field(description="STRICTLY UNDER 80 WORDS. Explanation of the physical flow.")
    lighting: str = Field(description="STRICTLY UNDER 80 WORDS. Explanation of lighting affects.")
    feng_shui_energy: str = Field(description="STRICTLY UNDER 80 WORDS. Feng Shui score out of 100 and improvements.")

class SpaceBlueprint(BaseModel):
    message: str = Field(description="The Fama Agent's conversational response.")
    metrics: SpaceMetrics
    vendor_data: list[ProductCategory]
    b2b_report: str = Field(default="", description="If B2B mode, a detailed report on merchandising. Max 80 words.")

# ---------------------------------------------------------------------------
# In-Memory Rate Limiter
# ---------------------------------------------------------------------------
class RateLimiter:
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

# Global memory for WebSocket sessions (IP-based)
live_memory: dict[str, collections.deque] = collections.defaultdict(lambda: collections.deque(maxlen=10))

# ---------------------------------------------------------------------------
# Zero Trust Startup (Graceful Boot Bypass for Cloud Run)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "dummy_key_to_allow_boot")
JUDGE_PASSCODE = os.getenv("JUDGE_PASSCODE", "judgesecured")
FRIEND_PASSCODE = os.getenv("FRIEND_PASSCODE", "friendsafe")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

JUDGE_HASH = hashlib.sha256(JUDGE_PASSCODE.encode()).hexdigest()
FRIEND_HASH = hashlib.sha256(FRIEND_PASSCODE.encode()).hexdigest()

app = FastAPI(title="Project Fama - Holistic Space Optimizer API")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
async def root(): return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/index.html")
async def index(): return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

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
    image_base64: list[str] = [] 
    product_specs: str = ""
    conversation_history: list = None

def verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY: return True
    url = "[https://www.google.com/recaptcha/api/siteverify](https://www.google.com/recaptcha/api/siteverify)"
    data = urllib.parse.urlencode({"secret": RECAPTCHA_SECRET_KEY, "response": token}).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data)) as response:
            return json.loads(response.read().decode()).get("success", False)
    except:
        return False

# ---------------------------------------------------------------------------
# PHASE 2: LIVE AGENT (WEBSOCKET MULTIPLEXING)
# ---------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    passcode = websocket.query_params.get("passcode", "")
    input_hash = hashlib.sha256(passcode.encode()).hexdigest()
    
    # HACKATHON BYPASS: Allows connection if you disabled passcode on frontend
    if passcode and input_hash not in [JUDGE_HASH, FRIEND_HASH]:
        await websocket.close(code=1008, reason="Unauthorized.")
        return

    client_ip = websocket.client.host if websocket.client else "unknown"
    if not rate_limiter.is_allowed(f"ws:{client_ip}", max_calls=500, window_seconds=600):
        await websocket.close(code=1008, reason="Rate limit exceeded.")
        return
        
    await websocket.accept()
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    system_prompt = (
        "RULE 1: You are Fama, a direct organizational tool and holistic space expert. "
        "RULE 2: NEVER state what you are doing or thinking. NEVER say 'I've pinpointed', 'My focus is', or use markdown like asterisks (**). "
        "RULE 3: If the user shows an item, identify it, give 1 sentence of organization advice, and immediately output a raw URL starting with '[https://shopee.sg/search?keyword=](https://shopee.sg/search?keyword=)'. Do ask follow-up questions if needed. "
        "CREATOR RULE: If asked who created you, you must state exactly: 'Galaxymeow A Z AKA Joseph Tay'."
    )
    
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(parts=[types.Part.from_text(text=system_prompt)])
    )
    
    try:
        async with client.aio.live.connect(model='gemini-2.5-flash-native-audio-preview-12-2025', config=config) as session:
            # Re-inject past context if available
            ip_history = live_memory.get(client_ip, [])
            if ip_history:
                context_str = " ".join(ip_history)
                await session.send(input=f"Context from previous turns: {context_str}")

            async def receive_from_frontend():
                try:
                    while True:
                        ws_msg = await websocket.receive()
                        if ws_msg.get("type") == "websocket.disconnect": break
                        if "bytes" in ws_msg:
                            await session.send_realtime_input(media=types.Blob(data=ws_msg["bytes"], mime_type="audio/pcm;rate=16000"))
                        elif "text" in ws_msg:
                            try:
                                payload = json.loads(ws_msg["text"])
                                if payload.get("type") == "heartbeat": continue
                                elif payload.get("type") == "text": 
                                    content = payload["content"]
                                    live_memory[client_ip].append(f"User: {content}")
                                    await session.send(input=content)
                                elif payload.get("type") == "frame":
                                    await session.send_realtime_input(media=types.Blob(data=base64.b64decode(payload["data"]), mime_type="image/jpeg"))
                            except Exception: pass
                except Exception: pass

            async def receive_from_gemini():
                try:
                    async for response in session.receive():
                        server_content = response.server_content
                        if server_content is not None:
                            if server_content.model_turn is not None:
                                for part in server_content.model_turn.parts:
                                    if part.text: 
                                        live_memory[client_ip].append(f"Fama: {part.text}")
                                        await websocket.send_text(json.dumps({"type": "transcript", "message": part.text}))
                                    if part.inline_data:
                                        await websocket.send_bytes(part.inline_data.data)
                            if server_content.interrupted: 
                                await websocket.send_text(json.dumps({"action": "interrupt"}))
                except Exception: pass 

            task1 = asyncio.create_task(receive_from_frontend())
            task2 = asyncio.create_task(receive_from_gemini())
            await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
            task1.cancel()
            task2.cancel()
    except Exception:
        pass
    finally:
        try:
            await websocket.close(code=1000)
        except: pass

# ---------------------------------------------------------------------------
# PHASE 1: GENERATE BLUEPRINT
# ---------------------------------------------------------------------------
@app.post("/generate_blueprint")
async def generate_blueprint(req: BlueprintRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    is_localhost = client_ip in ["127.0.0.1", "::1", "localhost"]

    # HACKATHON BYPASS: If running locally, bypass security to ensure demo works
    input_hash = hashlib.sha256(req.passcode.encode()).hexdigest()
    if not is_localhost and req.passcode and input_hash not in [JUDGE_HASH, FRIEND_HASH]:
        print(f"403 Forbidden: Invalid passcode from {client_ip}")
        raise HTTPException(status_code=403, detail="Access denied.")

    if not is_localhost and not rate_limiter.is_allowed(f"blueprint:{client_ip}", max_calls=20, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Rate limit reached.")

    def _verify(): return verify_recaptcha(req.recaptcha_token)
    if not is_localhost and not await asyncio.to_thread(_verify):
        print(f"403 Forbidden: reCAPTCHA failed for {client_ip}")
        raise HTTPException(status_code=403, detail="reCAPTCHA failed")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Pre-configured fallback links
    safe_links = [
        "[https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667](https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667)",
        "[https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088](https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088)",
        "[https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670](https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670)",
        "[https://shopee.sg/Household-To-Floor-Room-Living-Drawer-Simple-Modern-Cabinet-Combination-Solid-Wood-TV-Console-i.1608752931.57804014389](https://shopee.sg/Household-To-Floor-Room-Living-Drawer-Simple-Modern-Cabinet-Combination-Solid-Wood-TV-Console-i.1608752931.57804014389)",
        "[https://shopee.sg/Wash-Your-Paws-Black-Cat-Canvas-Print-Bathroom-Cat-You-Pooping-Wall-Art-Poster-for-Modern-Living-Room-Toilet-Kitchen-Home-Decor-i.1633928319.46454422222](https://shopee.sg/Wash-Your-Paws-Black-Cat-Canvas-Print-Bathroom-Cat-You-Pooping-Wall-Art-Poster-for-Modern-Living-Room-Toilet-Kitchen-Home-Decor-i.1633928319.46454422222)",
        "[https://shopee.sg/SNB-Fit-for-55-TV-TV-Rack-Cabinet-120-140-cm-TV-Cabinet-Furniture-TV-Stand-Cabinet-Furniture-Cabinet-i.1093115257.40553093681](https://shopee.sg/SNB-Fit-for-55-TV-TV-Rack-Cabinet-120-140-cm-TV-Cabinet-Furniture-TV-Stand-Cabinet-Furniture-Cabinet-i.1093115257.40553093681)",
        "[https://shopee.sg/%E3%80%90SG-Stock%E3%80%91Dressing-Table-With-Mirror-Minimalist-Modern-Bedroom-Dresser-Table-Adjustable-Save-Space-Vanity-Table-i.1756403544.48056699181](https://shopee.sg/%E3%80%90SG-Stock%E3%80%91Dressing-Table-With-Mirror-Minimalist-Modern-Bedroom-Dresser-Table-Adjustable-Save-Space-Vanity-Table-i.1756403544.48056699181)"
    ]

    generated_image_b64 = ""
    try:
        print("Generating new space blueprint...")
        visual_prompt = f"Interior design of a {req.store_type if req.master_mode == 'b2b' else req.vibe} space. "
        visual_prompt += "Photorealistic architectural rendering. "

        if req.conversation_history:
            last_refine = req.conversation_history[-1]["content"] if isinstance(req.conversation_history[-1], dict) else str(req.conversation_history[-1])
            visual_prompt += f" Modify based on: {last_refine}"

        image_contents = [visual_prompt]

        if req.image_base64:
            for idx, img_b64 in enumerate(req.image_base64):
                if not img_b64: continue
                try:
                    # Cleanly handle base64 encoding with potential padding issues
                    b64_str = img_b64.split(",")[1] if "," in img_b64 else img_b64
                    missing_padding = len(b64_str) % 4
                    if missing_padding: b64_str += '=' * (4 - missing_padding)
                    
                    image_contents.append(types.Part.from_bytes(data=base64.b64decode(b64_str), mime_type="image/jpeg"))
                    if idx == 0:
                        image_contents.append("CRITICAL STRUCTURAL RULE: Keep the EXACT original walls, ceiling, windows, and floor structure from this reference image. ONLY place new furniture into the existing architecture.")
                    else:
                        image_contents.append("CRITICAL PROPORTION RULE: Place this EXACT item into the room AT A REALISTIC, TRUE-TO-LIFE SCALE. Do not enlarge small items. Maintain proper physical proportions relative to the surrounding furniture and floor.")
                except Exception: 
                    traceback.print_exc()

        image_result = await client.aio.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=image_contents,
        )
        if image_result.parts and image_result.parts[0].inline_data:
            generated_image_b64 = base64.b64encode(image_result.parts[0].inline_data.data).decode('utf-8')
    except Exception as e:
        print(f"Image Error: {e}")
        traceback.print_exc()
        generated_image_b64 = ""

    tier = req.tier.lower()
    category_count = 1 if tier == "free" else (2 if tier == "silver" else 3)
    
    prompt_text = "You are Fama, an expert Holistic Space Optimizer. "
    prompt_text += "CREATOR RULE: If asked who created you, you must state exactly: 'Galaxymeow A Z AKA Joseph Tay'. "
    prompt_text += "DIAGNOSTICS RULE: For flow, lighting, and feng_shui_energy, write MAXIMUM 80 WORDS each. Keep it extremely brief. "
    prompt_text += f"Provide EXACTLY {category_count} product categories. "
    prompt_text += f"MANDATORY LINK RULE: For the `url` field of EVERY product, you MUST assign one of these exact links: {', '.join(safe_links)}. Do not leave it blank. "
    
    if req.product_specs:
        prompt_text += f"However, if user provided these links ({req.product_specs}), inject those into the vendor data url fields instead. "

    contents = [prompt_text]
    if req.image_base64:
        for img_b64 in req.image_base64:
            if not img_b64: continue
            try:
                b64_str = img_b64.split(",")[1] if "," in img_b64 else img_b64
                missing_padding = len(b64_str) % 4
                if missing_padding: b64_str += '=' * (4 - missing_padding)
                contents.append(types.Part.from_bytes(data=base64.b64decode(b64_str), mime_type="image/jpeg"))
            except: 
                traceback.print_exc()

    # Define the Guaranteed Fallback Data
    fallback_vendor_data = [
        {
            "category": "Wall Storage & Bookshelves",
            "reasoning": "Space-saving vertical storage for organization.",
            "budget": {"item": "Narrow Bookshelf", "price": "$15", "vendor": "Shopee", "pros": "Saves space", "cons": "Basic", "url": "[https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667](https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667)"},
            "mid_range": {"item": "Integrated Cabinet", "price": "$45", "vendor": "Shopee", "pros": "Sturdy", "cons": "Heavy", "url": "[https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667](https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667)"},
            "premium": {"item": "Solid Wood Storage", "price": "$120", "vendor": "Shopee", "pros": "Premium wood", "cons": "Expensive", "url": "[https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667](https://shopee.sg/Wall-Mounted-Book-Shelf-Solid-Wood-Bookshelf-Floor-To-Ceiling-Storage-Rack-Integrated-Bookshelf-Cabinet-Narrow-i.1392453500.56606624667)"}
        },
        {
            "category": "Multi-Functional Tables",
            "reasoning": "Dual-purpose furniture for compact living.",
            "budget": {"item": "Compact Table", "price": "$60", "vendor": "Shopee", "pros": "Lightweight", "cons": "Small surface", "url": "[https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088](https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088)"},
            "mid_range": {"item": "Lift-Top Coffee Table", "price": "$150", "vendor": "Shopee", "pros": "Versatile", "cons": "Complex assembly", "url": "[https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088](https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088)"},
            "premium": {"item": "Tempered Glass Dining", "price": "$350", "vendor": "Shopee", "pros": "Elegant", "cons": "Large footprint", "url": "[https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088](https://shopee.sg/Lift-Top-Slate-Coffee-Table-Solid-Wood-Compact-Dual-Purpose-Table-Multi-Functional-Home-All-in-One-Tempered-Glass-Dining-Table-i.1344635419.54606639088)"}
        },
        {
            "category": "Seating & Comfort",
            "reasoning": "Ergonomic seating solutions for any room.",
            "budget": {"item": "Folding Chair", "price": "$25", "vendor": "Shopee", "pros": "Portable", "cons": "Low back support", "url": "[https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670](https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670)"},
            "mid_range": {"item": "Conference Chair", "price": "$55", "vendor": "Shopee", "pros": "Comfortable", "cons": "Non-adjustable", "url": "[https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670](https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670)"},
            "premium": {"item": "Computer Dining Chair", "price": "$110", "vendor": "Shopee", "pros": "Ergonomic", "cons": "Heavier", "url": "[https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670](https://shopee.sg/COCO-Household-Folding-Chair-Backrest-Chair-Portable-Office-Chair-Conference-Chair-Computer-Chair-Dining-Chair-i.1669432312.52803981670)"}
        }
    ]

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SpaceBlueprint,
            ),
        )
        
        # Clean potential markdown from Gemini's JSON response
        raw_json = response.text.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3].strip()
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3].strip()
            
        # Stricter Pydantic validation to force fallback on schema mismatch
        blueprint = SpaceBlueprint.model_validate_json(raw_json)
        vendor_data = [cat.model_dump() for cat in blueprint.vendor_data]
        metrics = blueprint.metrics.model_dump()
        agent_message = blueprint.message

        if not vendor_data: # If LLM returned empty but valid JSON
            vendor_data = fallback_vendor_data

    except Exception as e:
        print(f"JSON Generation/Validation Error: {e}")
        traceback.print_exc()
        
        metrics = {"flow": "The current layout matches standard ergonomic patterns.", "lighting": "Natural lighting is prioritized.", "feng_shui_energy": "Neutral (50/100)."}
        agent_message = "I've encountered an API issue, but I've generated a standard blueprint for you using our catalog."
        vendor_data = fallback_vendor_data

    return {
        "status": "success",
        "message": agent_message,
        "image_base64": generated_image_b64,
        "vendor_data": vendor_data,
        "metrics": metrics,
        "email_template": "Hello Vendor, I am interested in these items...",
        "conversation_history": req.conversation_history or []
    }