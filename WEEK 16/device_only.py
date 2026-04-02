import asyncio
import json
import base64
import random
from datetime import datetime, timezone
import websockets

async def setup_device():
    for attempt in range(5): # try retry logic if it fails
        try:
            async with websockets.connect("ws://localhost:3000") as ws:
                print("[DEVICE] Connected, streaming data...")
                bpm = 70
                while True:
                    bpm += random.choice([5, -5])
                    
                    if random.random() < 0.15: # 15% chance of anomaly
                        bpm = 110 # Spiky heart rate!
                    elif random.random() < 0.1:
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
        except Exception as e:
            print("reconnecting...")
            await asyncio.sleep(2)

async def main():
    print("[*] Starting device simulation...")
    await setup_device()

if __name__ == "__main__":
    asyncio.run(main())
