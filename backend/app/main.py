import os
import io
import base64
import logging
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.config import settings
from app.telephony.twilio_service import twilio_service
from app.telephony.media_stream import TwilioMediaStreamHandler, dashboard_websockets, broadcast_to_dashboards
from app.telephony.conversation_relay import TwilioConversationRelayHandler
from app.telephony.gemini_live_stream import GeminiLiveStreamHandler
from app.whatsapp.cloud_api import whatsapp_service, whatsapp_dispatch_logs
from app.scheduler.callback_service import callback_service
from app.agent.conversation_engine import conversation_engine
from app.agent.decision_classifier import decision_classifier
from app.voice.tts_service import tts_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")

app = FastAPI(
    title=settings.APP_NAME,
    description="ElevateBox AI Voice Calling, Multi-Lingual Qualification & WhatsApp Action System",
    version="1.0.0"
)

# CORS middleware for Web Dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for Architecture Diagram and Resume PDF
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ----------------- PYDANTIC REQUEST MODELS -----------------

class CallInitiateRequest(BaseModel):
    phone_number: str = settings.TARGET_PHONE_NUMBER
    language: Optional[str] = "multi"
    mode: Optional[str] = "CONVERSATION_RELAY"

class SimulateTurnRequest(BaseModel):
    utterance: str
    phone_number: Optional[str] = settings.TARGET_PHONE_NUMBER
    history: Optional[List[Dict[str, str]]] = []
    language: Optional[str] = "multi"
    gender: Optional[str] = "female"

class WhatsAppTriggerRequest(BaseModel):
    phone_number: str = settings.TARGET_PHONE_NUMBER
    type: str = "MID_CALL"  # "MID_CALL", "POST_CALL", or "TEMPLATE"
    lead_details: Optional[Dict[str, Any]] = None
    template_name: Optional[str] = "jaspers_market_order_confirmation_v1"
    language_code: Optional[str] = "en_US"
    components: Optional[List[Dict[str, Any]]] = None

class WhatsAppTemplateRequest(BaseModel):
    phone_number: str = settings.TARGET_PHONE_NUMBER
    template_name: str = "jaspers_market_order_confirmation_v1"
    language_code: str = "en_US"
    components: Optional[List[Dict[str, Any]]] = None

class ConfigUpdateRequest(BaseModel):
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    CANDIDATE_PHONE: Optional[str] = None
    TARGET_PHONE_NUMBER: Optional[str] = None

# ----------------- REST API ENDPOINTS -----------------

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "twilio_configured": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN),
        "whatsapp_configured": bool(settings.WHATSAPP_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID),
        "llm_configured": bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY),
        "target_number": settings.TARGET_PHONE_NUMBER
    }

@app.get("/api/config")
async def get_config():
    return {
        "candidate_name": settings.CANDIDATE_NAME,
        "candidate_phone": settings.CANDIDATE_PHONE,
        "candidate_email": settings.CANDIDATE_EMAIL,
        "target_phone_number": settings.TARGET_PHONE_NUMBER,
        "twilio_configured": bool(settings.TWILIO_ACCOUNT_SID and not settings.TWILIO_ACCOUNT_SID.startswith("mock")),
        "whatsapp_configured": bool(settings.WHATSAPP_TOKEN and not settings.WHATSAPP_TOKEN.startswith("mock")),
        "groq_configured": bool(settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("mock")),
        "gemini_configured": bool(settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("mock")),
        "resume_url": settings.CANDIDATE_RESUME_URL,
        "architecture_diagram_url": settings.ARCHITECTURE_DIAGRAM_URL
    }

