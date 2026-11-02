import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.config import settings
from app.agent.conversation_engine import conversation_engine
from app.whatsapp.cloud_api import whatsapp_service
from app.scheduler.callback_service import callback_service
from app.telephony.media_stream import broadcast_to_dashboards

logger = logging.getLogger("conversation_relay")
logger.setLevel(logging.INFO)

class TwilioConversationRelayHandler:
    """
    Handles Twilio ConversationRelay WebSocket sessions with:
    - language="multi"
    - transcriptionProvider="Deepgram" (Automatic STT Language Detection)
    - ttsProvider="ElevenLabs" (Multilingual TTS Generation)
    - Multilingual & Code-Switching AI Conversational Intelligence
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.session_id: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.caller_phone: str = settings.TARGET_PHONE_NUMBER
        self.history: List[Dict[str, str]] = []
        self.call_active = True
        self.last_qualification: Dict[str, Any] = {}
        
        # Language state tracking with tolerance for noise/short utterances
        self.current_language: str = "multi"
        self.previous_language: Optional[str] = None
        self.detected_languages_history: List[str] = []
        self.code_switch_count: int = 0

    async def run(self):
        await self.websocket.accept()
        print("\n" + "="*70)
        logger.info("🟢 [CONVERSATION RELAY CONNECTED] Twilio ConversationRelay WebSocket accepted!")
        print("="*70)

        try:
            while self.call_active:
                raw_data = await self.websocket.receive_text()
                message = json.loads(raw_data)
                msg_type = message.get("type")

                if msg_type == "setup":
                    await self._handle_setup(message)

                elif msg_type == "prompt":
                    await self._handle_prompt(message)

                elif msg_type == "interrupt":
                    await self._handle_interrupt(message)

                elif msg_type == "end" or msg_type == "stop":
                    logger.info(f"🛑 [EVENT: {msg_type.upper()}] ConversationRelay session terminated by Twilio.")
                    self.call_active = False
                    await self._handle_call_ended()
                    break

                else:
                    logger.debug(f"ℹ️ [CONVERSATION RELAY EVENT]: {message}")

        except WebSocketDisconnect:
            logger.warning(f"⚠️ [RELAY DISCONNECTED] Client closed connection for Call SID: {self.call_sid}")
        except Exception as e:
            logger.error(f"❌ [RELAY ERROR] Exception in ConversationRelay handler: {str(e)}", exc_info=True)
        finally:
            if self.call_active:
                await self._handle_call_ended()

    async def _handle_setup(self, message: Dict[str, Any]):
        """
        Processes Twilio ConversationRelay 'setup' event.
        Extracts call SID, session ID, caller and recipient numbers.
        """
        self.session_id = message.get("sessionId")
        self.call_sid = message.get("callSid")
        from_number = message.get("from", "")
        to_number = message.get("to", "")
        custom_params = message.get("customParameters", {})

        if to_number and not to_number.startswith("+1605"):
            self.caller_phone = to_number
        elif from_number and not from_number.startswith("+1605"):
            self.caller_phone = from_number
        else:
            self.caller_phone = custom_params.get("to", settings.TARGET_PHONE_NUMBER)

        print("\n" + "#"*70)
        logger.info(f"🚀 [RELAY SETUP] Session ID: {self.session_id} | Call SID: {self.call_sid}")
        logger.info(f"📞 [RELAY SETUP] Caller Phone: {self.caller_phone}")
        print("#"*70 + "\n")

        await broadcast_to_dashboards("CALL_STARTED", {
            "session_id": self.session_id,
            "call_sid": self.call_sid,
            "caller_phone": self.caller_phone,
            "mode": "CONVERSATION_RELAY_MULTI"
        })

    async def _handle_prompt(self, message: Dict[str, Any]):
        """
        Processes Twilio/Deepgram transcribed user speech.
        Extracts voicePrompt and detected BCP-47 language tag (e.g., 'en', 'te', 'hi').
        Feeds transcript and detected language into LLM code-switching engine.
        """
        voice_prompt = message.get("voicePrompt", "").strip()
        detected_lang = message.get("lang", "multi")  # Primary BCP-47 tag from Deepgram, e.g. "en", "te", "hi"
        confidence = message.get("confidence", 1.0)

        print("\n" + "="*70)
        logger.info(f"🎙️ [DEEPGRAM STT PROMPT]: \"{voice_prompt}\"")
        logger.info(f"🌐 [DETECTED PRIMARY LANG]: {detected_lang} (Confidence: {confidence})")
        print("="*70 + "\n")

        # Track language switches & code-switching frequency
        if detected_lang and detected_lang != self.current_language:
            self.previous_language = self.current_language
            self.current_language = detected_lang
            self.code_switch_count += 1
            logger.info(f"🔀 [LANGUAGE SWITCH DETECTED]: {self.previous_language} ➔ {self.current_language} (Count: {self.code_switch_count})")

        self.detected_languages_history.append(detected_lang)

        # Broadcast caller speech to dashboard
        await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
            "speaker": "USER",
            "text": voice_prompt or "...",
            "language": detected_lang,
            "role": "user"
        })

        # Process turn with Pure AI Conversational Engine (Universal Omnilingual)
        turn_result = await conversation_engine.process_turn(
            conversation_history=self.history,
            latest_utterance=voice_prompt,
            caller_phone=self.caller_phone,
            detected_language=detected_lang
        )

        ai_reply = turn_result.get("speech_response", "Sure, I understand. Let's discuss your e-commerce requirements.")
        reply_lang = turn_result.get("language_detected", detected_lang)
        self.last_qualification = turn_result.get("qualification", self.last_qualification)

        # Append to conversation history
        self.history.append({"role": "user", "content": voice_prompt})
        self.history.append({"role": "assistant", "content": ai_reply})

        print("\n" + "#"*70)
        logger.info(f"🤖 [AI MULTILINGUAL REPLY]: \"{ai_reply}\"")
        logger.info(f"📊 [INTENT & ACTION]: {turn_result.get('intent')} | Action: {turn_result.get('action_trigger')}")
        print("#"*70 + "\n")

        # Broadcast AI response to dashboard
        await broadcast_to_dashboards("TRANSCRIPT_UPDATE", {
            "speaker": "AI",
            "text": ai_reply,
            "language": reply_lang,
            "role": "assistant"
        })

        await broadcast_to_dashboards("TURN_COMPLETED", {
            "speech_response": ai_reply,
            "language_detected": reply_lang,
            "intent": turn_result.get("intent", "WARM"),
            "confidence": turn_result.get("confidence", 0.9),
            "reason": turn_result.get("reason", ""),
            "action_trigger": turn_result.get("action_trigger", "NONE"),
            "qualification": self.last_qualification,
            "midcall_whatsapp_dispatched": turn_result.get("midcall_whatsapp_dispatched", False),
            "callback_scheduled": turn_result.get("callback_scheduled", None)
        })

        # Send response to Twilio ConversationRelay
        # With language="multi", Twilio and ElevenLabs automatically detect the language of the text token
        reply_message = {
            "type": "text",
            "token": ai_reply,
            "last": True,
            "lang": "multi"
        }
        await self.websocket.send_text(json.dumps(reply_message))
        logger.info(f"📤 [SENT TO CONVERSATION RELAY]: text token sent with lang='multi'")

        # Check if call reached its natural conclusion / farewell
        should_end = turn_result.get("end_call", False) or turn_result.get("action_trigger") == "END_CALL"
        if should_end:
            logger.info("📞 [FAREWELL REACHED]: Sending 'end' event to Twilio ConversationRelay.")
            end_message = {
                "type": "end",
                "handoffData": json.dumps({"reason": "call_completed", "intent": turn_result.get("intent")})
            }
            # Give a brief delay for ElevenLabs TTS audio token to finish playing before closing
            await asyncio.sleep(3.0)
            await self.websocket.send_text(json.dumps(end_message))
            self.call_active = False

    async def _handle_interrupt(self, message: Dict[str, Any]):
        """
        Handles caller interruption (barge-in) during AI speech output.
        """
        duration = message.get("durationUntilInterruptMs", "unknown")
        logger.info(f"⚡ [CALLER BARGE-IN / INTERRUPT] Caller interrupted AI after {duration}ms.")
        await broadcast_to_dashboards("INTERRUPT_EVENT", {
            "session_id": self.session_id,
            "durationMs": duration
        })

    async def _handle_call_ended(self):
        """
        Dispatches mandatory post-call WhatsApp summary with lead context, candidate info, and architecture diagram.
        """
        if not self.call_active:
            return
        self.call_active = False

        logger.info(f"🏁 [RELAY CALL ENDED] Generating post-call WhatsApp summary for: {self.caller_phone}")

        context = {
            "caller_quotes": self.last_qualification.get("caller_quotes", "Interested in e-commerce website development"),
            "products": self.last_qualification.get("products", "E-commerce Storefront"),
            "features": self.last_qualification.get("features", "UPI Payments, Instant Checkout & Automated Shipping"),
            "budget": self.last_qualification.get("budget", "Flexible"),
            "timeline": self.last_qualification.get("timeline", "2-3 Weeks"),
            "intent": self.last_qualification.get("intent", "WARM")
        }

        # Asynchronously dispatch post-call WhatsApp package
        asyncio.create_task(
            whatsapp_service.send_postcall_summary(
                to_phone=self.caller_phone,
                conversation_context=context,
                candidate_phone=settings.CANDIDATE_PHONE
            )
        )

        await broadcast_to_dashboards("CALL_ENDED", {
            "session_id": self.session_id,
            "call_sid": self.call_sid,
            "caller_phone": self.caller_phone,
            "context": context
        })
