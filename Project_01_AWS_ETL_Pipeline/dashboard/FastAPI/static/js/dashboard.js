// static/js/dashboard.js
class Dashboard {
    constructor() {
        console.log('Dashboard constructor called');
        this.currentPage = 'tickets';
        this.charts = {};
        this.init();
    }

    init() {
        console.log('Dashboard init called');
        this.setupNavigation();
        this.loadPage('tickets');
        setInterval(() => this.refreshCurrentPage(), 60000);
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('.nav-link').dataset.page;
                if (page) {
                    this.loadPage(page);
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    e.target.closest('.nav-link').classList.add('active');
                }
            });
        });
    }

    loadPage(page) {
        console.log('Loading page:', page);
        this.currentPage = page;
        const content = document.getElementById('dashboardContent');
        
        if (!content) {
            console.error('Dashboard content element not found');
            return;
        }

        content.innerHTML = `
            <div class="text-center loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Loading ${page.replace('-', ' ')} data...</p>
            </div>
        `;

        this.destroyCharts();

        try {
            if (page === 'tickets') {
                if (typeof TicketsPage !== 'undefined' && TicketsPage.render) {
                    TicketsPage.render(content);
                } else {
                    throw new Error('TicketsPage not found');
                }
            } else if (page === 'logs') {
                if (typeof LogsPage !== 'undefined' && LogsPage.render) {
                    LogsPage.render(content);
                } else {
                    throw new Error('LogsPage not found');
                }
            }
        } catch (error) {
            console.error(`Error loading page ${page}:`, error);
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Error loading ${page} page: ${error.message}
                </div>
            `;
        }

        const updateTime = document.getElementById('updateTime');
        if (updateTime) {
            updateTime.textContent = new Date().toLocaleTimeString();
        }
    }

    refreshCurrentPage() {
        this.loadPage(this.currentPage);
    }

    destroyCharts() {
        try {
            if (typeof Chart !== 'undefined' && Chart.instances) {
                Object.keys(Chart.instances).forEach(key => {
                    try { Chart.instances[key].destroy(); } catch (e) {}
                });
            }
        } catch (e) {}
        this.charts = {};
    }
}

console.log('Dashboard class loaded');