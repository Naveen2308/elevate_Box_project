import httpx
import logging
import asyncio
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger("whatsapp_cloud_api")
logger.setLevel(logging.INFO)

# In-memory store for WhatsApp dispatch events so the Web Dashboard can inspect logs in real-time
whatsapp_dispatch_logs: List[Dict[str, Any]] = []

class WhatsAppCloudAPIService:
    def __init__(self):
        self.api_version = settings.WHATSAPP_API_VERSION or "v21.0"
        self.token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    @property
    def endpoint(self) -> str:
        version = settings.WHATSAPP_API_VERSION or "v21.0"
        pid = self.phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        return f"https://graph.facebook.com/{version}/{pid}/messages"

    def _normalize_phone_number(self, phone: str) -> str:
        """Sanitizes and normalizes phone number to E.164 without leading plus."""
        cleaned = "".join(filter(str.isdigit, str(phone)))
        # Default to Indian country code +91 if 10 digits
        if len(cleaned) == 10:
            return f"91{cleaned}"
        elif len(cleaned) == 12 and cleaned.startswith("91"):
            return cleaned
        elif len(cleaned) == 11 and cleaned.startswith("1"):
            return cleaned
        return cleaned or "918977155678"

    async def send_text_message(self, to_phone: str, body: str) -> Dict[str, Any]:
        """Sends a text message via Meta WhatsApp Cloud API."""
        formatted_phone = self._normalize_phone_number(to_phone)
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {"preview_url": True, "body": body}
        }
        return await self._dispatch_request(payload, log_type="TEXT_MESSAGE")

    async def send_template_message(
        self,
        to_phone: str,
        template_name: str = "jaspers_market_order_confirmation_v1",
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Sends an approved WhatsApp Template message via Meta Cloud API.
        Used for business-initiated conversations outside the 24h customer support window.
        """
        formatted_phone = self._normalize_phone_number(to_phone)
        template_obj: Dict[str, Any] = {
            "name": template_name,
            "language": {"code": language_code}
        }
        if components:
            template_obj["components"] = components

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "template",
            "template": template_obj
        }
        return await self._dispatch_request(payload, log_type=f"TEMPLATE_{template_name.upper()}")

    async def send_media_message(
        self,
        to_phone: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an image or document via Meta WhatsApp Cloud API.
        media_type: 'image' or 'document'
        """
        formatted_phone = self._normalize_phone_number(to_phone)
        media_object: Dict[str, Any] = {"link": media_url}
        if caption:
            media_object["caption"] = caption
        if filename and media_type == "document":
            media_object["filename"] = filename

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": media_type,
            media_type: media_object
        }
        return await self._dispatch_request(payload, log_type=f"MEDIA_{media_type.upper()}")

    async def send_midcall_hot_lead_proposal(self, to_phone: str, lead_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Triggered asynchronously while caller is still on the phone with HIGH BUYING INTENT (HOT Lead).
        """
        products = lead_details.get("products", "your custom product catalog")
        budget = lead_details.get("budget", "as discussed")
        timeline = lead_details.get("timeline", "standard delivery")
        features = lead_details.get("features", "UPI Payments, Instant Checkout & Mobile Optimized")

        msg = (
            f"⚡ *ElevateBox Instant Proposal & Demo Link*\n\n"
            f"Hi! While we are on this call, here is the immediate e-commerce launch blueprint for *{products}*:\n\n"
            f"• *Features Discussed*: {features}\n"
            f"• *Target Timeline*: {timeline}\n"
            f"• *Budget Alignment*: {budget}\n\n"
            f"🔗 *Live Demo Store*: https://elevatebox-demo-store.vercel.app\n"
            f"📄 *Instant Portfolio*: https://elevatebox.com/case-studies\n\n"
            f"Let's finalize the next steps on the call right now!"
        )

        # 1. Send approved Template message to open the conversation window on the user's phone
        template_res = await self.send_template_message(
            to_phone=to_phone,
            template_name="jaspers_market_order_confirmation_v1",
            language_code="en_US",
            components=[{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Hot Lead Proposal"},
                    {"type": "text", "text": f"ELEVATE-{self._normalize_phone_number(to_phone)[-4:]}"},
                    {"type": "text", "text": "Instant Demo"}
                ]
            }]
        )
        
        # 2. Also send rich proposal text
        text_res = await self.send_text_message(to_phone, msg)
        logger.info(f"🔥 Mid-call WhatsApp fired for HOT lead {to_phone} (Template: {template_res.get('status_code')}, Text: {text_res.get('status_code')})")
        return template_res

    async def send_postcall_summary(
        self,
        to_phone: str,
        conversation_context: Dict[str, Any],
        candidate_phone: str = settings.CANDIDATE_PHONE,
        diagram_url: Optional[str] = None,
        resume_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends the mandatory Section 06 Post-Call WhatsApp package:
        1. Context of call quoting what was actually said (budget, timeline, features, products)
        2. Proper human framing (written like a real person follow-up)
        3. Candidate mobile number clearly visible
        4. Architecture diagram image
        5. Resume PDF / download link
        """
        caller_quotes = conversation_context.get("caller_quotes", "e-commerce website development requirements")
        budget = conversation_context.get("budget", "Not specified")
        timeline = conversation_context.get("timeline", "Not specified")
        products = conversation_context.get("products", "General inventory")
        features = conversation_context.get("features", "Standard e-commerce features")
        intent = conversation_context.get("intent", "WARM")

        # Human-crafted personalized follow-up narrative quoting caller requirements
        message_body = (
            f"Hi! Thank you for taking the time to speak with our AI system today.\n\n"
            f"Here is a summary of what we discussed for your upcoming e-commerce project:\n\n"
            f"📌 *Your Requirements & Specifics:*\n"
            f"• *Products/Category*: {products}\n"
            f"• *Key Features*: {features}\n"
            f"• *Stated Budget*: {budget}\n"
            f"• *Target Timeline*: {timeline}\n"
            f"• *Conversation Notes*: \"{caller_quotes}\"\n\n"
            f"💡 *Lead Classification*: {str(intent).upper()}\n\n"
            f"👤 *Candidate Contact Information:*\n"
            f"• *Direct Mobile / WhatsApp*: +91 {candidate_phone}\n"
            f"• *Email*: {settings.CANDIDATE_EMAIL}\n\n"
            f"Attached below are:\n"
            f"1️⃣ The System Architecture Diagram showing how this autonomous AI voice & WhatsApp engine is built.\n"
            f"2️⃣ My Resume for the SDE Intern role at ElevateBox.\n\n"
            f"Looking forward to connecting with you!"
        )

        results = []
        # 1. Send approved Template message to open the conversation window on the user's phone
        tmpl_res = await self.send_template_message(
            to_phone=to_phone,
            template_name="jaspers_market_order_confirmation_v1",
            language_code="en_US",
            components=[{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Post-Call Summary"},
                    {"type": "text", "text": f"ELEVATE-{self._normalize_phone_number(to_phone)[-4:]}"},
                    {"type": "text", "text": "Resume & Diagram Attached"}
                ]
            }]
        )
        results.append(tmpl_res)

        # 2. Send Main Context Text
        t_res = await self.send_text_message(to_phone, message_body)
        results.append(t_res)

        # Helper to construct public HTTPS URLs for media attachments
        def get_media_url(sub_path: str) -> str:
            if settings.PUBLIC_URL:
                p_host = settings.PUBLIC_URL.replace("http://", "").replace("https://", "")
                return f"https://{p_host}{sub_path}"
            return f"{settings.BASE_URL}{sub_path}"

        # 2. Send Architecture Diagram Image
        diag_path = diagram_url or get_media_url(settings.ARCHITECTURE_DIAGRAM_URL or "/static/architecture_diagram.png")
        try:
            img_res = await self.send_media_message(
                to_phone=to_phone,
                media_type="image",
                media_url=diag_path,
                caption="ElevateBox AI Voice & WhatsApp System Architecture Flow"
            )
            results.append(img_res)
        except Exception as e:
            logger.error(f"Failed sending architecture image: {e}")

        # 3. Send Resume PDF
        res_path = resume_url or get_media_url(settings.CANDIDATE_RESUME_URL or "/static/resume.pdf")
        try:
            pdf_res = await self.send_media_message(
                to_phone=to_phone,
                media_type="document",
                media_url=res_path,
                caption="SDE Intern Resume - ElevateBox Assignment",
                filename="SDE_Intern_Resume.pdf"
            )
            results.append(pdf_res)
        except Exception as e:
            logger.error(f"Failed sending resume PDF: {e}")

        return {"status": "success", "dispatched_items": results}

    async def _dispatch_request(self, payload: Dict[str, Any], log_type: str) -> Dict[str, Any]:
        """
        Dispatches request to Meta WhatsApp Cloud API or logs to sandbox if credentials are mock/test.
        """
        current_token = self.token or settings.WHATSAPP_TOKEN
        current_pid = self.phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID

        headers = {
            "Authorization": f"Bearer {current_token}",
            "Content-Type": "application/json"
        }

        # Check if live Meta WhatsApp credentials are configured
        is_live_configured = bool(current_token and current_pid and not current_token.startswith("mock"))

        response_data = {}
        status_code = 200

        if is_live_configured:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(self.endpoint, headers=headers, json=payload)
                    status_code = resp.status_code
                    try:
                        response_data = resp.json()
                    except Exception:
                        response_data = {"raw": resp.text}
                    logger.info(f"Meta WhatsApp Cloud API response ({status_code}): {response_data}")
            except Exception as exc:
                logger.error(f"Meta WhatsApp Cloud API error: {exc}")
                status_code = 500
                response_data = {"error": str(exc)}
        else:
            # Sandbox / Simulation Mode
            response_data = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": payload.get("to"), "wa_id": payload.get("to")}],
                "messages": [{"id": f"wamid_sim_{len(whatsapp_dispatch_logs) + 1}"}],
                "mode": "Sandbox / Simulation Mode"
            }

        log_entry = {
            "id": len(whatsapp_dispatch_logs) + 1,
            "timestamp": asyncio.get_event_loop().time(),
            "type": log_type,
            "recipient": payload.get("to"),
            "payload": payload,
            "status_code": status_code,
            "response": response_data,
            "is_live": is_live_configured
        }
        whatsapp_dispatch_logs.insert(0, log_entry)
        return log_entry

whatsapp_service = WhatsAppCloudAPIService()
