// static/js/tickets.js - Support Tickets Page
console.log('Loading TicketsPage...');

const TicketsPage = {
    render: async function(container) {
        console.log('TicketsPage.render called');
        try {
            const response = await fetch('/api/tickets/dashboard');
            const data = await response.json();
            console.log('Ticket data received:', data);
            
            const kpis = data.kpis || {};
            const charts = data.charts || {};
            const tables = data.tables || {};

            container.innerHTML = `
                <div class="page-section active">
                    <h2><i class="bi bi-ticket"></i> Support Tickets Dashboard</h2>
                    <p class="text-muted">Real-time data from Redshift Serverless</p>
                    
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-value">${kpis.total_tickets || 0}</div>
                            <div class="metric-label">Total Tickets</div>
                        </div>
                        <div class="metric-item" style="border-left: 4px solid #f39c12;">
                            <div class="metric-value">${kpis.open_tickets || 0}</div>
                            <div class="metric-label">Open Tickets</div>
                        </div>
                        <div class="metric-item" style="border-left: 4px solid #27ae60;">
                            <div class="metric-value">${kpis.resolved_tickets || 0}</div>
                            <div class="metric-label">Resolved Tickets</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${kpis.active_agents || 0}</div>
                            <div class="metric-label">Active Agents</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${kpis.avg_interactions || 0}</div>
                            <div class="metric-label">Avg Interactions</div>
                        </div>
                    </div>

                    <div class="chart-grid">
                        <div class="dashboard-card">
                            <h5>Tickets by Agent</h5>
                            <div class="chart-container">
                                <canvas id="ticketsByAgentChart"></canvas>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <h5>Tickets by Channel</h5>
                            <div class="chart-container">
                                <canvas id="ticketsByChannelChart"></canvas>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <h5>Tickets by Priority</h5>
                            <div class="chart-container">
                                <canvas id="ticketsByPriorityChart"></canvas>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <h5>Tickets by Status</h5>
                            <div class="chart-container">
                                <canvas id="ticketsByStatusChart"></canvas>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <h5>Resolution Time by Category</h5>
                            <div class="chart-container">
                                <canvas id="resolutionByCategoryChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <div class="dashboard-card">
                        <h5>Agent Performance</h5>
                        <div class="table-container">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Agent Name</th>
                                        <th>Tickets Handled</th>
                                        <th>Resolved Count</th>
                                        <th>Avg Resolution (min)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(tables.agent_performance || []).map(agent => `
                                        <tr>
                                            <td><strong>${agent.agent || 'N/A'}</strong></td>
                                            <td>${agent.tickets_handled || 0}</td>
                                            <td>${agent.resolved_count || 0}</td>
                                            <td>${Math.round(agent.avg_resolution_minutes || 0)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="dashboard-card">
                        <h5>Recent Tickets</h5>
                        <div class="table-container">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Ticket ID</th>
                                        <th>Agent</th>
                                        <th>Channel</th>
                                        <th>Category</th>
                                        <th>Priority</th>
                                        <th>Status</th>
                                        <th>Interactions</th>
                                        <th>Resolution (min)</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(tables.detailed_tickets || []).map(ticket => `
                                        <tr>
                                            <td><strong>${ticket.ticket_id || 'N/A'}</strong></td>
                                            <td>${ticket.agent || 'N/A'}</td>
                                            <td>${ticket.channel || 'N/A'}</td>
                                            <td>${ticket.issue_category || 'N/A'}</td>
                                            <td><span class="priority-${ticket.priority || 'Low'}">${ticket.priority || 'N/A'}</span></td>
                                            <td><span class="status-badge status-${ticket.status || 'Open'}">${ticket.status || 'N/A'}</span></td>
                                            <td>${ticket.interactions || 0}</td>
                                            <td>${ticket.resolution_minutes || '-'}</td>
                                            <td>${ticket.created_at || 'N/A'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            setTimeout(() => {
                TicketsPage.renderCharts(charts);
            }, 100);

        } catch (error) {
            console.error('Error reading tickets from Redshift:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Error reading ticket data from Redshift. Please try again later.
                    <br><small>${error.message}</small>
                </div>
            `;
        }
    },

    renderCharts: function(charts) {
        console.log('Rendering ticket charts...', charts);
        try {
            const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c'];
            
            const byAgentData = charts.by_agent || [];
            const ctx1 = document.getElementById('ticketsByAgentChart');
            if (ctx1) {
                new Chart(ctx1.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: byAgentData.map(d => d.name || 'Unknown'),
                        datasets: [{
                            label: 'Tickets',
                            data: byAgentData.map(d => d.count || 0),
                            backgroundColor: colors.slice(0, byAgentData.length || 1),
                            borderColor: '#2c3e50',
                            borderWidth: 1
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
                console.log('Tickets by Agent chart rendered');
            }

            const byChannelData = charts.by_channel || [];
            const ctx2 = document.getElementById('ticketsByChannelChart');
            if (ctx2) {
                new Chart(ctx2.getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: byChannelData.map(d => d.channel || 'Unknown'),
                        datasets: [{
                            data: byChannelData.map(d => d.count || 0),
                            backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
                console.log('Tickets by Channel chart rendered');
            }

            const byPriorityData = charts.by_priority || [];
            const ctx3 = document.getElementById('ticketsByPriorityChart');
            if (ctx3) {
                const priorityColors = { 
                    'Critical': '#e74c3c', 
                    'High': '#f39c12', 
                    'Medium': '#3498db', 
                    'Low': '#2ecc71' 
                };
                new Chart(ctx3.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: byPriorityData.map(d => d.priority || 'Unknown'),
                        datasets: [{
                            label: 'Tickets',
                            data: byPriorityData.map(d => d.count || 0),
                            backgroundColor: byPriorityData.map(d => priorityColors[d.priority] || '#95a5a6')
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
                console.log('Tickets by Priority chart rendered');
            }

            const byStatusData = charts.by_status || [];
            const ctx4 = document.getElementById('ticketsByStatusChart');
            if (ctx4) {
                const statusColors = { 
                    'Open': '#f39c12', 
                    'Resolved': '#27ae60', 
                    'Escalated': '#e74c3c' 
                };
                new Chart(ctx4.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: byStatusData.map(d => d.status || 'Unknown'),
                        datasets: [{
                            data: byStatusData.map(d => d.count || 0),
                            backgroundColor: byStatusData.map(d => statusColors[d.status] || '#95a5a6')
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
                console.log('Tickets by Status chart rendered');
            }

            const resolutionData = charts.resolution_by_category || [];
            const ctx5 = document.getElementById('resolutionByCategoryChart');
            if (ctx5) {
                new Chart(ctx5.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: resolutionData.map(d => d.category || 'Unknown'),
                        datasets: [{
                            label: 'Avg Resolution Time (min)',
                            data: resolutionData.map(d => Math.round(d.avg_time || 0)),
                            backgroundColor: '#3498db'
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
                console.log('Resolution by Category chart rendered');
            }
        } catch (error) {
            console.error('Error in renderCharts:', error);
        }
    }
};

console.log('TicketsPage loaded successfully');