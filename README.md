# ElevateBox AI Voice & WhatsApp System

> **Autonomous Multi-Lingual Lead Generation, Intent Classification & Real-Time WhatsApp Engagement Engine**
> *Engineered for ElevateBox (Banjara Hills, Hyderabad) SDE Intern Assignment*

---

## 🌟 Executive Overview & Assignment Checklist

This system dials **`8977155678`** autonomously, speaks fluently in **Telugu, Hindi, or English** (with code-switching), pitches custom e-commerce website development, qualifies the buyer (*budget, products, timeline, features*), classifies the lead (*HOT, WARM, COLD*), and executes real-time actions:
- 🔥 **HOT Lead**: Asynchronously fires a **WhatsApp proposal mid-call** while the call is still ongoing.
- ⚡ **WARM Lead**: Parses natural spoken time (*e.g., "call me back tomorrow morning at 10:30"*) and books the callback.
- ❄️ **COLD Lead**: Logs the conversation politely and offers informational follow-up.
- 📦 **Section 06 Post-Call WhatsApp Package**: Sends a personalized follow-up quoting the caller's specific requirements, candidate's mobile number (`8977155678`), the **System Architecture Diagram**, and candidate **Resume PDF**.

---

## 🏛️ System Architecture Flow

```
                                  [ OUTBOUND CALL TO 8977155678 ]
                                                 │
                                                 ▼
                ┌─────────────────────────────────────────────────────────────────┐
                │          Twilio Voice REST API & Bidirectional Media Streams   │
                └───────────────────────────────┬─────────────────────────────────┘
                                                │ (8kHz μ-law Audio)
                                                ▼
                ┌─────────────────────────────────────────────────────────────────┐
                │       Speech-to-Text: Deepgram Nova-2 / Whisper (En, Te, Hi)   │
                └───────────────────────────────┬─────────────────────────────────┘
                                                │ (Live Transcript Stream)
                                                ▼
                ┌─────────────────────────────────────────────────────────────────┐
                │   Conversation & Intent Engine (Groq Llama 3.3 70B / Gemini 2.0)│
                │     • Multi-lingual Dialogue Management (Telugu / Hindi / En)   │
                │     • Real-time Lead Intent: HOT 🔥 | WARM ⚡ | COLD ❄️          │
                │     • Function Calling & Action Decision System                 │
                └───────┬─────────────────────────────────────────────────┬───────┘
                        │ (TTS Text)                                      │ (Async Tool Events)
                        ▼                                                 ▼
        ┌───────────────────────────────┐               ┌─────────────────────────────────┐
        │  Edge-TTS Voice Generation    │               │  Meta WhatsApp Cloud API v21    │
        │  - Telugu (te-IN-Shruti)      │               │  • MID-CALL: Instant Demo Link  │
        │  - Hindi (hi-IN-Swara)        │               │  • POST-CALL: Quoted Context +  │
        │  - English (en-IN-Neerja)     │               │    Resume PDF + Architecture Img│
        └───────────────┬───────────────┘               └─────────────────────────────────┘
                        │ (Audio Out)
                        ▼
                [ CALLER HEARS RESPONSE ]
```

---

## 💰 100% Free-Tier / Trial Optimization Strategy

| Layer | Technology | Free Tier Benefit |
|---|---|---|
| **Telephony** | **Twilio Voice API** | ~$15.00 Free Trial Credit for Outbound Calls & Media Streams |
| **STT** | **Deepgram Nova-2 / Groq Whisper** | Deepgram $200 free credit / Groq 100% Free High-Throughput API |
| **LLM Engine** | **Groq Llama 3.3 70B / Gemini 2.0** | 100% Free tier (sub-200ms time-to-first-token & native tool use) |
| **Voice (TTS)** | **Edge-TTS (Neural Voices)** | 100% Free, zero-cost, natural Indian Telugu, Hindi & English voices |
| **WhatsApp API** | **Meta WhatsApp Cloud API** | 1,000 free service conversations / month + Free Developer Test Number |
| **Control Dashboard**| **React + Vite (Single Binary / Server)** | Included directly in FastAPI backend on `http://localhost:8000` |

