import json
import base64
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from app.config import settings
from app.agent.conversation_engine import conversation_engine
from app.voice.tts_service import tts_service
from app.whatsapp.cloud_api import whatsapp_service
from app.telephony.media_stream import broadcast_to_dashboards

logger = logging.getLogger("gemini_live_stream")
logger.setLevel(logging.INFO)

class GeminiLiveStreamHandler:
    """
    Handles Twilio Media Stream bi-directional audio bridge for Gemini Live / GenAI conversation.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.caller_phone: str = settings.TARGET_PHONE_NUMBER
        self.history: List[Dict[str, str]] = []
        self.call_active = True
        self.last_qualification: Dict[str, Any] = {}
        self.audio_packets_received = 0
        self.audio_packets_sent = 0

    async def run(self):
        try:
            logger.info("🟢 [GEMINI LIVE HANDLER]: Starting Media Stream handler loop")
            while self.call_active:
                raw_data = await self.websocket.receive_text()
                message = json.loads(raw_data)
                event = message.get("event")

                if event == "connected":
                    logger.info("🔗 [GEMINI LIVE]: Twilio Media Stream connected")

                elif event == "start":
                    start_data = message.get("start", {})
                    self.stream_sid = start_data.get("streamSid")
                    self.call_sid = start_data.get("callSid")
                    custom_params = start_data.get("customParameters", {})
                    if "caller_phone" in custom_params:
                        self.caller_phone = custom_params["caller_phone"]

                    logger.info(f"🚀 [GEMINI LIVE START]: StreamSID: {self.stream_sid} | CallSID: {self.call_sid} | To: {self.caller_phone}")
                    await broadcast_to_dashboards("CALL_STARTED", {
                        "stream_sid": self.stream_sid,
                        "call_sid": self.call_sid,
                        "caller_phone": self.caller_phone
                    })

                    # Send opening greeting
                    greeting = await conversation_engine.generate_opening_greeting()
                    self.history.append({"role": "assistant", "content": greeting})
                    await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
                        "speaker": "AI",
                        "text": greeting,
                        "language": "Universal",
                        "role": "assistant"
                    })

                elif event == "media":
                    self.audio_packets_received += 1
                    # In standard Twilio stream, audio chunks arrive here

                elif event == "stop":
                    logger.info(f"🛑 [GEMINI LIVE STOP]: Call ended for {self.caller_phone}")
                    self.call_active = False
                    # Auto trigger post-call Section 06 WhatsApp package
                    asyncio.create_task(
                        whatsapp_service.send_postcall_summary(
                            to_phone=self.caller_phone,
                            conversation_context=self.last_qualification
                        )
                    )
                    await broadcast_to_dashboards("CALL_ENDED", {
                        "caller_phone": self.caller_phone,
                        "call_sid": self.call_sid
                    })
                    break

        except WebSocketDisconnect:
            logger.info("Twilio Media Stream WebSocket disconnected.")
        except Exception as e:
            logger.error(f"Error in GeminiLiveStreamHandler: {e}")
