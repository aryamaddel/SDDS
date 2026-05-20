import os
import sys
import urllib.request

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
DEST_PATH = os.path.join(DEST_DIR, "qwen2.5-3b-instruct-q4_k_m.gguf")

def progress_callback(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = min(100, (downloaded / total_size) * 100) if total_size > 0 else 0
    downloaded_mb = downloaded / (1024 * 1024)
    total_mb = total_size / (1024 * 1024) if total_size > 0 else 0
    sys.stdout.write(f"\rDownloading Qwen2.5-3B-Instruct GGUF: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)...")
    sys.stdout.flush()

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    if os.path.exists(DEST_PATH):
        print(f"Model already exists at {DEST_PATH}")
        return
    print(f"Source URL: {MODEL_URL}")
    print(f"Destination: {DEST_PATH}")
    print("\nThis file is ~2.2 GB. The download might take a few minutes depending on your internet connection.")
    try:
        urllib.request.urlretrieve(MODEL_URL, DEST_PATH, progress_callback)
        print("\n\n[OK] Model download completed successfully!")
    except KeyboardInterrupt:
        print("\n\n[!] Download cancelled by user.")
        if os.path.exists(DEST_PATH):
            try:
                os.remove(DEST_PATH)
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERR] Failed to download model: {e}")
        if os.path.exists(DEST_PATH):
            try:
                os.remove(DEST_PATH)
            except Exception:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()
