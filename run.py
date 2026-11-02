import os
import sys
import uvicorn

if __name__ == "__main__":
    # Ensure backend directory is in sys.path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    print("=" * 70)
    print("🚀 ELEVATEBOX AI VOICE & WHATSAPP ENGAGEMENT ENGINE")
    print("📍 Banjara Hills, Hyderabad | SDE Intern Assignment")
    print("=" * 70)
    print("🌐 Dashboard UI & API: http://localhost:8000")
    print("📞 Target Phone Number: 8977155678")
    print("=" * 70)

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=backend_dir)
