const WebSocket = require('ws');
const { decryptPayload } = require('./encryption');

const WS_URL = 'ws://localhost:3000';

function startSimulation() {
    console.log('[*] Starting device simulation...');
    
    // 1. Setup Alert Listener
    const listenerWs = new WebSocket(WS_URL);
    
    listenerWs.on('open', () => {
        console.log('[LISTENER] Connected to server.');
        listenerWs.send(JSON.stringify({ type: 'register_listener' }));
    });

    listenerWs.on('message', (message) => {
        const payload = JSON.parse(message);
        if (payload.type === 'encrypted_alert') {
            console.log('\n[LISTENER] Received Encrypted Alert Payload:', payload.data);
            const decryptedAlert = decryptPayload(payload.data);
            console.log('[LISTENER] Decrypted Alert:', decryptedAlert, '\n');
        }
    });

    // 2. Setup simulated device stream
    const deviceWs = new WebSocket(WS_URL);
    let bpm = 70; // Start at normal resting heart rate

    deviceWs.on('open', () => {
        console.log('[DEVICE] Connected, streaming data...');
        
        setInterval(() => {
            // Emulate heart rate fluctuation
            bpm += (Math.random() > 0.5 ? 5 : -5);
            
            // Randomly force an anomaly (approx 5% chance per tick)
            if (Math.random() < 0.05) {
                bpm = 110; 
            } else if (Math.random() < 0.05) {
                bpm = 35;
            }

            // Ensure logic remains reasonable mostly
            if (bpm < 30) bpm = 35;
            if (bpm > 150) bpm = 140;

            const streamPayload = {
                deviceId: 'device-1234',
                timestamp: new Date().toISOString(),
                bpm: bpm
            };

            process.stdout.write(`[DEVICE] Emitting BPM: ${bpm}\r`);
            if (deviceWs.readyState === WebSocket.OPEN) {
                deviceWs.send(JSON.stringify(streamPayload));
            }
        }, 1000); // 1 tick per second
    });
}

// Ensure the server has time to start if you run them simultaneously 
setTimeout(startSimulation, 1500);
