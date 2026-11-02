import os
from PIL import Image, ImageDraw, ImageFont

def generate_architecture_diagram():
    width, height = 1200, 800
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # Draw grid lines for high-tech aesthetic
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill="#1E293B", width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill="#1E293B", width=1)

    # Helper function to draw rounded boxes
    def draw_box(x1, y1, x2, y2, bg_color, border_color, title, subtitle="", tags=[]):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=bg_color, outline=border_color, width=2)
        draw.text((x1 + 20, y1 + 16), title, fill="#FFFFFF")
        if subtitle:
            draw.text((x1 + 20, y1 + 42), subtitle, fill="#94A3B8")
        offset_y = y1 + 75
        for tag in tags:
            draw.text((x1 + 20, offset_y), f"• {tag}", fill="#38BDF8")
            offset_y += 22

    # Title Header
    draw.text((60, 40), "ELEVATEBOX AI VOICE & WHATSAPP SYSTEM ARCHITECTURE", fill="#38BDF8")
    draw.text((60, 70), "Autonomous Multi-Lingual Lead Generation, Classification & Engagement Engine", fill="#94A3B8")

    # Boxes
    # 1. Telephony Layer
    draw_box(60, 130, 380, 310, "#1E293B", "#38BDF8", "1. Telephony & Audio Bridge", "Twilio Voice REST API & WebSockets", [
        "Autonomous outbound dialer (8977155678)",
        "Bi-directional μ-law 8kHz audio streams",
        "Sub-300ms latency stream pipeline"
    ])

    # 2. STT Layer
    draw_box(440, 130, 760, 310, "#1E293B", "#818CF8", "2. Real-Time Speech-to-Text", "Deepgram Nova-2 / Whisper", [
        "Multi-lingual: Telugu, Hindi, English",
        "Seamless code-switching recognition",
        "Live partial transcription streaming"
    ])

    # 3. Decision & LLM Layer
    draw_box(440, 350, 760, 560, "#1E293B", "#F59E0B", "3. LLM & Conversation Engine", "Groq Llama 3.3 70B / Gemini 2.0", [
        "Natural e-commerce discovery probing",
        "Intent: HOT 🔥 | WARM ⚡ | COLD ❄️",
        "Tool Calling for mid-call actions"
    ])

    # 4. Voice Generation (TTS)
    draw_box(60, 350, 380, 560, "#1E293B", "#10B981", "4. Voice Generation (TTS)", "Edge-TTS Neural Voices", [
        "te-IN-Shruti / Mohan (Telugu)",
        "hi-IN-Swara / Madhur (Hindi)",
        "en-IN-Neerja / Prabhat (English)"
    ])

    # 5. WhatsApp Cloud API
    draw_box(820, 130, 1140, 350, "#1E293B", "#22C55E", "5. Meta WhatsApp Cloud API", "Direct Graph API v21.0", [
        "MID-CALL: Instant Demo & Catalog",
        "POST-CALL: Quoted Context Summary",
        "Candidate Phone, Resume PDF & Diagram"
    ])

    # 6. Callback Scheduler & Dashboard
    draw_box(820, 390, 1140, 560, "#1E293B", "#EC4899", "6. Scheduler & Control Center", "FastAPI + React Dashboard", [
        "Natural temporal dateparser (e.g. 'tomorrow')",
        "Live audio visualizer & transcripts",
        "Lead Matrix & Call Analytics"
    ])

    # Footer note
    draw.rounded_rectangle([60, 600, 1140, 740], radius=10, fill="#0B132B", outline="#475569", width=1)
    draw.text((80, 620), "KEY PERFORMANCE HIGHLIGHTS:", fill="#FCD34D")
    draw.text((80, 650), "✔ Non-blocking Mid-Call WhatsApp dispatch triggered dynamically upon high buyer intent.", fill="#E2E8F0")
    draw.text((80, 675), "✔ Fuzzy date parsing for natural speech callback bookings (e.g. 'tomorrow morning at 11').", fill="#E2E8F0")
    draw.text((80, 700), "✔ 100% Free-Tier & generous trial optimization across all telephony, voice, and LLM services.", fill="#E2E8F0")

    os.makedirs("backend/app/static", exist_ok=True)
    img_path = "backend/app/static/architecture_diagram.png"
    img.save(img_path)
    print(f"Generated architecture diagram at {img_path}")

def generate_sample_resume():
    # Simple valid sample PDF for candidate resume attachment
    os.makedirs("backend/app/static", exist_ok=True)
    resume_path = "backend/app/static/resume.pdf"
    
    # Generate minimal valid PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 130 >>\nstream\nBT\n/F1 20 Tf\n50 720 Td\n(Candidate Resume - SDE Intern ElevateBox) Tj\n/F1 12 Tf\n0 -30 Td\n(Phone: 8977155678 | Role: SDE Intern) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000427 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF\n"
    
    with open(resume_path, "wb") as f:
        f.write(pdf_content)
    print(f"Generated sample resume PDF at {resume_path}")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_sample_resume()
