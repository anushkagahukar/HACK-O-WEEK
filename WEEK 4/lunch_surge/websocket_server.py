"""
websocket_server.py — WebSocket server that streams simulated real-time
lunch surge readings every second.

Run this SEPARATELY in a second terminal:
    python websocket_server.py
"""

import asyncio
import json
import random
import websockets
from datetime import datetime
import numpy as np

PORT = 8765

LOCATIONS = ["Cafeteria A", "Food Court B", "Restaurant C", "Canteen D"]
WEATHER_CONDITIONS = ["Sunny", "Cloudy", "Rainy", "Windy", "Snowy"]

# Simulate a "current weather" that slowly drifts
current_state = {
    "temperature": 20.0,
    "humidity":    60.0,
    "wind_speed":  10.0,
    "weather":     "Sunny",
    "hour":        12,
}


def next_reading():
    """Generate one simulated sensor reading."""
    global current_state

    # Drift temperature slightly
    current_state["temperature"] += np.random.normal(0, 0.3)
    current_state["temperature"]  = np.clip(current_state["temperature"], -5, 40)
    current_state["humidity"]    += np.random.normal(0, 1)
    current_state["humidity"]     = np.clip(current_state["humidity"], 20, 100)
    current_state["wind_speed"]  += np.random.normal(0, 0.5)
    current_state["wind_speed"]   = max(0, current_state["wind_speed"])

    # Occasionally change weather
    if random.random() < 0.02:
        current_state["weather"] = random.choice(WEATHER_CONDITIONS)

    temp         = current_state["temperature"]
    hour_factor  = np.exp(-0.5 * ((current_state["hour"] - 12.5) / 1.2) ** 2)
    weather_fac  = {"Sunny":1.3,"Cloudy":1.0,"Rainy":0.75,"Windy":0.85,"Snowy":0.6}[current_state["weather"]]

    readings = []
    for loc in LOCATIONS:
        base = {"Cafeteria A":280,"Food Court B":350,"Restaurant C":180,"Canteen D":220}[loc]
        surge = int(base * hour_factor * weather_fac * random.uniform(0.88, 1.12))
        readings.append({
            "timestamp":   datetime.now().strftime("%H:%M:%S"),
            "location":    loc,
            "surge_count": max(0, surge),
            "temperature": round(current_state["temperature"], 1),
            "humidity":    round(current_state["humidity"], 1),
            "wind_speed":  round(current_state["wind_speed"], 1),
            "weather":     current_state["weather"],
        })
    return readings


async def stream(websocket):
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            readings = next_reading()
            await websocket.send(json.dumps(readings))
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def main():
    print(f"WebSocket server starting on ws://localhost:{PORT}")
    async with websockets.serve(stream, "localhost", PORT):
        await asyncio.Future()   # run forever


if __name__ == "__main__":
    asyncio.run(main())
