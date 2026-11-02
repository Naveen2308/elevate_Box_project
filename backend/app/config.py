import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Explicitly load .env from project root and backend dir
root_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "backend" / ".env")
load_dotenv()

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "ElevateBox AI Voice & WhatsApp System"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    BASE_URL: str = "http://localhost:8000"
    PUBLIC_URL: Optional[str] = None  # Ngrok / Cloudflare Tunnel URL for Twilio Webhooks

    # Candidate Information (ElevateBox Assignment)
    CANDIDATE_NAME: str = "SDE Intern Candidate"
    CANDIDATE_PHONE: str = "8977155678"  # Replace or customize via .env / UI
    CANDIDATE_EMAIL: str = "candidate@elevatebox.com"
    CANDIDATE_RESUME_URL: Optional[str] = "/static/resume.pdf"
    ARCHITECTURE_DIAGRAM_URL: Optional[str] = "/static/architecture_diagram.png"

    # Target Call Number (Default: ElevateBox Lead)
    TARGET_PHONE_NUMBER: str = "8977155678"

    # Twilio Telephony Credentials
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER", "")

    # Meta WhatsApp Cloud API Credentials
    WHATSAPP_TOKEN: Optional[str] = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v21.0")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "elevatebox_webhook_verify_token_2026")

    # LLM & AI Providers (Free Tier: Groq / Gemini)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    DEEPGRAM_API_KEY: Optional[str] = os.getenv("DEEPGRAM_API_KEY", "")

    # Speech Synthesis Preferences
    DEFAULT_VOICE_LANGUAGE: str = "en"  # "en", "te", "hi"
    DEFAULT_VOICE_GENDER: str = "female"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