@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest):
    if req.TWILIO_ACCOUNT_SID is not None:
        settings.TWILIO_ACCOUNT_SID = req.TWILIO_ACCOUNT_SID
    if req.TWILIO_AUTH_TOKEN is not None:
        settings.TWILIO_AUTH_TOKEN = req.TWILIO_AUTH_TOKEN
    if req.TWILIO_PHONE_NUMBER is not None:
        settings.TWILIO_PHONE_NUMBER = req.TWILIO_PHONE_NUMBER
    if req.WHATSAPP_TOKEN is not None:
        settings.WHATSAPP_TOKEN = req.WHATSAPP_TOKEN
        whatsapp_service.token = req.WHATSAPP_TOKEN
    if req.WHATSAPP_PHONE_NUMBER_ID is not None:
        settings.WHATSAPP_PHONE_NUMBER_ID = req.WHATSAPP_PHONE_NUMBER_ID
        whatsapp_service.phone_number_id = req.WHATSAPP_PHONE_NUMBER_ID
    if req.GROQ_API_KEY is not None:
        settings.GROQ_API_KEY = req.GROQ_API_KEY
        conversation_engine.groq_api_key = req.GROQ_API_KEY
    if req.GEMINI_API_KEY is not None:
        settings.GEMINI_API_KEY = req.GEMINI_API_KEY
        conversation_engine.gemini_api_key = req.GEMINI_API_KEY
    if req.CANDIDATE_PHONE is not None:
        settings.CANDIDATE_PHONE = req.CANDIDATE_PHONE
    if req.TARGET_PHONE_NUMBER is not None:
        settings.TARGET_PHONE_NUMBER = req.TARGET_PHONE_NUMBER
    return {"status": "success", "message": "Configuration updated successfully"}

@app.post("/api/calls/initiate")
async def initiate_call(req: CallInitiateRequest):
    """
    Triggers the autonomous outbound call to 8977155678 (or custom number) with selected language.
    """
    host = settings.PUBLIC_URL or f"localhost:{settings.PORT}"
    result = await twilio_service.initiate_outbound_call(
        to_number=req.phone_number,
        webhook_host=host,
        language=req.language or "en"
    )
    await broadcast_to_dashboards("CALL_INITIATED", {
        "phone_number": req.phone_number,
        "language": req.language or "en",
        "result": result
    })
    return result

@app.post("/api/calls/simulate-turn")
async def simulate_turn(req: SimulateTurnRequest):
    """
    Processes a spoken conversation turn in real-time.
    Runs STT -> LLM Conversation (Multilingual / Code-Switching) -> Intent Classification -> Mid-Call Action -> TTS!
    Returns spoken audio base64, transcript, and action status.
    """
    # 1. Process conversation turn with LLM and tool triggers
    turn_result = await conversation_engine.process_turn(
        conversation_history=req.history or [],
        latest_utterance=req.utterance,
        caller_phone=req.phone_number or settings.TARGET_PHONE_NUMBER,
        detected_language=req.language if req.language not in ["auto", "multi"] else None
    )

    speech_text = turn_result.get("speech_response", "Thank you for the information.")
    detected_lang = turn_result.get("language_detected", "multi")

    # 2. Synthesize TTS speech audio bytes
    audio_bytes, lang_used = await tts_service.synthesize_speech_bytes(
        text=speech_text,
        lang=detected_lang,
        gender=req.gender or "female"
    )
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    response_payload = {
        "speech_response": speech_text,
        "audio_base64": f"data:audio/mp3;base64,{audio_b64}",
        "language_detected": lang_used,
        "intent": turn_result.get("intent", "WARM"),
        "confidence": turn_result.get("confidence", 0.9),
        "reason": turn_result.get("reason", ""),
        "action_trigger": turn_result.get("action_trigger", "NONE"),
        "action_payload": turn_result.get("action_payload", {}),
        "qualification": turn_result.get("qualification", {}),
        "midcall_whatsapp_dispatched": turn_result.get("midcall_whatsapp_dispatched", False),
        "callback_scheduled": turn_result.get("callback_scheduled", None)
    }

    # Broadcast turn event to dashboard
    await broadcast_to_dashboards("TURN_COMPLETED", response_payload)

    return response_payload

