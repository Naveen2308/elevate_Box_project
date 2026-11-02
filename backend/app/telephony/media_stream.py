import json
import base64
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from app.config import settings
from app.agent.conversation_engine import conversation_engine
from app.voice.tts_service import tts_service
from app.whatsapp.cloud_api import whatsapp_service

logger = logging.getLogger("media_stream")
logger.setLevel(logging.DEBUG)

# Active connected dashboard sockets for live telemetry broadcast
dashboard_websockets: List[WebSocket] = []

async def broadcast_to_dashboards(event_type: str, data: Dict[str, Any]):
    message = json.dumps({"event": event_type, "data": data})
    disconnected = []
    for ws in dashboard_websockets:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in dashboard_websockets:
            dashboard_websockets.remove(ws)

class TwilioMediaStreamHandler:
    """
    Handles Twilio bi-directional WebSocket audio streams with detailed real-time logging.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.stream_sid = None
        self.call_sid = None
        self.caller_phone = settings.TARGET_PHONE_NUMBER
        self.history: List[Dict[str, str]] = []
        self.call_active = True
        self.last_qualification = {}
        self.audio_packets_received = 0
        self.audio_packets_sent = 0

    async def run(self):
        await self.websocket.accept()
        print("\n" + "="*70)
        logger.info("🟢 [WEBSOCKET CONNECTED] Twilio WebSocket connection accepted successfully!")
        print("="*70)

        try:
            while self.call_active:
                raw_data = await self.websocket.receive_text()
                message = json.loads(raw_data)
                event = message.get("event")

                if event == "connected":
                    protocol = message.get("protocol", "audio/x-mulaw")
                    version = message.get("version", "1.0.0")
                    logger.info(f"🔗 [EVENT: CONNECTED] Protocol: {protocol} | Version: {version}")

                elif event == "start":
                    start_data = message.get("start", {})
                    self.stream_sid = start_data.get("streamSid")
                    self.call_sid = start_data.get("callSid")
                    account_sid = start_data.get("accountSid")
                    media_format = start_data.get("mediaFormat", {})
                    custom_params = start_data.get("customParameters", {})
                    self.caller_phone = custom_params.get("to", settings.TARGET_PHONE_NUMBER)

                    print("\n" + "#"*70)
                    logger.info(f"🚀 [EVENT: START] Stream SID: {self.stream_sid}")
                    logger.info(f"📞 [EVENT: START] Call SID: {self.call_sid} | To: {self.caller_phone}")
                    logger.info(f"🎙️ [AUDIO FORMAT] Encoding: {media_format.get('encoding')} | Sample Rate: {media_format.get('sampleRate')}Hz | Channels: {media_format.get('channels')}")
                    print("#"*70 + "\n")

                    await broadcast_to_dashboards("CALL_STARTED", {
                        "stream_sid": self.stream_sid,
                        "call_sid": self.call_sid,
                        "caller_phone": self.caller_phone
                    })

                    # Play opening greeting
                    await self._send_greeting()

                elif event == "media":
                    self.audio_packets_received += 1
                    media_data = message.get("media", {})
                    payload_len = len(media_data.get("payload", ""))
                    track = media_data.get("track", "inbound")
                    timestamp = media_data.get("timestamp", "0")

                    # Log periodic audio telemetry every 50 packets (~1 sec) to keep terminal responsive
                    if self.audio_packets_received % 50 == 0:
                        logger.info(f"📥 [AUDIO STREAM INBOUND] Track: {track} | Packets Received: {self.audio_packets_received} | Chunk Size: {payload_len} chars | Timestamp: {timestamp}")

                elif event == "mark":
                    mark_name = message.get("mark", {}).get("name", "unknown")
                    logger.info(f"📍 [EVENT: MARK COMPLETED] Audio playback mark reached: '{mark_name}'")

                elif event == "stop":
                    logger.info(f"🛑 [EVENT: STOP] Twilio Stream Ended. Total Inbound Packets: {self.audio_packets_received}")
                    self.call_active = False
                    await self._handle_call_ended()
                    break

                else:
                    logger.debug(f"ℹ️ [TWILIO RAW EVENT]: {message}")

        except WebSocketDisconnect:
            logger.warning(f"⚠️ [WEBSOCKET DISCONNECTED] Client closed connection for Call SID: {self.call_sid}")
        except Exception as e:
            logger.error(f"❌ [MEDIA STREAM ERROR] Exception occurred: {str(e)}", exc_info=True)
        finally:
            if self.call_active:
                await self._handle_call_ended()

    async def _send_audio_to_twilio(self, text: str, lang: str = "en"):
        """
        Synthesizes TTS audio and streams it directly to Twilio over WebSocket so the caller hears it!
        """
        try:
            logger.info(f"🔊 [SENDING AUDIO TO CALLER] Synthesizing speech for Twilio: \"{text[:60]}...\"")
            # 1. Synthesize audio bytes
            audio_bytes, detected_lang = await tts_service.synthesize_speech_bytes(text, lang=lang)
            
            # 2. Twilio Media Streams format: Base64 payload in 'media' event
            # Convert audio to chunks and send to Twilio
            b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Send media payload to Twilio WebSocket
            media_message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": b64_audio
                }
            }
            await self.websocket.send_text(json.dumps(media_message))
            
            # Send mark event to track completion
            mark_message = {
                "event": "mark",
                "streamSid": self.stream_sid,
                "mark": {
                    "name": f"greeting_{self.audio_packets_sent}"
                }
            }
            await self.websocket.send_text(json.dumps(mark_message))
            logger.info(f"✅ [AUDIO SENT TO TWILIO] Streamed {len(audio_bytes)} bytes of audio payload to phone call.")
        except Exception as e:
            logger.error(f"Failed streaming audio to Twilio: {e}")

    async def _send_greeting(self):
        greeting_text = (
            "Hi! I am calling from ElevateBox regarding your interest in building an e-commerce website. "
            "What kind of products are you planning to sell online?"
        )
        self.history.append({"role": "assistant", "content": greeting_text})
        
        logger.info(f"🗣️ [AI GREETING]: \"{greeting_text}\"")
        await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
            "speaker": "AI",
            "text": greeting_text,
            "language": "en",
            "role": "assistant"
        })
        # Stream greeting audio to the caller's phone!
        await self._send_audio_to_twilio(greeting_text, lang="en")

    async def _handle_call_ended(self):
        """
        Fires the mandatory post-call WhatsApp summary to the caller when the call completes.
        """
        logger.info(f"🏁 [CALL COMPLETED] Generating post-call WhatsApp summary for: {self.caller_phone}")
        full_text = " ".join([turn.get("content", "") for turn in self.history])

        context = {
            "caller_quotes": self.last_qualification.get("caller_quotes", "Interested in e-commerce website development"),
            "products": self.last_qualification.get("products", "E-commerce Storefront"),
            "features": self.last_qualification.get("features", "UPI Payments, Instant Checkout & Automated Shipping"),
            "budget": self.last_qualification.get("budget", "Flexible"),
            "timeline": self.last_qualification.get("timeline", "2-3 Weeks"),
            "intent": self.last_qualification.get("intent", "WARM")
        }

        # Send post-call WhatsApp package
        asyncio.create_task(
            whatsapp_service.send_postcall_summary(
                to_phone=self.caller_phone,
                conversation_context=context,
                candidate_phone=settings.CANDIDATE_PHONE
            )
        )

        await broadcast_to_dashboards("CALL_ENDED", {
            "stream_sid": self.stream_sid,
            "caller_phone": self.caller_phone,
            "context": context
        })
