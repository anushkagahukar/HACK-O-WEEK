let aesKey = null;

// UI Elements
const wsStatusDot = document.querySelector('#ws-status .dot');
const wsStatusText = document.querySelector('#ws-status');
const cryptoStatus = document.getElementById('crypto-status');
const bpmNumber = document.getElementById('live-bpm');
const deviceLbl = document.getElementById('lbl-device');
const heartIcon = document.querySelector('.heart');
const alertsContainer = document.getElementById('alerts-container');

// Establish WebSocket Connection
function connect() {
    const ws = new WebSocket('ws://localhost:3000');

    ws.onopen = () => {
        wsStatusDot.classList.remove('disconnected');
        wsStatusDot.classList.add('connected');
        wsStatusText.innerHTML = `<span class="dot connected"></span> Connected`;
        
        // Register this client as a listener
        ws.send(JSON.stringify({ type: 'register_listener' }));
    };

    ws.onclose = () => {
        wsStatusDot.classList.add('disconnected');
        wsStatusDot.classList.remove('connected');
        wsStatusText.innerHTML = `<span class="dot disconnected"></span> Disconnected`;
        cryptoStatus.classList.remove('secured');
        cryptoStatus.innerHTML = `<span class="icon lock-icon">🔒</span> Connection Lost`;
        setTimeout(connect, 3000); // Auto-reconnect
    };

    ws.onmessage = async (event) => {
        const payload = JSON.parse(event.data);

        // Simulated Stream Intercept (Normally Stream and Alerts are separate channels, but to show on dashboard we will render it if we receive it. Note: Python server might not broadcast raw stream. Let's create a hack for the demo to broadcast stream too or just listen to alerts.)
        // Wait, the Python server currently only pushes "key_exchange" and "encrypted_alert" to registered listeners.
        // I will alter device_simulator.py to push raw streams directly to clients, or have the server push it. 
        // For now, if payload.type == 'raw_stream':
        if (payload.type === 'raw_stream') {
            updateLiveMonitor(payload.bpm, payload.deviceId);
        }

        if (payload.type === 'key_exchange') {
            await importKey(payload.key);
            cryptoStatus.classList.add('secured');
            cryptoStatus.innerHTML = `<span class="icon lock-icon">🔐</span> TLS & AES Active`;
        }

        if (payload.type === 'encrypted_alert') {
            if (!aesKey) {
                console.error("Received encrypted alert but don't have the AES key!");
                return;
            }
            const decryptedAlert = await decryptData(payload.data);
            if (decryptedAlert) {
                renderAlert(decryptedAlert, payload.data);
                updateLiveMonitor(decryptedAlert.raw_value, decryptedAlert.deviceId, true);
            }
        }
    };
}

// Convert Base64 string to ArrayBuffer
function _base64ToArrayBuffer(base64) {
    const binary_string = window.atob(base64);
    const len = binary_string.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}

// Web Crypto API: Import the raw AES-256 Key
async function importKey(base64Key) {
    const keyData = _base64ToArrayBuffer(base64Key);
    try {
        aesKey = await window.crypto.subtle.importKey(
            "raw",
            keyData,
            { name: "AES-CBC", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
        console.log("Successfully imported AES key into Web Crypto API.");
    } catch (e) {
        console.error("Error importing key:", e);
    }
}

// Web Crypto API: Decrypt the Alert Payload
async function decryptData(encryptedBase64Payload) {
    try {
        const rawBytes = new Uint8Array(_base64ToArrayBuffer(encryptedBase64Payload));
        // First 16 bytes are the IV
        const iv = rawBytes.slice(0, 16);
        const cipherText = rawBytes.slice(16);

        const decryptedBuffer = await window.crypto.subtle.decrypt(
            { name: "AES-CBC", iv: iv },
            aesKey,
            cipherText
        );

        const decoder = new TextDecoder();
        let jsonStr = decoder.decode(decryptedBuffer);
        
        // Remove PKCS7 padding manually (WebCrypto does it for us sometimes, but we added it manually in Python)
        // Wait, WebCrypto auto-removes PKCS7 padding for AES-CBC! So jsonStr should be clean.
        
        // If there's garbage at the end due to manual padding, we sanitize
        jsonStr = jsonStr.replace(/[\x00-\x1F\x7F-\x9F]/g, ""); 

        return JSON.parse(jsonStr);
    } catch(e) {
        console.error("Decryption failed:", e);
        return null;
    }
}

// UI Updates
let simulateBpmInterval = null;

function updateLiveMonitor(bpm, deviceId, isAnomaly=false) {
    deviceLbl.textContent = deviceId;
    bpmNumber.textContent = bpm;
    
    // Heartbeat anim
    heartIcon.classList.remove('beat');
    void heartIcon.offsetWidth; // trigger reflow
    heartIcon.classList.add('beat');

    if (isAnomaly) {
        if (bpm > 100) {
            bpmNumber.className = 'bpm-number anomaly-high';
        } else {
            bpmNumber.className = 'bpm-number anomaly-low';
        }
    } else {
        bpmNumber.className = 'bpm-number';
    }
}

function renderAlert(alertObj, rawEncrypted) {
    const emptyState = document.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const timeString = new Date(alertObj.timestamp || new Date()).toLocaleTimeString();
    
    // Truncate ciphertext for display
    const shortCipher = rawEncrypted.substring(0, 32) + "...";

    const cardHtml = `
        <div class="alert-card">
            <div class="alert-header">
                <span>[${timeString}]</span>
                <span>Device: ${alertObj.deviceId}</span>
            </div>
            <div class="alert-title">${alertObj.reason}</div>
            <div class="alert-meta">
                <small>Secure Payload Decrypted (AES-256)</small>
                <code>${shortCipher}</code>
            </div>
        </div>
    `;

    alertsContainer.insertAdjacentHTML('afterbegin', cardHtml);
}

// Start
connect();
