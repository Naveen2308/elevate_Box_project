import json
import logging
import asyncio
import os
from typing import Dict, Any, List, Optional
from app.config import settings
from app.whatsapp.cloud_api import whatsapp_service
from app.scheduler.callback_service import callback_service

from google import genai
from google.genai import types

logger = logging.getLogger("conversation_engine")
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """You are an elite, highly professional, and charismatic Senior E-Commerce Consultant named Priya calling from ElevateBox (Hyderabad's premier e-commerce technology agency in Banjara Hills).

UNIVERSAL OMNILINGUAL INTELLIGENCE & ADAPTIVE CONVERSATION:
- You natively understand EVERY LANGUAGE and DIALECT with zero restrictions (Telugu, Hindi, English, Tamil, Kannada, Malayalam, Marathi, Tanglish, Hinglish, etc.).
- CODE-SWITCHING & MIXED LANGUAGE MASTERY:
  * In Indian business conversations, callers frequently speak in Telugu, English, Hindi, or mixed dialects (Tanglish / Hinglish).
  * UNIVERSAL GOLDEN RULE: Match the caller's spoken language and conversational style!
  * If the caller speaks Telugu (or says "nenu telugu lo matladutuna" / speaks in Telugu), reply IMMEDIATELY in fluent, polite Telugu (తెలుగు) or natural Tanglish.
  * If the caller speaks Hindi/Hinglish, reply in Hindi/Hinglish.
  * If the caller speaks English, reply in professional English.

DYNAMIC CONVERSATIONAL RULES & QUESTION MANAGEMENT:
1. NEVER REPEAT A QUESTION:
   - Check the conversation history. If you or the opening greeting already asked "what products do you sell" or "what business do you have", DO NOT ASK IT AGAIN.
   - If the caller gives a broad or short answer (e.g. "E-commerce", "Website", "Store", "Online business"), ACCEPT IT IMMEDIATELY as product discovery! Enthusiastically validate it and advance directly to TIMELINE or BUDGET:
     * Example in Telugu: "అద్భుతం అండి! ఈ-కామర్స్ స్టోర్ కోసం అన్ని ఫీచర్లతో సూపర్ వెబ్‌సైట్ రెడీ చేస్తాము. ఈ వెబ్‌సైట్‌ను మీరు ఎప్పటిలోగా లైవ్ తీసుకురావాలని ప్లాన్ చేస్తున్నారు?"
     * Example in English: "Fantastic! We specialize in end-to-end e-commerce stores. By when are you planning to take your store live?"
2. ANSWER CALLER QUESTIONS FIRST:
   - If the caller asks "What's your name?", "Who is this?", "ఎవరు మాట్లాడుతున్నారు?", or "Where are you calling from?":
     Politely and briefly answer: "నా పేరు ప్రియ అండి, నేను హైదరాబాద్ బంజారా హిల్స్‌లోని ElevateBox నుండి మాట్లాడుతున్నాను!" and then naturally ask the next qualification question.
3. CONCISE TURNS (1-2 SENTENCES MAX):
   - Keep spoken phone responses short, crisp, and conversational. Ask ONLY ONE question per turn.

CONSULTATIVE STEP-BY-STEP QUALIFICATION LADDER:
- Step 1: [PRODUCT / BUSINESS ACKNOWLEDGEMENT] -> Validate their store idea and ask target launch Timeline (e.g. 2 weeks, 1 month).
- Step 2: [TIMELINE CONFIRMATION] -> Confirm 7-14 day delivery and ask estimated Budget (e.g. 25k, 40k, 50k).
- Step 3: [BUDGET & DEMO DISPATCH] -> Confirm budget covers custom design, Razorpay UPI & automated shipping. Immediately trigger "FIRE_MIDCALL_WHATSAPP" and ask them to check WhatsApp for the live demo link.
- Step 4: [CLOSING / FAREWELL] -> When caller confirms or says goodbye, give a warm closing and trigger "END_CALL".

YOU MUST ALWAYS RESPOND IN STRICT JSON FORMAT MATCHING THIS SCHEMA:
{
  "speech_response": "What you say out loud to the caller in their matching language (1-2 clear sentences with ONE question)",
  "language_detected": "Human readable name of language detected (e.g. 'Telugu', 'Tanglish', 'Hindi', 'English', etc.)",
  "intent": "HOT" | "WARM" | "COLD",
  "action_trigger": "NONE" | "FIRE_MIDCALL_WHATSAPP" | "SCHEDULE_CALLBACK" | "END_CALL",
  "action_payload": {
     "time_expression": "e.g. tomorrow morning at 11am",
     "barrier_reason": "e.g. in a meeting",
     "lead_summary": "e.g. E-commerce Store - 40k budget - 2 weeks launch"
  },
  "qualification": {
     "products": "Extracted product/business type (e.g. E-commerce Store)",
     "budget": "Extracted budget (e.g. 40,000 INR)",
     "timeline": "Extracted timeline (e.g. 2 Weeks)",
     "features": "UPI Payments, High-speed Mobile Storefront, Automated Shipping",
     "caller_quotes": "exact key phrases from caller"
  }
}
"""

