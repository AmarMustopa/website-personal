// File ini untuk AJAX auto-refresh dashboard
function fetchDashboardData() {
    fetch('/api/status/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('monitor-temp').innerText = data.temperature + ' °C';
            document.getElementById('monitor-hum').innerText = data.humidity + ' %';
            document.getElementById('monitor-gas').innerText = data.gas;
            document.getElementById('monitor-status').innerText = data.status;
            // Ganti warna status
            let statusBox = document.getElementById('monitor-status');
            statusBox.className = 'status ' + data.status.toLowerCase().replace(' ', '-');
        });
    fetch('/api/history/')
        .then(response => response.json())
        .then(history => {
            let table = document.getElementById('history-table');
            if (table) {
                let rows = '';
                history.forEach(row => {
                    rows += `<tr><td>${row.created_at}</td><td>${row.temperature}</td><td>${row.humidity}</td><td>${row.gas}</td><td>${row.status}</td></tr>`;
                });
                table.innerHTML = rows;
            }
        });
}
setInterval(fetchDashboardData, 5000); // refresh tiap 5 detik
window.onload = fetchDashboardData;
