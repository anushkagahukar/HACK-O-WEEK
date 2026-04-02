# Wearable Data Ingestion System

A secure real-time backend that receives wearable device data via WebSockets, encrypts sensitive fields with AES-256, stores everything in a local SQLite database, and exposes REST APIs for retrieval and analysis.

---

## Tech Stack

- Node.js + Express.js
- WebSocket (`ws`)
- SQLite (`sqlite3`) — local file, no cloud
- AES-256-CBC encryption (`crypto` — built-in)
- `dotenv` for environment config

---

## Project Structure

```
wearable-data-ingestion-system/
├── server.js               # Entry point
├── testClient.js           # Simulated wearable device client
├── .env                    # Environment variables
├── config/
│   └── config.js           # Centralized config
├── database/
│   ├── db.js               # SQLite connection + table setup
│   └── wearable.db         # Auto-created on first run
├── websocket/
│   └── wsServer.js         # WebSocket server
├── routes/
│   └── wearableRoutes.js   # Express route definitions
├── controllers/
│   └── wearableController.js # Business logic + DB queries
├── utils/
│   ├── encryption.js       # AES encrypt/decrypt
│   ├── validator.js        # Payload validation
│   └── logger.js           # Timestamped console logger
└── middleware/
    ├── rateLimiter.js      # In-memory rate limiting
    └── errorHandler.js     # Global error handler
```

---

## Setup & Run

### 1. Install dependencies
```bash
npm install
```

### 2. Configure environment
Edit `.env` if needed (defaults work out of the box):
```
PORT=3000
WS_PORT=8080
ENCRYPTION_KEY=wearable_secure_key_32bytes_long!
```

### 3. Start the server
```bash
npm start
```
You'll see:
```
[INFO] SQLite database connected
[INFO] wearable_data table is ready
[INFO] HTTP server running at http://localhost:3000
[INFO] WebSocket server listening on ws://localhost:8080
```

### 4. Run the test client (in a separate terminal)
```bash
npm run client
```
The client simulates a wearable device, sending random data every 3 seconds with auto-reconnect.

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/wearable/history/:userId` | All records for a user |
| GET | `/api/wearable/latest/:userId` | Most recent record (cached) |
| GET | `/api/wearable/stats/:userId` | Avg heart rate, total steps, avg sleep |
| POST | `/api/wearable/test` | Insert mock data manually |

### Example: Insert test data
```bash
curl -X POST http://localhost:3000/api/wearable/test \
  -H "Content-Type: application/json" \
  -d '{"userId":"U123","deviceId":"D456","heartRate":82,"steps":5400,"calories":230,"sleepHours":6.5,"timestamp":"2026-04-02T10:30:00Z"}'
```

### Example: Get stats
```bash
curl http://localhost:3000/api/wearable/stats/U123
```

---

## WebSocket Payload Format

```json
{
  "userId": "U123",
  "deviceId": "D456",
  "heartRate": 82,
  "steps": 5400,
  "calories": 230,
  "sleepHours": 6.5,
  "timestamp": "2026-04-02T10:30:00Z"
}
```

### Validation Rules
| Field | Rule |
|-------|------|
| userId | Required, non-empty string |
| deviceId | Required, non-empty string |
| heartRate | Number, 40–200 |
| steps | Number, ≥ 0 |
| calories | Number, ≥ 0 |
| sleepHours | Number, 0–24 |
| timestamp | Valid ISO 8601 string |

---

## Security Features

- AES-256-CBC encryption on `heartRate`, `steps`, `calories`, `sleepHours` before DB storage
- Random IV per encryption — same value encrypts differently each time
- Rate limiting: 30 requests/minute per IP (configurable via `.env`)
- Input validation rejects malformed or out-of-range data

---

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Real-time ingestion | WebSocket server (`ws`) |
| Data encryption | AES-256-CBC via `crypto` |
| Local storage | SQLite (`wearable.db`) |
| REST APIs | Express.js routes |
| Caching | In-memory Map for latest data |
| Rate limiting | Per-IP request counter |
| Logging | Timestamped console logger |