@app.api_route("/api/telephony/twiml", methods=["GET", "POST"], response_class=PlainTextResponse)
async def twilio_twiml_webhook(request: Request):
    """
    Twilio Webhook returning initial TwiML greeting with conversational voice and Gather.
    """
    to_phone = request.query_params.get("to") or settings.TARGET_PHONE_NUMBER
    stream_param = request.query_params.get("stream", "false").lower() == "true"
    host = settings.PUBLIC_URL or f"localhost:{settings.PORT}"
    
    # Broadcast call started event to web dashboard
    await broadcast_to_dashboards("CALL_STARTED", {
        "caller_phone": to_phone,
        "mode": "TWILIO_VOICE"
    })

    if stream_param:
        twiml_xml = twilio_service.generate_twiml_stream(host=host, to_number=to_phone)
        logger.info(f"Generated Media Stream TwiML:\n{twiml_xml}")
        return Response(content=twiml_xml, media_type="application/xml")

    # Generate dynamic opening greeting
    greeting = await conversation_engine.generate_opening_greeting()
    
    # Broadcast opening transcript to web dashboard
    await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
        "speaker": "AI",
        "text": greeting,
        "language": "Universal",
        "role": "assistant"
    })

    twiml_xml = twilio_service.generate_twiml_conversation_turn(
        speech_text=greeting,
        host=host,
        language="te-IN"
    )
    
    logger.info(f"Generated Conversational Voice TwiML:\n{twiml_xml}")
    return Response(content=twiml_xml, media_type="application/xml")

call_session_histories: Dict[str, List[Dict[str, str]]] = {}

@app.api_route("/api/telephony/gather-response", methods=["GET", "POST"], response_class=PlainTextResponse)
async def twilio_gather_response(request: Request):
    """
    Processes caller's spoken words transcribed directly by Twilio, maintains multi-turn context, and replies!
    """
    body = {}
    try:
        # Check query params
        if request.query_params:
            body.update(dict(request.query_params))
        # Check form data
        form_data = await request.form()
        if form_data:
            body.update(dict(form_data))
    except Exception:
        pass

    speech_result = body.get("SpeechResult", "").strip()
    confidence = body.get("Confidence", "0.0")
    # Determine actual customer / lead phone number
    to_number = body.get("To", "")
    from_number = body.get("From", "")
    if to_number and not to_number.startswith("+1605"):
        caller_phone = to_number
    elif from_number and not from_number.startswith("+1605"):
        caller_phone = from_number
    else:
        caller_phone = settings.TARGET_PHONE_NUMBER

    call_id = body.get("CallSid") or caller_phone

    print("\n" + "="*70)
    logger.info(f"🎙️ [CALLER SPOKE / RECEIVED SPEECH]: \"{speech_result}\" (Confidence: {confidence})")
    print("="*70 + "\n")

    # Broadcast caller speech to web dashboard
    await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
        "speaker": "USER",
        "text": speech_result or "...",
        "language": "auto",
        "role": "user"
    })

    lang_param = request.query_params.get("lang", "en-IN")
    forced_lang = "te" if "te" in lang_param else ("hi" if "hi" in lang_param else "en")

    # Retrieve or initialize call session history
    if call_id not in call_session_histories:
        call_session_histories[call_id] = []

    history = call_session_histories[call_id]

    # Process user speech through Pure AI Conversation Engine
    turn_result = await conversation_engine.process_turn(
        conversation_history=history,
        latest_utterance=speech_result if speech_result else "హలో, మీరు మాట్లాడేది వినపడలేదు",
        caller_phone=caller_phone,
        detected_language=forced_lang
    )

    ai_reply = turn_result.get("speech_response")
    detected_lang = turn_result.get("language_detected", forced_lang)

    # Append to session history for continuous dialogue progression
    history.append({"role": "user", "content": speech_result})
    history.append({"role": "assistant", "content": ai_reply})

    print("\n" + "#"*70)
    logger.info(f"🤖 [AI GENERATED REPLY]: \"{ai_reply}\" (Lang: {detected_lang})")
    logger.info(f"📊 [INTENT CLASSIFIED]: {turn_result.get('intent')} | Action: {turn_result.get('action_trigger')}")
    print("#"*70 + "\n")

    # Broadcast AI response to web dashboard
    await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
        "speaker": "AI",
        "text": ai_reply,
        "language": detected_lang,
        "role": "assistant"
    })

    # Pick voice language for Twilio
    lang_str = str(detected_lang).lower()
    if "te" in lang_str or "telugu" in lang_str:
        twilio_lang = "te-IN"
    elif "hi" in lang_str or "hindi" in lang_str:
        twilio_lang = "hi-IN"
    else:
        twilio_lang = "en-IN"
    host = settings.PUBLIC_URL or f"localhost:{settings.PORT}"
    
    # Check if this turn ends the call gracefully
    should_hangup = turn_result.get("end_call", False) or turn_result.get("action_trigger") == "END_CALL"
    if should_hangup:
        logger.info("📞 [CALL COMPLETION]: Farewell spoken -> Twilio <Hangup/> issued.")
    
    twiml_reply = twilio_service.generate_twiml_conversation_turn(
        ai_reply,
        host=host,
        language=twilio_lang,
        is_end_of_call=should_hangup
    )

    return Response(content=twiml_reply, media_type="application/xml")

