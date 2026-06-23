// static/js/logs.js
console.log('Loading LogsPage...');

const LogsPage = {
    render: async function(container) {
        console.log('LogsPage.render called');
        try {
            const response = await fetch('/api/logs/dashboard?days=30');
            const data = await response.json();
            console.log('Log data received:', data);
            
            const kpis = data.kpis || {};
            const charts = data.charts || {};

            container.innerHTML = `
                <div class="page-section active">
                    <h2><i class="bi bi-file-text"></i> Support Logs Dashboard</h2>
                    <p class="text-muted">Real-time log data from Redshift</p>
                    
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-value">${kpis.total_logs || 0}</div>
                            <div class="metric-label">Total Logs</div>
                        </div>
                        <div class="metric-item" style="border-left: 4px solid #e74c3c;">
                            <div class="metric-value">${kpis.error_logs || 0}</div>
                            <div class="metric-label">Error Logs</div>
                        </div>
                        <div class="metric-item" style="border-left: 4px solid #f39c12;">
                            <div class="metric-value">${kpis.warning_logs || 0}</div>
                            <div class="metric-label">Warning Logs</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${kpis.avg_cpu || 0}%</div>
                            <div class="metric-label">Avg CPU Usage</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${kpis.avg_response_time || 0}ms</div>
                            <div class="metric-label">Avg Response Time</div>
                        </div>
                    </div>

                    <div class="dashboard-card">
                        <h5>Logs by Ticket</h5>
                        <div class="table-container">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Ticket ID</th>
                                        <th>Total Logs</th>
                                        <th>Error Logs</th>
                                        <th>Warning Logs</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(charts.logs_by_ticket || []).slice(0, 10).map(log => `
                                        <tr>
                                            <td><strong>${log.ticket_id || 'N/A'}</strong></td>
                                            <td>${log.log_count || 0}</td>
                                            <td><span class="text-danger">${log.error_count || 0}</span></td>
                                            <td><span class="text-warning">${log.warning_count || 0}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('Error reading logs:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Error reading log data. Please try again later.
                    <br><small>${error.message}</small>
                </div>
            `;
        }
    }
};

console.log('LogsPage loaded successfully');