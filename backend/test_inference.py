import asyncio
from llama_cpp_client import chat

async def main():
    print("[..] Starting test chat completion with ATLAS...")
    # Test a simple prompt to make sure it loads and outputs structured JSON
    message = "Where are the op camping zones?"
    map_context = {}
    
    try:
        result = await chat(message, map_context)
        print("\n[OK] Inference succeeded!")
        print("ATLAS Response:")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n[ERR] Inference failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
