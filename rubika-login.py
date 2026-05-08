from rubpy import Client as RubikaClient
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SESSION = os.getenv("RUBIKA_SESSION", "rubika_session").strip()

def ensure_session():
    """Ensure session exists, if not create one"""
    session_path = Path(SESSION)
    if session_path.exists() or Path(f"{SESSION}.session").exists() or Path(f"{SESSION}.sqlite").exists():
        return
    
    client = RubikaClient(name=SESSION)
    try:
        client.start()
        print("Login successful.")
    finally:
        try:
            client.disconnect()
        except Exception:
            pass
