import asyncio
import json
import base64
import random
from datetime import datetime, timezone
import websockets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

KEY = None

def decrypt_payload(b64data: str) -> dict:
    raw = base64.b64decode(b64data)
    iv = raw[:16]
    encrypted_text = raw[16:]
    
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_text) + decryptor.finalize()
    
    pad_len = decrypted_padded[-1]
    decrypted_text = decrypted_padded[:-pad_len].decode('utf-8')
    return json.loads(decrypted_text)

async def setup_listener():
    global KEY
    async with websockets.connect("ws://localhost:3000") as ws:
        print("[LISTENER] Connected to server.")
        await ws.send(json.dumps({"type": "register_listener"}))
        
        async for message in ws:
            payload = json.loads(message)
            if payload.get("type") == "key_exchange":
                KEY = base64.b64decode(payload["key"])
                print("[LISTENER] Received encryption key.")
            elif payload.get("type") == "encrypted_alert":
                print(f"\n[LISTENER] Encrypted Payload Received:\n{payload['data']}")
                if KEY:
                    decrypted = decrypt_payload(payload["data"])
                    print(f"[LISTENER] DECRYPTED CRITICAL ALERT: {json.dumps(decrypted, indent=2)}\n")

async def setup_device():
    await asyncio.sleep(1) # wait for listener connection
    async with websockets.connect("ws://localhost:3000") as ws:
        print("[DEVICE] Connected, streaming data...")
        bpm = 70
        while True:
            bpm += random.choice([5, -5])
            
            if random.random() < 0.15: # 15% chance of anomaly
                bpm = 110 # Spiky heart rate!
            elif random.random() < 0.05:
                bpm = 35 # low
                
            bpm = max(35, min(140, bpm))
            
            payload = {
                "deviceId": "device-py-123",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bpm": bpm
            }
            
            print(f"[DEVICE] Emitting BPM: {bpm}")
            await ws.send(json.dumps(payload))
            await asyncio.sleep(1)

async def main():
    print("[*] Starting simulation...")
    await asyncio.gather(
        setup_listener(),
        setup_device()
    )

if __name__ == "__main__":
    asyncio.run(main())
