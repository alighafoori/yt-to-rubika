import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
from rubpy import Client as RubikaClient

load_dotenv()

SESSION = os.getenv("RUBIKA_SESSION", "rubika_session").strip()
TARGET = "me"
DATA_DIR = Path("./data")


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


def upload_file(file_path: str, caption: str = ""):
    """Upload a single file to Rubika"""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    client = RubikaClient(name=SESSION)
    try:
        client.start()
        print(f"Uploading: {file_path} {caption}")
        result = client.send_document(TARGET, file_path, caption=caption or "")
        print(f"Uploaded: {file_path}")
        return result
    except Exception as e:
        print(f"Upload failed: {e}")
        raise  # Re-raise the error so the caller knows it failed
    finally:
        try:
            client.disconnect()
        except Exception:
            pass


def upload_all_files():
    """Upload all files in ./data folder one by one"""
    if not DATA_DIR.exists():
        print(f"Folder not found: {DATA_DIR}")
        return
    
    files = [f for f in DATA_DIR.iterdir() if f.is_file()]
    
    if not files:
        print("No files found in ./data")
        return
    
    ensure_session()
    
    for index, file_path in enumerate(files, 1):
        try:
            # Create simple numbered filename with original extension
            original_name = file_path.stem
            extension = file_path.suffix
            clean_name = f"{index}{extension}"
            
            # Create temp copy with numbered name
            temp_path = file_path.with_name(clean_name)
            shutil.copy2(file_path, temp_path)
            
            try:
                # Use original filename as caption
                upload_file(str(temp_path), caption=original_name)
                file_path.unlink()  # Delete original file after successful upload
                print(f"Deleted original: {file_path.name}")
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
                
        except Exception as e:
            print(f"Failed to upload {file_path.name}: {e}")


if __name__ == "__main__":
    upload_all_files()