from fastapi import Request

@app.post("/api/telephony/status")
async def twilio_status_webhook(request: Request):
    """
    Receives call status updates (ringing, in-progress, completed) from Twilio.
    """
    try:
        form_data = await request.form()
        body = dict(form_data)
        if not body:
            try:
                body = await request.json()
            except Exception:
                body = {}
    except Exception:
        body = {}

    rec_url = body.get("RecordingUrl")
    rec_sid = body.get("RecordingSid") or body.get("CallSid")
    if rec_url:
        mp3_url = f"{rec_url}.mp3"
        logger.info(f"🎙️ [CALL RECORDING READY]: {mp3_url}")
        
        # Asynchronously download MP3 to local recordings folder
        async def download_recording(url: str, filename: str):
            try:
                rec_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "recordings")
                os.makedirs(rec_dir, exist_ok=True)
                file_path = os.path.join(rec_dir, f"{filename}.mp3")
                
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN) if settings.TWILIO_ACCOUNT_SID else None
                async with httpx.AsyncClient(timeout=30.0, auth=auth) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(resp.content)
                        logger.info(f"💾 [SAVED TO LOCAL STORAGE]: {file_path} ({len(resp.content)} bytes)")
                    else:
                        logger.warning(f"Could not download MP3 directly (Status: {resp.status_code})")
            except Exception as e:
                logger.error(f"Failed saving local MP3 recording: {e}")

        asyncio.create_task(download_recording(mp3_url, rec_sid))
    
    logger.info(f"Twilio Call Status Webhook: {body}")
    await broadcast_to_dashboards("CALL_STATUS_UPDATE", body)
    return {"status": "received"}

@app.post("/api/whatsapp/dispatch")
async def dispatch_whatsapp(req: WhatsAppTriggerRequest):
    """
    Triggers mid-call, post-call, or template WhatsApp message manually or via system action.
    """
    if req.type == "MID_CALL":
        res = await whatsapp_service.send_midcall_hot_lead_proposal(
            to_phone=req.phone_number,
            lead_details=req.lead_details or {}
        )
    elif req.type == "TEMPLATE":
        res = await whatsapp_service.send_template_message(
            to_phone=req.phone_number,
            template_name=req.template_name or "jaspers_market_order_confirmation_v1",
            language_code=req.language_code or "en_US",
            components=req.components
        )
    else:
        res = await whatsapp_service.send_postcall_summary(
            to_phone=req.phone_number,
            conversation_context=req.lead_details or {},
            candidate_phone=settings.CANDIDATE_PHONE
        )
    await broadcast_to_dashboards("WHATSAPP_DISPATCHED", res)
    return res