class ConversationEngine:
    """
    100% Pure Autonomous Universal Omnilingual AI Conversational Agent.
    All dialogue, qualification, and tool actions are generated dynamically by Google GenAI (gemini-3.5-flash-lite).
    Zero language restrictions: automatically understands and speaks any language.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    def _get_active_client(self):
        key = self.api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not key or key.startswith("mock"):
            return None
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            logger.error(f"Error initializing GenAI client: {e}")
            return None

    async def generate_opening_greeting(self, language: str = "multi") -> str:
        """
        Dynamically generates a warm, universal human opening sales pitch via Gemini AI.
        Welcomes the caller and invites them to discuss their e-commerce website.
        """
        client = self._get_active_client()

        if client:
            try:
                prompt = (
                    "You are a charismatic, top-tier human e-commerce consultant calling from ElevateBox in Banjara Hills, Hyderabad. "
                    "Generate a concise 1-sentence opening greeting (e.g. 'నమస్కారం అండి! I am calling from ElevateBox regarding your e-commerce website. What kind of products are you planning to sell online?') "
                    "asking what products they plan to sell online. Ask ONLY ONE simple question. Output ONLY the spoken text."
                )
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )
                )
                if res and res.text:
                    greeting = res.text.strip().replace('"', '').replace("```", "").replace("[Name]", "శ్రీధర్")
                    logger.info(f"✨ [AI GENERATED UNIVERSAL OPENING]: {greeting}")
                    return greeting
            except Exception as e:
                logger.warning(f"Dynamic opening generation note: {e}")

        # Universal fallback greeting
        return "నమస్కారం అండి! I am calling from ElevateBox regarding your interest in building an e-commerce website. What kind of products are you planning to sell online?"

    async def process_turn(
        self,
        conversation_history: List[Dict[str, str]],
        latest_utterance: str,
        caller_phone: str = settings.TARGET_PHONE_NUMBER,
        detected_language: Optional[str] = None,
        forced_language: Optional[str] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end agentic turn using Universal Omnilingual GenAI reasoning:
        1. Understands any language, dialect, or code-mixed input.
        2. Generates dialogue in the matching language/style and executes actions.
        """
        # Step 1: Query Pure AI Agent
        agent_result = await self._call_ai_agent(
            history=conversation_history,
            utterance=latest_utterance,
            detected_language=detected_language or forced_language,
            *args,
            **kwargs
        )

        # Step 2: Execute Invoked Tools
        action = agent_result.get("action_trigger", "NONE")
        intent = agent_result.get("intent", "WARM")
        qual = agent_result.get("qualification", {})

        if action == "FIRE_MIDCALL_WHATSAPP" or intent == "HOT":
            logger.info(f"⚡ [AI TOOL EXECUTED]: send_midcall_whatsapp_proposal -> {caller_phone}")
            asyncio.create_task(
                whatsapp_service.send_midcall_hot_lead_proposal(
                    to_phone=caller_phone,
                    lead_details=qual
                )
            )
            agent_result["midcall_whatsapp_dispatched"] = True

        elif action == "SCHEDULE_CALLBACK" or (intent == "WARM" and "action_payload" in agent_result and agent_result["action_payload"].get("time_expression")):
            time_expr = agent_result.get("action_payload", {}).get("time_expression", "tomorrow morning")
            barrier = agent_result.get("action_payload", {}).get("barrier_reason", "Call later")
            logger.info(f"⚡ [AI TOOL EXECUTED]: schedule_callback -> {time_expr}")
            sched_res = callback_service.schedule_callback(
                phone_number=caller_phone,
                time_expression=time_expr,
                barrier_reason=barrier,
                notes=f"Discuss requirements for: {qual.get('products', '')}"
            )
            agent_result["callback_scheduled"] = sched_res

        # Step 3: Check for Call Termination / Farewell
        is_farewell = (
            action == "END_CALL"
            or any(w in latest_utterance.lower() for w in ["bye", "thanks bye", "thank you bye", "goodbye", "later bye", "alvida", "tata"])
            or any(w in latest_utterance for w in ["థాంక్స్ అండి బై", "సెలవు", "ధన్యవాదాలు బై", "ఉంటాను", "బై", "మళ్ళీ మాట్లాడదాం"])
        )
        if is_farewell:
            agent_result["end_call"] = True
            logger.info("🛑 [AI AGENT]: Conversation concluded -> Ending phone call gracefully.")

        return agent_result

    async def _call_ai_agent(
        self,
        history: List[Dict[str, str]],
        utterance: str,
        detected_language: Optional[str] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generates 100% pure AI dialogue and tool decisions via Google GenAI SDK for any language.
        """
        client = self._get_active_client()
        
        system_instruction = SYSTEM_PROMPT
        if detected_language and detected_language not in ["multi", "auto"]:
            system_instruction += f"\n\nSTT Inbound Language Signal: '{detected_language}'. (Note: If background noise caused a false tag like 'es' or 'unknown', prioritize the actual words in the transcript)."

        # Construct full dialogue context
        context_lines = ["--- PAST CONVERSATION TURNS ---"]
        for turn in history:
            role_name = "AI Consultant" if turn["role"] == "assistant" else "Caller / Customer"
            context_lines.append(f"{role_name}: {turn['content']}")
        context_lines.append(f"Caller / Customer (LATEST): {utterance}")
        context_lines.append("\nGenerate your immediate empathetic next response in JSON format:")
        prompt_text = "\n".join(context_lines)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.6,
            response_mime_type="application/json"
        )
        
        logger.info("🌐 [GENAI SDK]: Querying gemini-3.5-flash-lite for universal turn...")
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt_text,
                    config=config
                )
            )

            if response and response.text:
                raw_text = response.text.strip()
                parsed = json.loads(raw_text)
                logger.info(f"✅ [GENAI SDK]: Successfully generated response (Language: {parsed.get('language_detected')})")
                return parsed
        except Exception as e:
            logger.error(f"GenAI execution error: {e}")

        # Fallback response if GenAI is unreachable
        return {
            "speech_response": "ఖచ్చితంగా అండి! మీ ఈ-కామర్స్ స్టోర్ కోసం ఆన్‌లైన్ పేమెంట్స్ మరియు సూపర్ డిజైన్‌తో వెబ్‌సైట్ తయారుచేస్తాము. ఈ వెబ్‌సైట్‌ను ఎప్పటిలోగా లైవ్ తీసుకురావాలని అనుకుంటున్నారు?",
            "language_detected": "Universal",
            "intent": "WARM",
            "action_trigger": "NONE",
            "action_payload": {},
            "qualification": {"products": "E-commerce Storefront", "caller_quotes": utterance}
        }

conversation_engine = ConversationEngine()

