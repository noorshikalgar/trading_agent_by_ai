// UI State Management
let currentStatus = 'stopped';

// DOM Elements
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnStop = document.getElementById('btn-stop');
const statusBadge = document.getElementById('agent-status');

// Control Buttons
btnStart.addEventListener('click', () => sendControl('start'));
btnPause.addEventListener('click', () => sendControl('pause'));
btnStop.addEventListener('click', () => sendControl('stop'));

// Send control command to backend
async function sendControl(action) {
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action})
        });
        const data = await response.json();
        
        if (data.success) {
            console.log(data.message);
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Control error:', error);
        alert('Failed to send command');
    }
}

// Update UI from backend state
async function updateUI() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update status
        currentStatus = data.status;
        statusBadge.textContent = currentStatus.toUpperCase();
        statusBadge.className = `status-badge ${currentStatus}`;
        
        // Update buttons
        btnStart.disabled = currentStatus === 'running';
        btnPause.disabled = currentStatus !== 'running';
        btnStop.disabled = currentStatus === 'stopped';
        
        // Update market hours
        document.getElementById('market-hours').textContent =
            `Market: ${data.market_hours}`;
        
        // Update portfolio
        const p = data.portfolio;
        document.getElementById('cash').textContent =
            `₹${p.cash.toLocaleString('en-IN', {maximumFractionDigits: 2})}`;
        document.getElementById('holdings-value').textContent =
            `₹${p.holdings_value.toLocaleString('en-IN', 
               {maximumFractionDigits: 2})}`;
        document.getElementById('total-value').textContent =
            `₹${p.total_value.toLocaleString('en-IN', 
               {maximumFractionDigits: 2})}`;
        
        const plElem = document.getElementById('unrealized-pl');
        plElem.textContent =
            `₹${p.unrealized_pl.toLocaleString('en-IN', 
               {maximumFractionDigits: 2})}`;
        plElem.className = `metric-value ${p.unrealized_pl >= 0 ? 
                            'positive' : 'negative'}`;
        
        // Update holdings table
        const holdingsBody = document.getElementById('holdings-body');
        if (data.holdings.length === 0) {
            holdingsBody.innerHTML =
                '<tr><td colspan="6" class="empty">No holdings</td></tr>';
        } else {
            holdingsBody.innerHTML = data.holdings.map(h => `
                <tr>
                    <td><strong>${h.symbol}</strong></td>
                    <td>${h.quantity}</td>
                    <td>₹${h.avg_price.toFixed(2)}</td>
                    <td>₹${h.current_price.toFixed(2)}</td>
                    <td>₹${h.value.toFixed(2)}</td>
                    <td class="${h.pl >= 0 ? 'positive' : 'negative'}">
                        ₹${h.pl.toFixed(2)}
                    </td>
                </tr>
            `).join('');
        }
        
        // Update trades table
        const tradesBody = document.getElementById('trades-body');
        if (data.recent_trades.length === 0) {
            tradesBody.innerHTML =
                '<tr><td colspan="7" class="empty">No trades yet</td></tr>';
        } else {
            tradesBody.innerHTML = data.recent_trades.map(t => {
                const time = new Date(t.timestamp).toLocaleTimeString();
                return `
                    <tr>
                        <td>${time}</td>
                        <td><strong>${t.symbol}</strong></td>
                        <td class="${t.action === 'BUY' ? 
                                    'positive' : 'negative'}">
                            ${t.action}
                        </td>
                        <td>${t.quantity}</td>
                        <td>₹${t.price.toFixed(2)}</td>
                        <td>₹${t.total.toFixed(2)}</td>
                        <td style="font-size:0.85em">${t.reason}</td>
                    </tr>
                `;
            }).join('');
        }
        
    } catch (error) {
        console.error('Update error:', error);
    }
}

// Update logs
async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        const logsContainer = document.getElementById('logs-container');
        
        logsContainer.innerHTML = data.logs.map(log =>
            `<div>${log}</div>`
        ).join('');
        
    } catch (error) {
        console.error('Logs error:', error);
    }
}

// Auto-refresh
setInterval(updateUI, 2000);    // Update UI every 2 seconds
setInterval(updateLogs, 3000);  // Update logs every 3 seconds

// Initial load
updateUI();
updateLogs();