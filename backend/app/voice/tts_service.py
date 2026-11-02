import re
import io
import asyncio
import logging
from typing import Tuple
import edge_tts
from app.config import settings

logger = logging.getLogger("tts_service")
logger.setLevel(logging.INFO)

# Voice Mappings for natural multi-lingual Indian speech
VOICE_MAP = {
    "te": {
        "female": "te-IN-ShrutiNeural",
        "male": "te-IN-MohanNeural"
    },
    "hi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural"
    },
    "en": {
        "female": "en-IN-NeerjaNeural",
        "male": "en-IN-PrabhatNeural"
    }
}

class TextToSpeechService:
    def __init__(self):
        self.default_gender = settings.DEFAULT_VOICE_GENDER

    def detect_language(self, text: str) -> str:
        """
        Detects Telugu, Hindi, or English from characters or phonetics.
        """
        if not text:
            return "en"

        # Telugu Unicode range
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"
        # Hindi / Devanagari Unicode range
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"

        # Romanized keyword checks for Indian code-switching (Tanglish / Hinglish)
        telugu_keywords = {
            "namaskaram", "cheppandi", "avunu", "miku", "chala", "kavali", "ela",
            "entha", "andi", "naku", "naa", "cheyali", "matladutunnamu", "chesanu", "ayindhi",
            "ayindi", "pampandi", "undi", "undali", "chusi", "kavalanukuntunnamu", "cheddam",
            "meeru", "kuda", "ippude", "chepparu"
        }
        hindi_keywords = {
            "namaste", "boliay", "haan", "aapko", "chahiye", "kitna", "kaise", "theek",
            "shukriya", "kijiye", "karna", "chahta", "hoon", "banwani", "mein", "baje",
            "mujhe", "hum", "karenge", "bhi", "abhi", "kripya"
        }

        text_words = set(re.findall(r'\b\w+\b', text.lower()))
        te_score = len(text_words & telugu_keywords)
        hi_score = len(text_words & hindi_keywords)

        if te_score > 0 or hi_score > 0:
            return "te" if te_score >= hi_score else "hi"

        return "en"

    def get_voice_for_language(self, lang: str, gender: str = "female") -> str:
        lang_key = lang if lang in VOICE_MAP else "en"
        gender_key = gender if gender in ["female", "male"] else "female"
        return VOICE_MAP[lang_key][gender_key]

    async def synthesize_speech_bytes(self, text: str, lang: str = None, gender: str = "female") -> Tuple[bytes, str]:
        """
        Synthesizes text into high-quality MP3 audio bytes using Edge TTS.
        """
        if not lang or lang in ["auto", "multi"]:
            lang = self.detect_language(text)

        voice = self.get_voice_for_language(lang, gender)
        logger.info(f"Synthesizing speech: voice={voice}, lang={lang}, text_len={len(text)}")

        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+5%", pitch="+0Hz")
        
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])

        audio_bytes = audio_stream.getvalue()
        return audio_bytes, lang

    async def synthesize_mulaw_raw(self, text: str, lang: str = None, gender: str = "female") -> Tuple[bytes, str]:
        """
        Synthesizes text and formats directly as 8000Hz mono mu-law audio payload for Twilio telephony.
        """
        mp3_bytes, detected_lang = await self.synthesize_speech_bytes(text, lang, gender)
        
        # Twilio Media Streams accepts 8000Hz 1-channel mulaw (PCMU)
        # We can stream raw chunks or encoded audio bytes directly over WebSocket
        return mp3_bytes, detected_lang

tts_service = TextToSpeechService()

