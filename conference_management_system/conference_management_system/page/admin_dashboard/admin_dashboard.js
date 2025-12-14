frappe.pages['admin-dashboard'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Conference Admin Dashboard',
        single_column: true
    });

    function renderPage() {
        page.body.empty();

        const $root = $(`
            <div class="adm-dashboard">
                <div class="adm-stats-row">
                    <div class="adm-stat-card adm-click" data-route="List,Conference">
                        <div class="adm-stat-value" id="total-conferences">0</div>
                        <div class="adm-stat-label">Total Conferences</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,Session">
                        <div class="adm-stat-value" id="total-sessions">0</div>
                        <div class="adm-stat-label">Total Sessions</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,Registration">
                        <div class="adm-stat-value" id="total-registrations">0</div>
                        <div class="adm-stat-label">Total Registrations</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,Conference,{%22status%22:[%22in%22,[%22Upcoming%22,%22Ongoing%22]]}">
                        <div class="adm-stat-value" id="active-conferences">0</div>
                        <div class="adm-stat-label">Active Conferences</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,Mock Payment Details,{%22payment_status%22:%22Success%22}">
                        <div class="adm-stat-value" id="total-revenue">₹0</div>
                        <div class="adm-stat-label">Total Revenue</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,Mock Email Log">
                        <div class="adm-stat-value" id="email-logs">0</div>
                        <div class="adm-stat-label">Email Logs</div>
                    </div>
                    <div class="adm-stat-card adm-click" data-route="List,API Log">
                        <div class="adm-stat-value" id="api-calls">0</div>
                        <div class="adm-stat-label">API Calls</div>
                    </div>
                </div>

                <div class="adm-main">
                    <div class="adm-column">
                        <div class="adm-card">
                            <div class="adm-card-header">
                                <h3>Quick Actions</h3>
                            </div>
                            <div class="adm-card-body adm-actions-grid">
                                <button class="adm-btn adm-btn-primary" data-route="Form,Conference,new-conference-1">
                                    New Conference
                                </button>
                                <button class="adm-btn" data-route="List,Conference">All Conferences</button>
                                <button class="adm-btn" data-route="List,Session">All Sessions</button>
                                <button class="adm-btn" data-route="List,Registration">All Registrations</button>
                                <button class="adm-btn" data-route="List,Attendee">All Attendees</button>
                                <button class="adm-btn" data-route="List,Mock Payment Details">Payment Details</button>
                                <button class="adm-btn" data-route="List,Mock Email Log">Email Logs</button>
                                <button class="adm-btn" data-route="List,API Log">API Logs</button>
                            </div>
                        </div>

                        <div class="adm-card">
                            <div class="adm-card-header">
                                <h3>Reports &amp; Analytics</h3>
                            </div>
                            <div class="adm-card-body adm-actions-grid">
                                <button class="adm-btn adm-btn-accent" data-route="query-report,Conference Report">
                                    Conference Report
                                </button>
                                <button class="adm-btn adm-btn-accent" data-route="query-report,Session Analysis Report">
                                    Session Analysis
                                </button>
                                <button class="adm-btn adm-btn-accent" data-route="query-report,API Usage Report">
                                    API Usage Report
                                </button>
                                <button class="adm-btn" data-route="List,Registration,{%22payment_status%22:%22Paid%22}">
                                    Paid Registrations
                                </button>
                                <button class="adm-btn" data-route="List,Registration,{%22payment_status%22:%22Pending%22}">
                                    Pending Payments
                                </button>
                                <button class="adm-btn" data-route="List,Mock Email Log,{%22email_type%22:%22Session%20Recommendations%22}">
                                    Recommendation Emails
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="adm-column">
                        <div class="adm-card adm-card-full">
                            <div class="adm-card-header">
                                <h3>Revenue &amp; Performance Analytics</h3>
                            </div>
                            <div class="adm-card-body">
                                <div id="revenue-summary" class="adm-revenue-grid">Loading...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>
                :root {
                    --adm-bg: #ffffff;
                    --adm-bg-subtle: #f5f5f5;
                    --adm-border-soft: #e5e5e5;
                    --adm-border-strong: #111111;
                    --adm-text-main: #111111;
                    --adm-text-muted: #666666;
                    --adm-text-soft: #999999;
                    --adm-accent-dark: #111827;
                    --adm-shadow-soft: 0 1px 3px rgba(0, 0, 0, 0.04);
                    --adm-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.08);
                }

                * {
                    box-sizing: border-box;
                }

                .adm-dashboard {
                    padding: 20px 24px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: var(--adm-bg);
                    min-height: 100vh;
                    color: var(--adm-text-main);
                }

                .adm-stats-row {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 12px;
                    margin-bottom: 20px;
                }

                .adm-stat-card {
                    background: #ffffff;
                    border: 1px solid var(--adm-border-soft);
                    border-radius: 6px;
                    padding: 14px 12px;
                    height: 88px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center; /* centered */
                    position: relative;
                    overflow: hidden;
                    transition: border-color 0.12s ease, box-shadow 0.12s ease, transform 0.12s ease, background-color 0.12s ease;
                }

                .adm-stat-card::before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: #000000;
                }

                .adm-stat-card.adm-click {
                    cursor: pointer;
                }

                .adm-stat-card.adm-click:hover {
                    background: #fafafa;
                    border-color: var(--adm-border-strong);
                    box-shadow: var(--adm-shadow-hover);
                    transform: translateY(-1px);
                }

                .adm-stat-value {
                    font-size: 22px;
                    font-weight: 700;
                    color: var(--adm-text-main);
                    line-height: 1.1;
                    margin-bottom: 2px;
                    text-align: center; /* centered */
                }

                .adm-stat-label {
                    font-size: 11px;
                    color: var(--adm-text-muted);
                    text-transform: uppercase;
                    letter-spacing: 0.06em;
                    font-weight: 500;
                    text-align: center; /* centered */
                }

                .adm-main {
                    display: grid;
                    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.1fr);
                    gap: 20px;
                    align-items: stretch;
                }

                .adm-column {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .adm-card {
                    background: #ffffff;
                    border: 1px solid var(--adm-border-soft);
                    border-radius: 6px;
                    display: flex;
                    flex-direction: column;
                    box-shadow: var(--adm-shadow-soft);
                    min-height: 0;
                }

                .adm-card-full {
                    height: 100%;
                }

                .adm-card-header {
                    padding: 12px 16px;
                    border-bottom: 1px solid var(--adm-border-soft);
                    background: var(--adm-bg-subtle);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }

                .adm-card-header h3 {
                    margin: 0;
                    font-size: 13px;
                    font-weight: 600;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                    color: var(--adm-text-main);
                }

                .adm-card-body {
                    padding: 14px 16px 16px 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 0;
                }

                .adm-actions-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                }

                .adm-btn {
                    height: 34px;
                    border-radius: 4px;
                    border: 1px solid var(--adm-border-soft);
                    background: #ffffff;
                    color: var(--adm-text-main);
                    font-size: 12px;
                    font-weight: 500;
                    text-align: center;
                    cursor: pointer;
                    padding: 0 8px;
                    line-height: 1;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    transition: border-color 0.12s ease, background-color 0.12s ease, color 0.12s ease, box-shadow 0.12s ease;
                }

                .adm-btn:hover {
                    background: #fafafa;
                    border-color: var(--adm-border-strong);
                    box-shadow: var(--adm-shadow-soft);
                }

                .adm-btn-primary {
                    background: #000000;
                    border-color: #000000;
                    color: #ffffff;
                }

                .adm-btn-primary:hover {
                    background: #222222;
                    border-color: #222222;
                }

                .adm-btn-accent {
                    border-color: #111111;
                    color: var(--adm-accent-dark);
                }

                .adm-btn-accent:hover {
                    background: #f3f3f3;
                }

                .adm-revenue-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                    gap: 12px;
                }

                .adm-revenue-item {
                    text-align: center;
                    padding: 10px 8px;
                    border-radius: 4px;
                    border: 1px solid transparent;
                    min-height: 70px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }

                .adm-revenue-item.adm-click {
                    cursor: pointer;
                    transition: background-color 0.12s ease, border-color 0.12s ease, transform 0.12s ease;
                }

                .adm-revenue-item.adm-click:hover {
                    background: #fafafa;
                    border-color: var(--adm-border-soft);
                    transform: translateY(-1px);
                }

                .adm-revenue-number {
                    font-size: 18px;
                    font-weight: 600;
                    color: var(--adm-text-main);
                    margin-bottom: 2px;
                }

                .adm-revenue-label {
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 0.06em;
                    color: var(--adm-text-soft);
                    font-weight: 500;
                }

                .adm-empty {
                    text-align: center;
                    padding: 30px 16px;
                    font-size: 12px;
                    color: var(--adm-text-soft);
                }

                @media (max-width: 1200px) {
                    .adm-main {
                        grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
                    }
                }

                @media (max-width: 992px) {
                    .adm-dashboard {
                        padding: 16px;
                    }
                    .adm-main {
                        grid-template-columns: minmax(0, 1fr);
                    }
                }

                @media (max-width: 768px) {
                    .adm-stats-row {
                        grid-template-columns: minmax(0, 1fr);
                        gap: 10px;
                    }
                    .adm-stat-card {
                        height: 80px;
                        padding: 12px 10px;
                    }
                    .adm-stat-value {
                        font-size: 20px;
                    }
                    .adm-actions-grid {
                        grid-template-columns: minmax(0, 1fr);
                    }
                }

                @media (max-width: 480px) {
                    .adm-dashboard {
                        padding: 12px;
                    }
                    .adm-revenue-grid {
                        grid-template-columns: minmax(0, 1fr);
                    }
                }
            </style>
        `).appendTo(page.body);

        $(document).on('click', '.adm-btn, .adm-stat-card.adm-click, .adm-revenue-item.adm-click', function () {
            const route = $(this).data('route');
            if (!route) return;

            const parts = String(route).split(',');
            const [type, doctype, filters] = parts;

            if (type === 'Form') {
                frappe.set_route('Form', doctype, 'new');
            } else if (type === 'List') {
                if (filters) {
                    frappe.set_route('List', doctype, 'List', JSON.parse(decodeURIComponent(filters)));
                } else {
                    frappe.set_route('List', doctype);
                }
            } else if (type === 'query-report') {
                frappe.set_route('query-report', doctype);
            }
        });

        loadDashboardData();
    }

    function loadDashboardData() {
        loadStatistics();
        loadRevenueSummary();
    }

    function loadStatistics() {
        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.admin.get_dashboard_stats',
            callback: function (r) {
                if (r.message && r.message.success) {
                    const stats = r.message.data || {};
                    $('#total-conferences').text(stats.conferences || 0);
                    $('#total-sessions').text(stats.sessions || 0);
                    $('#total-registrations').text(stats.registrations || 0);
                    $('#active-conferences').text(stats.active_conferences || 0);
                    $('#total-revenue').text('₹' + (stats.total_revenue || 0).toLocaleString());
                    $('#email-logs').text(stats.email_logs || 0);
                    $('#api-calls').text(stats.api_logs || 0);
                }
            }
        });
    }

    function loadRevenueSummary() {
        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.admin.get_revenue_summary',
            callback: function (r) {
                const container = $('#revenue-summary');
                if (r.message && r.message.success) {
                    const data = r.message.data || {};
                    const paymentMethodsCount = data.payment_methods ? Object.keys(data.payment_methods).length : 0;

                    container.html(`
                        <div class="adm-revenue-item adm-click" data-route="List,Mock Payment Details,{%22payment_status%22:%22Success%22}">
                            <div class="adm-revenue-number">₹${(data.total_revenue || 0).toLocaleString()}</div>
                            <div class="adm-revenue-label">Total Revenue</div>
                        </div>
                        <div class="adm-revenue-item">
                            <div class="adm-revenue-number">₹${(data.processing_fees || 0).toLocaleString()}</div>
                            <div class="adm-revenue-label">Processing Fees</div>
                        </div>
                        <div class="adm-revenue-item">
                            <div class="adm-revenue-number">₹${(data.net_revenue || 0).toLocaleString()}</div>
                            <div class="adm-revenue-label">Net Revenue</div>
                        </div>
                        <div class="adm-revenue-item adm-click" data-route="List,Registration,{%22payment_status%22:%22Paid%22}">
                            <div class="adm-revenue-number">${data.paid_registrations || 0}</div>
                            <div class="adm-revenue-label">Paid Registrations</div>
                        </div>
                        <div class="adm-revenue-item">
                            <div class="adm-revenue-number">${data.conversion_rate || 0}%</div>
                            <div class="adm-revenue-label">Conversion Rate</div>
                        </div>
                        <div class="adm-revenue-item adm-click" data-route="List,Registration,{%22payment_status%22:%22Pending%22}">
                            <div class="adm-revenue-number">${paymentMethodsCount}</div>
                            <div class="adm-revenue-label">Payment Methods</div>
                        </div>
                    `);
                } else {
                    container.html('<div class="adm-empty">No revenue data available</div>');
                }
            }
        });
    }

    renderPage();
};
