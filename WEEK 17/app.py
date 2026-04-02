import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Secure Data Export", layout="wide")

# --- Security Functions ---
# For demonstration, we'll use a fixed key and IV. Typically these are managed securely.
KEY = b'12345678901234561234567890123456' # 32 bytes for AES-256
IV = b'1234567890123456' # 16 bytes for AES block size

def encrypt_data(data: str) -> bytes:
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()
    # PKCS7 Padding
    padding_length = 16 - (len(data.encode()) % 16)
    padded_data = data.encode() + bytes([padding_length]) * padding_length
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt_data(ciphertext: bytes) -> str:
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    # Remove PKCS7 Padding
    padding_length = padded_data[-1]
    data = padded_data[:-padding_length]
    return data.decode('utf-8')

# --- Data Generation ---
@st.cache_data
def generate_mock_encrypted_data() -> bytes:
    np.random.seed(42)
    timestamps = [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(50)]
    heart_rates = np.random.normal(70, 15, 50)
    # inject some anomalies
    heart_rates[5] = 120
    heart_rates[15] = 45
    heart_rates[30] = 150
    
    spo2 = np.random.normal(98, 2, 50)
    spo2[10] = 88
    spo2[40] = 90
    
    df = pd.DataFrame({
        'Timestamp': [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps],
        'HeartRate': heart_rates.astype(int),
        'SpO2': spo2.astype(int)
    })
    csv_string = df.to_csv(index=False)
    return encrypt_data(csv_string)
    
# --- PDF Generation ---
def generate_pdf(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Patient Biometric Data Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Note: Anomalous readings (HeartRate > 100 or < 60, SpO2 < 95) are highlighted in red.", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Table data
    data = [df.columns.tolist()] + df.values.tolist()
    
    table = Table(data)
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]
    
    # Highlight anomalies dynamically
    for row_idx, row in enumerate(df.itertuples()):
        hr = row.HeartRate
        spo2 = row.SpO2
        
        # Col 1 is Timestamp, Col 2 is HeartRate, Col 3 is SpO2 (0-indexed in table, so Timestamp = 0, HR = 1, SpO2 = 2)
        if hr > 100 or hr < 60:
            style_commands.append(('BACKGROUND', (1, row_idx + 1), (1, row_idx + 1), colors.lightcoral))
        if spo2 < 95:
            style_commands.append(('BACKGROUND', (2, row_idx + 1), (2, row_idx + 1), colors.lightcoral))
            
    table.setStyle(TableStyle(style_commands))
    elements.append(table)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# --- App Layout ---
def main():
    st.title("🛡️ Secure Biometric Data Export")
    st.markdown("This dashboard retrieves an **AES-256-CBC encrypted** data payload, decrypts it on the fly, detects biometrics anomalies, and allows exporting to CSV and highlighted PDF.")
    
    # Fetch encrypted mock data
    encrypted_payload = generate_mock_encrypted_data()
    
    st.subheader("1. System State")
    st.info(f"Retrieved encrypted payload of size: {len(encrypted_payload)} bytes.")
    
    # User Action: Decrypt
    st.subheader("2. Decrypt & Analyze")
    if st.button("Decrypt Data On-the-Fly", type="primary"):
        with st.spinner("Decrypting data using AES-256..."):
            try:
                decrypted_csv = decrypt_data(encrypted_payload)
                df = pd.read_csv(io.StringIO(decrypted_csv))
                
                # Sort by timestamp
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df = df.sort_values(by='Timestamp', ascending=False).reset_index(drop=True)
                
                st.success("Successfully decrypted data!")
                
                # Flag anomalies for the UI display
                def highlight_anomalies(row):
                    styles = []
                    for col, val in row.items():
                        if col == 'HeartRate' and (val > 100 or val < 60):
                            styles.append('background-color: lightcoral')
                        elif col == 'SpO2' and val < 95:
                            styles.append('background-color: lightcoral')
                        else:
                            styles.append('')
                    return styles
                
                st.dataframe(df.style.apply(highlight_anomalies, axis=1), use_container_width=True)
                
                # Export Options
                st.subheader("3. Export Reports")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📄 Download Raw Data (CSV)",
                        data=csv_data,
                        file_name="patient_data.csv",
                        mime="text/csv",
                    )
                    
                with col2:
                    pdf_data = generate_pdf(df)
                    st.download_button(
                        label="📑 Download Report with Anomalies (PDF)",
                        data=pdf_data,
                        file_name="patient_anomaly_report.pdf",
                        mime="application/pdf",
                    )
                    
            except Exception as e:
                st.error(f"Decryption failed: {e}")

if __name__ == "__main__":
    main()
