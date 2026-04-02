import asyncio
import json
import os
import uuid
import base64
from websockets.server import serve
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

THRESHOLDS_BPM_HIGH = 100
THRESHOLDS_BPM_LOW = 40

# Security (in memory for demo)
KEY = os.urandom(32)
IV = os.urandom(16)

def encrypt_payload(payload: dict) -> str:
    # AES-256-CBC with PKCS7 padding
    text = json.dumps(payload).encode('utf-8')
    pad_len = 16 - (len(text) % 16)
    text += bytes([pad_len]) * pad_len
    
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(text) + encryptor.finalize()
    
    # Send iv:encrypted base64 mapped
    combined = IV + encrypted
    return base64.b64encode(combined).decode('utf-8')

alert_clients = set()

def detect_anomaly(data: dict):
    bpm = data.get("bpm")
    if bpm is None:
        return None
        
    reason = ""
    if bpm > THRESHOLDS_BPM_HIGH:
        reason = f"High BPM detected: {bpm}"
    elif bpm < THRESHOLDS_BPM_LOW:
        reason = f"Low BPM detected: {bpm}"
        
    if reason:
        return {
            "alertId": str(uuid.uuid4()),
            "deviceId": data.get("deviceId", "unknown"),
            "timestamp": data.get("timestamp"),
            "severity": "CRITICAL",
            "reason": reason,
            "raw_value": bpm
        }
    return None

async def handler(websocket):
    print(f"[+] New connection established")
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data.get("type") == "register_listener":
                alert_clients.add(websocket)
                print("[*] Registered new alert listener")
                
                await websocket.send(json.dumps({
                    "type": "key_exchange",
                    "key": base64.b64encode(KEY).decode('utf-8')
                }))
                continue
                
            anomaly = detect_anomaly(data)
            
            # Broadcast raw stream for dashboard visualization
            if "bpm" in data:
                raw_payload = json.dumps({
                    "type": "raw_stream",
                    "bpm": data.get("bpm"),
                    "deviceId": data.get("deviceId")
                })
                disconnected = set()
                for client in alert_clients:
                    try:
                        await client.send(raw_payload)
                    except Exception:
                        disconnected.add(client)
                for client in disconnected:
                    alert_clients.remove(client)

            if anomaly:
                print(f"\n[!] Anomaly Detected: {anomaly['reason']}")
                encrypted_alert = encrypt_payload(anomaly)
                notificationPayload = json.dumps({
                    "type": "encrypted_alert",
                    "data": encrypted_alert
                })
                
                disconnected = set()
                for client in alert_clients:
                    try:
                        await client.send(notificationPayload)
                    except Exception:
                        disconnected.add(client)
                
                for client in disconnected:
                    alert_clients.remove(client)
                
    except Exception as e:
        pass
    finally:
        print("[-] Connection closed")
        if websocket in alert_clients:
            alert_clients.remove(websocket)

async def main():
    async with serve(handler, "localhost", 3000):
        print("[*] WebSocket server listening on ws://localhost:3000...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
