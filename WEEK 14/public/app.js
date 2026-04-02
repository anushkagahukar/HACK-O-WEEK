// Secret key should ideally be managed securely. Using a predefined hardcoded key for the demo.
const SECRET_KEY = 'secure-wearable-encryption-key-123';
const API_URL = 'http://localhost:3000/api/data';

// DOM Elements
const btnSimulate = document.getElementById('btnSimulate');
const btnSend = document.getElementById('btnSend');
const rawContent = document.getElementById('rawContent');
const encContent = document.getElementById('encContent');
const btnRefresh = document.getElementById('btnRefresh');
const logsContent = document.getElementById('logsContent');
const hrChartCanvas = document.getElementById('hrChart');

let currentCiphertext = '';
let myChart = null;

// Initialize Chart.js
function initChart() {
  const ctx = hrChartCanvas.getContext('2d');
  myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Heart Rate (bpm)',
        data: [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderWidth: 2,
        pointRadius: 3,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' }, suggestedMin: 50, suggestedMax: 150 }
      },
      plugins: {
        legend: { labels: { color: '#f1f5f9' } }
      }
    }
  });
}

// Generate Random Data
function generateData() {
  const heartRate = Math.floor(Math.random() * (120 - 60 + 1)) + 60;
  const steps = Math.floor(Math.random() * (1000 - 100 + 1)) + 100;
  const timestamp = new Date().toISOString();
  
  return { heartRate, steps, timestamp };
}

// Event: Simulate & Encrypt
btnSimulate.addEventListener('click', () => {
    const data = generateData();
    const payloadStr = JSON.stringify(data, null, 2);
    
    // Update UI Raw
    rawContent.textContent = payloadStr;
    
    // Encrypt
    const ciphertext = CryptoJS.AES.encrypt(JSON.stringify(data), SECRET_KEY).toString();
    currentCiphertext = ciphertext;
    
    // Update UI Encrypted
    encContent.textContent = ciphertext;
    btnSend.disabled = false;
});

// Event: Send to Server
btnSend.addEventListener('click', async () => {
    if(!currentCiphertext) return;
    
    const originalText = btnSend.textContent;
    btnSend.textContent = 'Sending...';
    btnSend.disabled = true;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ciphertext: currentCiphertext })
        });

        if (response.ok) {
            btnSend.textContent = 'Sent Successfully!';
            setTimeout(() => {
                btnSend.textContent = originalText;
                // btnSend.disabled = false; keep it disabled until regenerated
            }, 2000);
            refreshData();
        } else {
            console.error('Failed to send data');
            btnSend.textContent = 'Error Sending';
        }
    } catch (err) {
        console.error(err);
    }
});

// Fetch and visualize data
async function refreshData() {
    try {
        const response = await fetch(API_URL);
        const records = await response.json();
        
        // Data prep for chart
        const labels = [];
        const hrData = [];
        let logsHTML = '';
        
        // We want chronological for chart; API sends DESC initially
        const ascRecords = [...records].reverse();

        ascRecords.forEach(record => {
            // Decrypt
            try {
               const bytes = CryptoJS.AES.decrypt(record.ciphertext, SECRET_KEY);
               const decryptedData = JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
               
               // Extract time for label
               const dateObj = new Date(decryptedData.timestamp || record.timestamp);
               const timeLabel = dateObj.toLocaleTimeString();

               labels.push(timeLabel);
               hrData.push(decryptedData.heartRate);

            } catch (e) {
               console.warn("Failed to decrypt a record, possibly wrong key");
            }
        });

        // Update Chart
        if (myChart) {
            myChart.data.labels = labels;
            myChart.data.datasets[0].data = hrData;
            myChart.update();
        }

        // Update Logs List (descending order)
        records.forEach(record => {
           logsHTML += `<div class="log-item">
              [ID: ${record.id}] Ciphertext stored: ${record.ciphertext.substring(0,20)}...
           </div>`;
        });
        logsContent.innerHTML = logsHTML || '<div class="log-item">No records found.</div>';

    } catch (err) {
        console.error('Error fetching data', err);
    }
}

btnRefresh.addEventListener('click', refreshData);

// Init
window.onload = () => {
    initChart();
    refreshData();
};
