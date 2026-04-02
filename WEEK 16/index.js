const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { encryptPayload } = require('./encryption');
const { detectAnomaly } = require('./anomalyDetector');

const app = express();
const server = http.createServer(app);

// WebSocket Server
const wss = new WebSocket.Server({ server });

// Keep track of connected dashboard/alert clients
const alertClients = new Set();

wss.on('connection', (ws, req) => {
    console.log('[+] New WebSocket connection established.');

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);

            // If a client identifies as an 'alert_listener', register them
            if (data.type === 'register_listener') {
                alertClients.add(ws);
                console.log('[*] Registered new alert listener.');
                return;
            }

            // Normal data ingestion (simulate Device stream)
            // console.log(`[STREAM] Device ${data.deviceId} sent BPM: ${data.bpm}`);
            
            // 1. Detect anomalies
            const anomaly = detectAnomaly(data);
            
            // 2. If anomaly found, push encrypted notification
            if (anomaly) {
                console.warn(`[!] Anomaly Detected: ${anomaly.reason}`);
                
                const encryptedAlert = encryptPayload(anomaly);
                const notificationPayload = JSON.stringify({
                    type: 'encrypted_alert',
                    data: encryptedAlert
                });

                // Push to all registered alert listeners
                for (const client of alertClients) {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(notificationPayload);
                    }
                }
            }

        } catch (error) {
            console.error('[-] Error processing message:', error.message);
        }
    });

    ws.on('close', () => {
        console.log('[-] WebSocket client disconnected.');
        alertClients.delete(ws);
    });
});

app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'Alert System is running.' });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`[*] Server listening on port ${PORT}`);
    console.log(`[*] WebSocket server attached and waiting for connections...`);
});
