// Generate or retrieve session ID
function getSessionId() {
    let sessionId = localStorage.getItem('horcrux_session');
    if (!sessionId) {
        sessionId = Math.random().toString(36).substring(2) + Date.now().toString(36);
        localStorage.setItem('horcrux_session', sessionId);
    }
    return sessionId;
}

const sessionId = getSessionId();

// Update progress bar and text
function updateProgress(found, total) {
    const percentage = (found / total) * 100;
    document.getElementById('progressFill').style.width = percentage + '%';
    document.getElementById('progressText').textContent = 
        `${found} / ${total} HORCRUXES DESTROYED`;
}

// Show message
function showMessage(text, type = 'info') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = type;
}

// Show final flag
function showFinalFlag(flag) {
    document.getElementById('finalFlag').textContent = flag;
    document.getElementById('finalSection').style.display = 'block';
}

// Load progress on page load
async function loadProgress() {
    try {
        const response = await fetch('/api/progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId })
        });
        
        const data = await response.json();
        updateProgress(data.found, data.total);
        
        if (data.complete) {
            // Try to get final flag
            const finalResponse = await fetch('/api/final', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId })
            });
            
            const finalData = await finalResponse.json();
            if (finalData.success) {
                showFinalFlag(finalData.flag);
                showMessage('PASSAGE GRANTED. PLATFORM REVEALED.', 'success');
            }
        }
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

// Validate flag
async function validateFlag() {
    const flagInput = document.getElementById('flagInput');
    const flag = flagInput.value.trim();
    
    if (!flag) {
        showMessage('ENTER A FLAG', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ flag, sessionId })
        });
        
        const data = await response.json();
        
        if (!data.valid) {
            showMessage('INVALID HORCRUX', 'error');
            return;
        }
        
        if (data.duplicate) {
            showMessage('HORCRUX ALREADY DESTROYED', 'info');
            updateProgress(data.found, data.total);
            return;
        }
        
        updateProgress(data.found, data.total);
        
        const remaining = data.total - data.found;
        if (data.complete) {
            showMessage('FINAL HORCRUX DESTROYED. PLATFORM UNLOCKING...', 'success');
        } else {
            showMessage(`HORCRUX ${data.found} DESTROYED. ${remaining} REMAINING.`, 'success');
        }
        
        if (data.complete) {
            // Fetch final flag
            setTimeout(async () => {
                const finalResponse = await fetch('/api/final', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sessionId })
                });
                
                const finalData = await finalResponse.json();
                if (finalData.success) {
                    showFinalFlag(finalData.flag);
                    showMessage('PASSAGE GRANTED. PLATFORM REVEALED.', 'success');
                }
            }, 800);
        }
        
        flagInput.value = '';
        
    } catch (error) {
        showMessage('ERROR VALIDATING FLAG', 'error');
        console.error('Error:', error);
    }
}

// Event listeners
document.getElementById('validateBtn').addEventListener('click', validateFlag);
document.getElementById('flagInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        validateFlag();
    }
});

// Load progress on page load
loadProgress();
