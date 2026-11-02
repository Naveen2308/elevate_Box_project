import logging
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from app.config import settings

logger = logging.getLogger("twilio_service")
logger.setLevel(logging.INFO)

from twilio.twiml.voice_response import VoiceResponse, Connect, Stream, Gather, Say

class TwilioTelephonyService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER
        self._client: Optional[Client] = None

    def get_client(self) -> Optional[Client]:
        if not self._client and self.account_sid and self.auth_token and not self.account_sid.startswith("mock"):
            try:
                self._client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio Client: {e}")
        return self._client

    def generate_twiml_conversation_relay(
        self,
        host: str,
        language: str = "multi",
        welcome_greeting: Optional[str] = None,
        transcription_provider: str = "Deepgram",
        tts_provider: str = "ElevenLabs",
        voice: Optional[str] = None,
        to_number: Optional[str] = None
    ) -> str:
        """
        Generates standard Twilio ConversationRelay TwiML with language='multi',
        automatic STT via Deepgram, and multilingual TTS via ElevenLabs.
        """
        greeting = welcome_greeting or (
            "Hi! I am calling from ElevateBox regarding your interest in building an e-commerce website. "
            "What kind of products are you planning to sell online?"
        )
        # Escape XML characters in greeting
        clean_greeting = (
            greeting.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

        ws_host = host.replace("http://", "").replace("https://", "")
        ws_url = f"wss://{ws_host}/ws/conversation-relay"

        voice_attr = f' voice="{voice}"' if voice else ""
        custom_param = f'\n            <CustomParameter name="to" value="{to_number}" />' if to_number else ""

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <ConversationRelay url="{ws_url}" language="{language}" transcriptionProvider="{transcription_provider}" speechModel="nova-3-general" ttsProvider="{tts_provider}" ignoreBackchannel="true"{voice_attr} welcomeGreeting="{clean_greeting}">{custom_param}
            <Language code="te" transcriptionProvider="{transcription_provider}" ttsProvider="{tts_provider}" />
            <Language code="hi" transcriptionProvider="{transcription_provider}" ttsProvider="{tts_provider}" />
            <Language code="en" transcriptionProvider="{transcription_provider}" ttsProvider="{tts_provider}" />
            <Language code="ta" transcriptionProvider="{transcription_provider}" ttsProvider="{tts_provider}" />
            <Language code="kn" transcriptionProvider="{transcription_provider}" ttsProvider="{tts_provider}" />
        </ConversationRelay>
    </Connect>
</Response>"""
        return twiml.strip()

    def generate_twiml_conversation_turn(self, speech_text: str, host: str, language: str = "en-IN", is_end_of_call: bool = False) -> str:
        """
        Generates TwiML that speaks text to caller and accurately gathers caller's spoken speech.
        If is_end_of_call is True, speaks the final farewell and cleanly hangs up the call.
        """
        response = VoiceResponse()
        clean_host = host.replace("http://", "").replace("https://", "").rstrip("/")
        lang_code = language if "-" in language else ("te-IN" if language == "te" else ("hi-IN" if language == "hi" else "en-IN"))
        
        if is_end_of_call:
            response.say(speech_text, language=lang_code)
            response.hangup()
            return str(response)

        # Twilio Gather listens to caller's voice and transcribes in the selected language
        gather = Gather(
            input="speech",
            action=f"https://{clean_host}/api/telephony/gather-response?lang={lang_code}",
            method="POST",
            language=lang_code,
            speech_timeout="auto",
            timeout=5
        )
        gather.say(speech_text, language=lang_code)
        response.append(gather)
        
        # Fallback if silence is detected: redirect back to gather
        response.say("హలో, మీరు మాట్లాడేది వినపడలేదు. దయచేసి మళ్ళీ చెప్పండి.", language=lang_code)
        response.redirect(f"https://{clean_host}/api/telephony/twiml?to=caller")
        return str(response)

    def generate_twiml_gemini_live_stream(self, host: str, to_number: Optional[str] = None) -> str:
        """
        Generates TwiML connecting the live phone call directly to Gemini 3.1 Flash Live
        over Twilio Media Streams (Bidirectional Audio-to-Audio bidiGenerateContent).
        """
        ws_host = host.replace("http://", "").replace("https://", "")
        ws_url = f"wss://{ws_host}/ws/gemini-live"
        custom_param = f'\n            <Parameter name="to" value="{to_number}" />' if to_number else ""
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}">{custom_param}
        </Stream>
    </Connect>
</Response>"""
        return twiml.strip()

    def generate_twiml_stream(self, host: str, language: str = "multi", initial_greeting: Optional[str] = None, is_secure: bool = True, to_number: Optional[str] = None) -> str:
        """
        Generates TwiML connecting the live phone call directly to Gemini 3.1 Flash Live Preview
        over Twilio Media Streams (bidirectional speech-to-speech).
        """
        return self.generate_twiml_gemini_live_stream(host=host, to_number=to_number)

    async def initiate_outbound_call(
        self,
        to_number: str,
        webhook_host: str,
        language: str = "multi",
        caller_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Triggers an autonomous outbound call via Twilio to the lead's phone number using Gemini 3.1 Flash Live.
        """
        client = self.get_client()
        from_phone = caller_id or self.from_number or "+12025550199"
        
        # Clean phone number
        cleaned_to = "".join(filter(str.isdigit, to_number))
        if len(cleaned_to) == 10:
            formatted_to = f"+91{cleaned_to}"
        elif not to_number.startswith("+"):
            formatted_to = f"+{cleaned_to}"
        else:
            formatted_to = to_number

        if client:
            try:
                domain = settings.PUBLIC_URL or webhook_host
                twiml_url = f"https://{domain}/api/telephony/twiml?to={formatted_to}"
                status_url = f"https://{domain}/api/telephony/status"
                
                logger.info(f"Initiating Twilio Gemini Live call -> webhook: {twiml_url}")
                call = client.calls.create(
                    to=formatted_to,
                    from_=from_phone,
                    url=twiml_url,
                    record=False,
                    recording_status_callback=f"https://{domain}/api/telephony/status",
                    status_callback=status_url,
                    status_callback_event=["initiated", "ringing", "answered", "completed"]
                )
                logger.info(f"Twilio Gemini Live Call Initiated: SID={call.sid}, To={formatted_to}")
                return {
                    "success": True,
                    "mode": "LIVE_TWILIO_GEMINI_3_1_FLASH_LIVE",
                    "call_sid": call.sid,
                    "status": call.status,
                    "to": formatted_to,
                    "from": from_phone,
                    "language": "Universal Live"
                }
            except Exception as e:
                logger.error(f"Twilio outbound call error: {e}")
                return {
                    "success": False,
                    "mode": "LIVE_TWILIO_FAILED",
                    "error": str(e),
                    "to": formatted_to
                }
        else:
            # Simulated Call for local testing / sandbox
            sim_sid = f"CA_sim_{cleaned_to}"
            logger.info(f"[SIMULATION] Outbound call placed to {formatted_to} (Gemini 3.1 Flash Live sandbox)")
            return {
                "success": True,
                "mode": "SIMULATED_TEST_CALL",
                "call_sid": sim_sid,
                "status": "in-progress",
                "to": formatted_to,
                "from": from_phone,
                "language": "Universal Live",
                "message": "Call simulated successfully via Gemini 3.1 Flash Live!"
            }

twilio_service = TwilioTelephonyService()