---

## 🚀 Quickstart & Running Locally

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Optional for UI dev; pre-built bundle is served automatically)

### 2. Install Dependencies
```powershell
# Backend Dependencies
python -m pip install -r backend\requirements.txt

# Frontend Dependencies (if building from source)
cd frontend
npm install
npm run build
cd ..
```

### 3. Launch System
```powershell
python run.py
```

Open your browser at **`http://localhost:8000`**.

---

## 🎯 Testing the Assignment Capabilities

1. **Autonomous Call Dialing**:
   - Enter `8977155678` and click **"Dial via Twilio"** or **"Web Voice Call"**.
2. **Language Handling & Code-Switching**:
   - Speak in Telugu (*"Namaskaram andi! Naku online saree business website kavali, budget 40,000"*).
   - Or speak in Hindi (*"Namaste! Hamare paas electronic products hain, UPI payment chahiye"*).
   - Or speak in English.
   - The AI automatically adapts to the caller's language.
3. **Mid-Call WhatsApp Trigger (HOT Lead)**:
   - Say: *"Send me the demo store link on WhatsApp immediately, our budget is 50k and we want to start in 2 weeks."*
   - Watch the live **Mid-Call WhatsApp banner** ignite instantly while the voice call continues without interruption.
4. **Natural Temporal Callback Scheduling (WARM Lead)**:
   - Say: *"I am in a meeting right now, please call me back tomorrow morning at 11 AM."*
   - The AI acknowledges the timing and books the callback in the scheduler.
5. **Section 06 Post-Call WhatsApp Delivery**:
   - Click **"End Call & Send Summary"** or complete the call.
   - The WhatsApp payload containing quoted caller specifics, candidate phone (`8977155678`), architecture diagram image, and resume PDF is dispatched!

---

## 📁 Repository Structure

```
├── run.py                           # Single-command launcher for whole system
├── ElevateBox_SDE_Intern_Assignment.pdf
├── backend/
│   ├── requirements.txt             # Python dependencies
│   ├── app/
│   │   ├── main.py                  # FastAPI server, REST & WebSocket routes
│   │   ├── config.py                # Environment & credential configuration
│   │   ├── generate_assets.py       # Architecture diagram & resume generator
│   │   ├── telephony/
│   │   │   ├── twilio_service.py    # Outbound dialer & TwiML generator
│   │   │   └── media_stream.py      # Bidirectional WebSocket audio handler
│   │   ├── voice/
│   │   │   └── tts_service.py       # Edge-TTS multilingual neural synthesizer
│   │   ├── agent/
│   │   │   ├── conversation_engine.py # Sales dialogue manager & tool calling
│   │   │   └── decision_classifier.py # Lead Intent Classifier (HOT/WARM/COLD)
│   │   ├── whatsapp/
│   │   │   └── cloud_api.py         # Meta WhatsApp Cloud API dispatcher
│   │   ├── scheduler/
│   │   │   └── callback_service.py  # Spoken time dateparser & booking store
│   │   └── static/
│   │       ├── architecture_diagram.png # System Architecture Diagram
│   │       └── resume.pdf           # Candidate Resume
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx                  # Main React dashboard application
        ├── index.css                # Glassmorphic dark-mode design system
        └── components/
            ├── Header.jsx           # Top branding and connection state
            ├── CallControlPanel.jsx # Telephony & Web Voice dialer
            ├── LiveConsole.jsx      # Live audio waveforms & transcript stream
            ├── LeadMatrix.jsx       # Intent qualification matrix & badge
            ├── WhatsAppFeed.jsx     # WhatsApp Cloud API payload inspector
            ├── CallbackList.jsx     # Scheduled callback list
            └── ConfigModal.jsx      # API key & settings modal
```
