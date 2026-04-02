import streamlit as st
import websocket
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

st.set_page_config(page_title="VitalAlert™", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")

# --- Styling aesthetics to abide by the system instructions ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d0e15;
        color: #ffffff;
    }
    .metric-value {
        font-size: 5rem !important;
        font-weight: 800;
        color: #00f0ff;
        text-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
        text-align: center;
    }
    .metric-label {
        font-size: 1.5rem;
        color: #8b8b99;
        text-align: center;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .anomaly-high, .anomaly-low {
        color: #ff2a5f !important;
        text-shadow: 0 0 30px rgba(255, 42, 95, 0.5) !important;
    }
    .alert-box {
        background: rgba(255, 42, 95, 0.1);
        border-left: 4px solid #ff2a5f;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "aes_key" not in st.session_state:
    st.session_state["aes_key"] = None
if "bpm" not in st.session_state:
    st.session_state["bpm"] = "--"

def decrypt_payload(b64data: str, key: bytes) -> dict:
    try:
        raw = base64.b64decode(b64data)
        iv = raw[:16]
        encrypted_text = raw[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_text) + decryptor.finalize()
        
        pad_len = decrypted_padded[-1]
        decrypted_text = decrypted_padded[:-pad_len].decode('utf-8')
        return json.loads(decrypted_text)
    except Exception as e:
        return {"error": str(e)}

st.title("❤️‍🔥 VitalAlert™ Dashboard")
st.markdown("### Real-Time Biometric Streams with Encrypted AES-256 Alerts")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Live Vitals Monitor")
    bpm_placeholder = st.empty()

with col2:
    st.markdown("### Critical Alerts Log")
    st.markdown("`Alerts are AES encrypted before leaving the backend.`")
    alerts_placeholder = st.empty()

def render_ui(bpm, deviceId):
    # Determine class for beautiful style
    bpm_class = "metric-value"
    is_anomaly = False
    if isinstance(bpm, int):
        if bpm > 100 or bpm < 40:
            bpm_class += " anomaly-high"
            is_anomaly = True

    with bpm_placeholder.container():
        st.markdown(f'<div class="{bpm_class}">{bpm}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">BPM</div>', unsafe_allow_html=True)
        st.caption(f"Connected Device: `{deviceId}`")

def render_alerts():
    with alerts_placeholder.container():
        if len(st.session_state["messages"]) == 0:
            st.info("All clear. Monitoring for biometric anomalies...")
        for alert in reversed(st.session_state["messages"][-5:]):
            st.markdown(f"""
            <div class="alert-box">
                <b>[{alert['timestamp']}] - {alert['reason']}</b><br>
                <small>Severity: {alert['severity']}</small><br>
                <code style="font-size:0.7em; color:yellow;">DECRYPTED PAYLOAD</code>
            </div>
            """, unsafe_allow_html=True)

# Run websocket sync logic
# Streamlit rerun architecture makes loop handling tricky, but we can wrap it in an infinite loop that updates placeholders.
@st.fragment
def realtime_stream():
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:3000")
        ws.send(json.dumps({"type": "register_listener"}))

        while True:
            resp = ws.recv()
            if not resp:
                break
            
            data = json.loads(resp)

            if data.get("type") == "key_exchange":
                st.session_state["aes_key"] = base64.b64decode(data["key"])

            elif data.get("type") == "raw_stream":
                render_ui(data["bpm"], data.get("deviceId", "Unknown"))
                
            elif data.get("type") == "encrypted_alert":
                if st.session_state["aes_key"]:
                    decrypted = decrypt_payload(data["data"], st.session_state["aes_key"])
                    st.session_state["messages"].append(decrypted)
                    render_alerts()
                    
    except Exception as e:
        st.error(f"Waiting for backend stream connection... {e}")

# Initial draw
render_ui("--", "Awaiting Device...")
render_alerts()

# Fire connection
if st.button("Reconnect Stream"):
    pass # page reload triggers connection
realtime_stream()