@app.post("/api/whatsapp/send-template")
async def send_whatsapp_template_endpoint(req: WhatsAppTemplateRequest):
    """
    Directly dispatches an approved WhatsApp Template message.
    """
    res = await whatsapp_service.send_template_message(
        to_phone=req.phone_number,
        template_name=req.template_name,
        language_code=req.language_code,
        components=req.components
    )
    await broadcast_to_dashboards("WHATSAPP_DISPATCHED", res)
    return res

@app.get("/api/whatsapp/webhook")
async def whatsapp_webhook_verification(request: Request):
    """
    Meta WhatsApp Cloud API Webhook verification challenge (hub.mode, hub.challenge, hub.verify_token).
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    expected_token = settings.WHATSAPP_VERIFY_TOKEN or "elevatebox_webhook_verify_token_2026"

    if mode == "subscribe" and token == expected_token:
        logger.info("🟢 [META WHATSAPP WEBHOOK]: Webhook verified successfully!")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logger.warning(f"🔴 [META WHATSAPP WEBHOOK]: Verification failed. Token received: {token}")
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook_event(request: Request):
    """
    Receives incoming WhatsApp messages and delivery status updates from Meta Cloud API.
    """
    try:
        body = await request.json()
        logger.info(f"📩 [META WHATSAPP INBOUND EVENT]: {body}")
        
        # Broadcast incoming WhatsApp notification to web dashboard
        await broadcast_to_dashboards("WHATSAPP_WEBHOOK_EVENT", body)
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook event: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/api/whatsapp/logs")
async def get_whatsapp_logs():
    return {"logs": whatsapp_dispatch_logs}

@app.get("/api/callbacks")
async def get_callbacks():
    return {"callbacks": callback_service.get_all_callbacks()}

@app.post("/api/callbacks/schedule")
async def schedule_callback_manual(payload: Dict[str, Any] = Body(...)):
    res = callback_service.schedule_callback(
        phone_number=payload.get("phone_number", settings.TARGET_PHONE_NUMBER),
        time_expression=payload.get("time_expression", "tomorrow morning"),
        notes=payload.get("notes", "Web manual booking"),
        barrier_reason=payload.get("barrier_reason", "Customer requested callback")
    )
    return res

# ----------------- WEBSOCKET ENDPOINTS -----------------

@app.websocket("/ws/dashboard")
async def dashboard_websocket_endpoint(websocket: WebSocket):
    """
    Real-time telemetry WebSocket for the React Dashboard.
    """
    await websocket.accept()
    dashboard_websockets.append(websocket)
    logger.info(f"Dashboard client connected. Total connected: {len(dashboard_websockets)}")
    try:
        while True:
            data = await websocket.receive_text()
            # Heartbeat / Ping-pong
    except WebSocketDisconnect:
        if websocket in dashboard_websockets:
            dashboard_websockets.remove(websocket)
        logger.info("Dashboard client disconnected.")

@app.websocket("/ws/gemini-live")
@app.websocket("/ws/media-stream")
async def gemini_live_websocket_endpoint(websocket: WebSocket):
    """
    Twilio Media Streams bi-directional audio bridge to Gemini 3.1 Flash Live (bidiGenerateContent).
    """
    await websocket.accept()
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"🟢 [TWILIO GEMINI LIVE] WebSocket connection accepted from {client_host}")
    handler = GeminiLiveStreamHandler(websocket)
    await handler.run()

@app.websocket("/ws/conversation-relay")
@app.websocket("/ws/relay")
async def conversation_relay_websocket_endpoint(websocket: WebSocket):
    """
    Twilio ConversationRelay bi-directional WebSocket handler (fallback mode).
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"Incoming WebSocket connection attempt on /ws/conversation-relay from {client_host}")
    handler = TwilioConversationRelayHandler(websocket)
    await handler.run()

@app.websocket("/ws/twilio")
async def twilio_websocket_endpoint(websocket: WebSocket):
    """
    Twilio Media Stream bi-directional WebSocket handler.
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(f"Incoming WebSocket connection attempt on /ws/twilio from {client_host}")
    handler = TwilioMediaStreamHandler(websocket)
    await handler.run()

# Mount built React Frontend if available
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

