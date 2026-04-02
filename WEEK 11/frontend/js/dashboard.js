document.addEventListener('DOMContentLoaded', () => {
    // Check auth
    if (!localStorage.getItem('token')) {
        window.location.href = 'index.html';
        return;
    }

    // Fade in effect
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        const icon = themeToggle.querySelector('i');
        if (document.body.classList.contains('light-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    });

    // Load Data
    loadUserProfile();
    loadWearableHistory();

    // Setup Sync Form
    document.getElementById('wearable-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('sync-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
        btn.disabled = true;

        const syncData = {
            heartRate: parseInt(document.getElementById('heartRate').value),
            steps: parseInt(document.getElementById('steps').value),
            sleep: parseFloat(document.getElementById('sleep').value),
            calories: parseInt(document.getElementById('calories').value),
            stressLevel: parseInt(document.getElementById('stressLevel').value),
        };

        try {
            await fetchAPI('/user/wearable', {
                method: 'POST',
                body: JSON.stringify(syncData)
            });
            
            showAlert('Data synced successfully!', 'success');
            document.getElementById('wearable-form').reset();
            loadWearableHistory(); // Refresh table
        } catch (error) {
            showAlert(error.message, 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
});

async function loadUserProfile() {
    try {
        const user = await fetchAPI('/user/profile');
        
        document.getElementById('profile-name').textContent = user.name;
        document.getElementById('profile-email').textContent = user.email;
        document.getElementById('profile-age').textContent = user.age || 'Not provided';
        document.getElementById('profile-gender').textContent = user.gender || 'Not provided';
        document.getElementById('profile-phone').textContent = user.phone || 'Unknown';
        
        // Update avatar initial
        if(user.name) {
            document.getElementById('avatar-initial').textContent = user.name.charAt(0).toUpperCase();
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
        if (error.message === 'Not authorized, token failed' || error.message === 'Not authorized, no token') {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        }
    }
}

async function loadWearableHistory() {
    try {
        const history = await fetchAPI('/user/wearable-history');
        const tbody = document.getElementById('history-tbody');
        
        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No history available. Sync your first data above.</td></tr>';
            return;
        }

        tbody.innerHTML = history.map(entry => {
            const date = new Date(entry.timestamp);
            return `
                <tr>
                    <td>${date.toLocaleDateString()} <span style="color:var(--text-muted);font-size:0.8em;">${date.toLocaleTimeString()}</span></td>
                    <td><strong>${entry.heartRate}</strong> <small>bpm</small></td>
                    <td><strong>${entry.steps.toLocaleString()}</strong></td>
                    <td><strong>${entry.sleep}</strong> <small>h</small></td>
                    <td><strong>${entry.calories}</strong> <small>kcal</small></td>
                    <td>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <div style="flex:1; height:4px; background:var(--glass-border); border-radius:2px; overflow:hidden;">
                                <div style="height:100%; width:${entry.stressLevel}%; background:${getStressColor(entry.stressLevel)}"></div>
                            </div>
                            <small>${entry.stressLevel}</small>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error fetching history:', error);
        const tbody = document.getElementById('history-tbody');
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--error-color);">Failed to load history</td></tr>';
    }
}

function getStressColor(level) {
    if (level < 30) return 'var(--success-color)';
    if (level < 70) return '#f59e0b';
    return 'var(--error-color)';
}
