frappe.pages['attendee-portal'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Conference Portal',
        single_column: true
    });

    let currentTab = 'conferences';
    let allConferences = [];
    let lastSearchKeyword = '';

    function renderPage() {
        page.body.empty();

        const $root = $(`
            <div class="ap-root">
                <div class="ap-tabs-row">
                    <button class="ap-tab ${currentTab === 'conferences' ? 'active' : ''}" data-tab="conferences">
                        Conferences
                    </button>
                    <button class="ap-tab ${currentTab === 'registrations' ? 'active' : ''}" data-tab="registrations">
                        Registrations
                    </button>
                    <button class="ap-tab ${currentTab === 'recommendations' ? 'active' : ''}" data-tab="recommendations">
                        Recommendations
                    </button>
                </div>

                <div class="ap-body">
                    <div id="conferences-tab" class="ap-panel ${currentTab === 'conferences' ? 'active' : ''}">
                        <div class="ap-toolbar">
                            <div class="ap-toolbar-left">
                                <input type="text" id="search-input" class="ap-input" placeholder="Type to search...">
                                <div class="ap-key-hint">Type to filter, clear to reset</div>
                            </div>
                        </div>
                        <div id="conferences-list" class="ap-list ap-list-borderless"></div>
                    </div>

                    <div id="registrations-tab" class="ap-panel ${currentTab === 'registrations' ? 'active' : ''}">
                        <div id="registrations-list" class="ap-list ap-list-borderless"></div>
                    </div>

                    <div id="recommendations-tab" class="ap-panel ${currentTab === 'recommendations' ? 'active' : ''}">
                        <div class="ap-toolbar ap-toolbar-right-only">
                            <div class="ap-caption">Personalized suggestions based on your activity</div>
                            <button class="ap-btn ap-btn-primary" id="get-recommendations">Get My Recommendations</button>
                            <button class="ap-btn" id="refresh-recommendations">Refresh</button>
                        </div>
                        <div id="recommendations-list" class="ap-list ap-list-borderless"></div>
                    </div>
                </div>
            </div>

            <style>
                :root {
                    --ap-bg: #ffffff;
                    --ap-border-soft: #e5e5e5;
                    --ap-border-strong: #111111;
                    --ap-text-main: #111111;
                    --ap-text-muted: #666666;
                    --ap-text-soft: #999999;
                }

                * { box-sizing: border-box; }

                .ap-root {
                    padding: 16px 24px 12px 24px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background: var(--ap-bg);
                    min-height: 100vh;
                    color: var(--ap-text-main);
                }

                .ap-tabs-row {
                    display: inline-flex;
                    border-bottom: 1px solid var(--ap-border-soft);
                    gap: 18px;
                    margin-bottom: 12px;
                }

                .ap-tab {
                    border: none;
                    background: transparent;
                    padding: 6px 0 10px 0;
                    font-size: 12px;
                    font-weight: 500;
                    color: var(--ap-text-soft);
                    cursor: pointer;
                    position: relative;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }

                .ap-tab::after {
                    content: "";
                    position: absolute;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    height: 2px;
                    background: transparent;
                }

                .ap-tab.active {
                    color: var(--ap-text-main);
                }

                .ap-tab.active::after {
                    background: #000000;
                }

                .ap-tab:not(.active):hover {
                    color: var(--ap-text-muted);
                }

                .ap-body { margin-top: 4px; }

                .ap-panel { display: none; }
                .ap-panel.active { display: block; }

                .ap-toolbar {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px;
                    padding: 6px 0 10px 0;
                    border-bottom: 1px solid var(--ap-border-soft);
                    margin-bottom: 4px;
                }

                .ap-toolbar-left {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    flex: 1;
                }

                .ap-toolbar-right-only {
                    justify-content: flex-end;
                }

                .ap-input {
                    flex: 1;
                    height: 30px;
                    padding: 4px 10px;
                    border-radius: 4px;
                    border: 1px solid var(--ap-border-soft);
                    font-size: 12px;
                    color: var(--ap-text-main);
                }

                .ap-input:focus {
                    outline: none;
                    border-color: var(--ap-border-strong);
                }

                .ap-key-hint {
                    font-size: 10px;
                    color: var(--ap-text-soft);
                    white-space: nowrap;
                }

                .ap-caption {
                    font-size: 11px;
                    color: var(--ap-text-soft);
                    margin-right: 8px;
                }

                .ap-btn {
                    height: 30px;
                    padding: 0 12px;
                    border-radius: 999px;
                    border: 1px solid var(--ap-border-soft);
                    background: #ffffff;
                    font-size: 11px;
                    font-weight: 500;
                    color: var(--ap-text-main);
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    transition: border-color 0.12s ease, background-color 0.12s ease, color 0.12s ease;
                }

                .ap-btn:hover {
                    background: #f6f6f6;
                    border-color: var(--ap-border-strong);
                }

                .ap-btn-primary {
                    background: #000000;
                    border-color: #000000;
                    color: #ffffff;
                }

                .ap-btn-primary:hover {
                    background: #222222;
                    border-color: #222222;
                }

                .ap-list {
                    max-height: 76vh;
                    overflow-y: auto;
                    padding: 4px 0 0 0;
                    margin-right: 2px;
                }

                .ap-list::-webkit-scrollbar { width: 4px; }
                .ap-list::-webkit-scrollbar-track { background: transparent; }
                .ap-list::-webkit-scrollbar-thumb {
                    background: rgba(0, 0, 0, 0.35);
                    border-radius: 4px;
                }

                .ap-list-borderless > div { border-bottom: 1px solid #f3f3f3; }
                .ap-list-borderless > div:last-child { border-bottom: none; }

                .ap-conf-row {
                    padding: 10px 0;
                    transition: background-color 0.12s ease;
                }

                .ap-conf-row:hover { background: #fafafa; }

                .ap-conf-top {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 4px;
                    gap: 8px;
                }

                .ap-conf-title {
                    font-size: 13px;
                    font-weight: 600;
                    color: var(--ap-text-main);
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                .ap-conf-meta {
                    font-size: 11px;
                    color: var(--ap-text-muted);
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                }

                .ap-conf-actions { margin-top: 6px; }

                .ap-session-toggle {
                    height: 24px;
                    padding: 0 10px;
                    border-radius: 999px;
                    border: 1px solid var(--ap-border-soft);
                    background: #ffffff;
                    font-size: 11px;
                    font-weight: 500;
                    color: var(--ap-text-main);
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                }

                .ap-session-toggle:hover {
                    border-color: var(--ap-border-strong);
                    background: #f6f6f6;
                }

                .ap-sessions-box {
                    display: none;
                    margin-top: 8px;
                    padding: 8px 10px;
                    border-left: 1px solid var(--ap-border-soft);
                }

                .ap-session-row { padding: 8px 0; }

                .ap-session-title {
                    font-size: 12px;
                    font-weight: 600;
                    color: var(--ap-text-main);
                    margin-bottom: 3px;
                }

                .ap-session-meta {
                    font-size: 11px;
                    color: var(--ap-text-muted);
                    margin-bottom: 6px;
                }

                .ap-register-btn {
                    height: 24px;
                    padding: 0 10px;
                    border-radius: 999px;
                    border: 1px solid var(--ap-border-soft);
                    background: #ffffff;
                    font-size: 11px;
                    font-weight: 500;
                    color: var(--ap-text-main);
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                }

                .ap-register-btn:hover:not(:disabled) {
                    border-color: var(--ap-border-strong);
                    background: #f6f6f6;
                }

                .ap-register-btn:disabled {
                    background: #f3f3f3;
                    color: var(--ap-text-soft);
                    border-color: #d4d4d4;
                    cursor: default;
                }

                .ap-reg-row {
                    padding: 10px 0;
                    transition: background-color 0.12s ease;
                }

                .ap-reg-row:hover { background: #fafafa; }

                .ap-reg-top {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 4px;
                }

                .ap-reg-id {
                    font-size: 12px;
                    font-weight: 600;
                    color: var(--ap-text-main);
                }

                .ap-status-pill {
                    padding: 2px 10px;
                    border-radius: 999px;
                    font-size: 10px;
                    font-weight: 500;
                    border: 1px solid var(--ap-border-soft);
                    color: var(--ap-text-main);
                }

                .ap-status-pending { border-style: dashed; }

                .ap-reg-meta {
                    font-size: 11px;
                    color: var(--ap-text-muted);
                    line-height: 1.4;
                    margin-bottom: 4px;
                }

                .ap-pay-btn {
                    height: 24px;
                    padding: 0 10px;
                    border-radius: 999px;
                    border: 1px solid var(--ap-border-strong);
                    background: #ffffff;
                    font-size: 11px;
                    font-weight: 500;
                    color: var(--ap-text-main);
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                }

                .ap-pay-btn:hover { background: #f6f6f6; }

                .ap-join-btn {
                    height: 24px;
                    padding: 0 10px;
                    border-radius: 999px;
                    border: 1px solid #28a745;
                    background: #28a745;
                    font-size: 11px;
                    font-weight: 500;
                    color: #ffffff;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.12s ease;
                }

                .ap-join-btn:hover {
                    background: #218838;
                    color: #ffffff;
                    text-decoration: none;
                }

                .ap-interest-bar {
                    display: inline-flex;
                    border-radius: 999px;
                    border: 1px solid var(--ap-border-soft);
                    overflow: hidden;
                }

                .ap-interest-btn {
                    border: none;
                    background: transparent;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 0 10px;
                    height: 24px;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: var(--ap-text-muted);
                    border-right: 1px solid var(--ap-border-soft);
                }

                .ap-interest-btn:last-child { border-right: none; }

                .ap-interest-btn.active {
                    background: #000000;
                    color: #ffffff;
                }

                .ap-interest-btn.negative.active {
                    background: #222222;
                    color: #ffffff;
                }

                .ap-empty {
                    text-align: center;
                    padding: 24px 8px;
                    font-size: 12px;
                    color: var(--ap-text-soft);
                }

                @media (max-width: 768px) {
                    .ap-root { padding: 12px; }
                    .ap-toolbar {
                        flex-direction: column;
                        align-items: stretch;
                    }
                    .ap-toolbar-left {
                        flex-direction: column;
                        align-items: stretch;
                    }
                }

                @media (max-width: 480px) {
                    .ap-root { padding: 8px; }
                    .ap-tabs-row { gap: 10px; }
                    .ap-tab { font-size: 11px; }
                }
            </style>
        `).appendTo(page.body);

        $root.find('.ap-tab').on('click', function () {
            const tab = $(this).data('tab');
            currentTab = tab;
            renderPage();
            if (tab === 'conferences') loadConferences();
            else if (tab === 'registrations') loadRegistrations();
            else if (tab === 'recommendations') loadRecommendations(true);
        });

        $('#search-input').on('input', handleSearchInput);

        $('#get-recommendations').on('click', () => loadRecommendations(true));
        $('#refresh-recommendations').on('click', () => loadRecommendations(true));

        if (currentTab === 'conferences') loadConferences();
        else if (currentTab === 'registrations') loadRegistrations();
        else if (currentTab === 'recommendations') loadRecommendations(true);
    }

    function handleSearchInput() {
        const keyword = $('#search-input').val().trim();
        lastSearchKeyword = keyword;

        if (!keyword) {
            if (allConferences && allConferences.length) {
                renderConferences(allConferences);
            } else {
                loadConferences();
            }
            return;
        }

        if (!allConferences || !allConferences.length) {
            loadConferencesAndThenFilter(keyword);
            return;
        }

        const lower = keyword.toLowerCase();
        const filtered = allConferences.filter(conf =>
            (conf.conference_name || '').toLowerCase().includes(lower) ||
            (conf.location || '').toLowerCase().includes(lower)
        );

        if (filtered.length) {
            renderConferences(filtered);
        } else {
            $('#conferences-list').html('<div class="ap-empty">No conferences match this keyword.</div>');
        }
    }

    function loadConferencesAndThenFilter(keyword) {
        const container = $('#conferences-list');
        container.html('<div class="ap-empty">Loading conferences...</div>');

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.conferences.get_upcoming_conferences',
            callback: function (r) {
                if (r.message && r.message.success) {
                    allConferences = r.message.data || [];
                    lastSearchKeyword = keyword;
                    $('#search-input').val(keyword);
                    handleSearchInput();
                } else {
                    container.html('<div class="ap-empty">No conferences found.</div>');
                }
            },
            error: function () {
                container.html('<div class="ap-empty">Failed to load conferences.</div>');
            }
        });
    }

    function loadConferences() {
        const container = $('#conferences-list');
        container.html('<div class="ap-empty">Loading conferences...</div>');

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.conferences.get_upcoming_conferences',
            callback: function (r) {
                if (r.message && r.message.success) {
                    allConferences = r.message.data || [];
                    if (!lastSearchKeyword) {
                        $('#search-input').val('');
                        renderConferences(allConferences);
                    } else {
                        handleSearchInput();
                    }
                } else {
                    container.html('<div class="ap-empty">No conferences found.</div>');
                }
            },
            error: function () {
                container.html('<div class="ap-empty">Failed to load conferences.</div>');
            }
        });
    }

    function renderConferences(conferences) {
        const container = $('#conferences-list');
        if (!conferences || !conferences.length) {
            container.html('<div class="ap-empty">No conferences found.</div>');
            return;
        }

        let html = '';
        conferences.forEach(conf => {
            html += `
                <div class="ap-conf-row">
                    <div class="ap-conf-top">
                        <div class="ap-conf-title">${frappe.utils.escape_html(conf.conference_name)}</div>
                    </div>
                    <div class="ap-conf-meta">
                        <span>${conf.start_date} - ${conf.end_date}</span>
                        <span>${conf.location || 'Virtual'}</span>
                        <span>₹${conf.registration_fee || 0}</span>
                    </div>
                    <div class="ap-conf-actions">
                        <button class="ap-session-toggle" data-conference="${conf.name}">View Sessions</button>
                    </div>
                    <div class="ap-sessions-box" id="sessions-${conf.name.replace(/[^a-zA-Z0-9]/g, '_')}"></div>
                </div>
            `;
        });

        container.html(html);

        container.find('.ap-session-toggle').on('click', function () {
            const confName = $(this).data('conference');
            const boxId = confName.replace(/[^a-zA-Z0-9]/g, '_');
            const box = $(`#sessions-${boxId}`);
            const button = $(this);
            

            
            if (box.is(':visible')) {

                box.hide();
                button.text('View Sessions');
            } else {

                button.text('Loading...');
                loadSessions(confName, box, button);
            }
        });
    }

    function loadSessions(conferenceName, container, button) {
        container.html('<div class="ap-empty" style="padding: 8px;">Loading sessions...</div>').show();

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.sessions.get_sessions_by_conference',
            args: { conference_id: conferenceName },
            callback: function (r) {

                
                if (r.message && r.message.success) {
                    const sessions = r.message.data || [];

                    if (sessions.length > 0) {
                        renderSessions(sessions, container, conferenceName);
                    } else {
                        container.html('<div class="ap-empty" style="padding: 8px;">No sessions found for this conference.</div>');
                    }
                } else {
                    const errorMsg = r.message?.error || r.message?.message || 'Failed to load sessions';
                    container.html(`<div class="ap-empty" style="padding: 8px;">${errorMsg}</div>`);
                }
                button.text('Hide Sessions');
            },
            error: function(xhr, status, error) {
                console.error('Sessions API Error:', xhr, status, error);
                container.html('<div class="ap-empty" style="padding: 8px;">Failed to load sessions.</div>');
                button.text('Hide Sessions');
            }
        });
    }

    function renderSessions(sessions, container, conferenceName) {
        let html = '';
        sessions.forEach(session => {
            
            const availableSpots = session.available_spots || 0;
            const isAvailable = availableSpots > 0;
            const userRegistered = session.user_registered || false;

            let buttonText = 'Register';
            let disabledAttr = '';
            if (userRegistered) {
                buttonText = 'Registered';
                disabledAttr = 'disabled';
            } else if (!isAvailable) {
                buttonText = 'Full';
                disabledAttr = 'disabled';
            }

            const sessionHtml = `
                <div class="ap-session-row">
                    <div class="ap-session-title">${frappe.utils.escape_html(session.session_name)}</div>
                    <div class="ap-session-meta">
                        ${session.speaker || 'TBA'} • ${session.start_time}-${session.end_time} •
                        ${availableSpots}/${session.max_attendees || 'Unlimited'}
                    </div>
                    <button class="ap-register-btn"
                        data-session="${session.name}"
                        data-conference="${conferenceName}"
                        ${disabledAttr}>
                        ${buttonText}
                    </button>
                </div>
            `;
            
            html += sessionHtml;
        });

        container.html(html);

        container.find('.ap-register-btn').on('click', function () {
            if ($(this).prop('disabled')) return;
            const sessionName = $(this).data('session');
            const confName = $(this).data('conference');
            registerForSession(sessionName, confName);
        });

    }

    function registerForSession(sessionName, conferenceName) {
        const email = frappe.session.user;
        const name = frappe.session.user_fullname || email;

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.registrations.register_for_session',
            args: { session_id: sessionName, attendee_name: name, email: email },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.msgprint({
                        title: 'Registration Successful!',
                        message: `Registration ID: ${r.message.data.registration_id}<br><br><strong>Next Step:</strong> Go to the <strong>Registrations</strong> tab to complete your payment.`,
                        indicator: 'green'
                    });
                    // Auto-switch to registrations tab after 3 seconds
                    setTimeout(() => {
                        currentTab = 'registrations';
                        renderPage();
                        loadRegistrations();
                    }, 3000);
                } else {
                    frappe.msgprint({
                        title: 'Error',
                        message: r.message?.error || 'Registration failed',
                        indicator: 'red'
                    });
                }
            }
        });
    }

    function loadRegistrations() {
        const container = $('#registrations-list');
        container.html('<div class="ap-empty">Loading registrations...</div>');

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.registrations.get_attendee_registrations',
            callback: function (r) {
                if (r.message && r.message.success && r.message.data && r.message.data.length > 0) {
                    renderRegistrations(r.message.data, container);
                } else {
                    const message = r.message?.message || 'No registrations found.';
                    container.html(`<div class="ap-empty">${message}</div>`);
                }
            },
            error: function () {
                container.html('<div class="ap-empty">No registrations found. Please register for sessions first.</div>');
            }
        });
    }

    function renderRegistrations(registrations, container) {
        let html = '';
        registrations.forEach(reg => {
            html += `
                <div class="ap-reg-row">
                    <div class="ap-reg-top">
                        <div class="ap-reg-id">REG ${reg.name}</div>
                        <span class="ap-status-pill ap-status-${reg.payment_status.toLowerCase()}">
                            ${reg.payment_status}
                        </span>
                    </div>
                    <div class="ap-reg-meta">
                        ${reg.registration_date} • ₹${reg.amount || 0}<br>
                        ${reg.conference_name} • ${reg.session_name}<br>
                        ${reg.speaker || 'TBA'} • ${reg.start_time}-${reg.end_time}
                    </div>
                    ${reg.payment_status === 'Pending'
                        ? `<button class="ap-pay-btn" data-registration="${reg.name}">Pay Now</button>`
                        : reg.payment_status === 'Paid' && reg.join_link
                        ? `<a href="${reg.join_link}" target="_blank" class="ap-join-btn">Join Session</a>`
                        : ''}
                </div>
            `;
        });

        container.html(html || '<div class="ap-empty">No registrations found.</div>');

        container.find('.ap-pay-btn').on('click', function () {
            processPayment($(this).data('registration'));
        });
    }

    function processPayment(registrationId) {
        const paymentMethods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking'];

        const dialog = new frappe.ui.Dialog({
            title: 'Select Payment Method',
            fields: [
                {
                    fieldtype: 'Select',
                    fieldname: 'payment_method',
                    label: 'Payment Method',
                    options: paymentMethods.join('\n'),
                    reqd: 1,
                    default: 'Credit Card'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'card_number',
                    label: 'Card Number (Mock)',
                    placeholder: '1234 5678 9012 3456',
                    depends_on: 'eval:doc.payment_method && doc.payment_method.indexOf("Card") !== -1'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'upi_id',
                    label: 'UPI ID (Mock)',
                    placeholder: 'user@paytm',
                    depends_on: 'eval:doc.payment_method == "UPI"'
                }
            ],
            primary_action_label: 'Pay Now',
            primary_action: function (values) {
                dialog.hide();
                frappe.call({
                    method: 'conference_management_system.conference_management_system.api.v1.registrations.process_payment',
                    args: {
                        registration_id: registrationId,
                        payment_method: values.payment_method,
                        card_number: values.card_number,
                        upi_id: values.upi_id
                    },
                    callback: function (r) {
                        if (r.message?.success) {
                            frappe.msgprint({
                                title: 'Payment Successful',
                                message: `Transaction ID: ${r.message.transaction_id}<br>Amount: ₹${r.message.amount}<br>Processing Fee: ₹${r.message.processing_fee}`,
                                indicator: 'green'
                            });
                            loadRegistrations();
                        } else {
                            frappe.msgprint({
                                title: 'Payment Failed',
                                message: r.message?.error || 'Payment processing failed',
                                indicator: 'red'
                            });
                        }
                    }
                });
            }
        });

        dialog.show();
    }

    function loadRecommendations(forceRefresh = false) {
        const container = $('#recommendations-list');
        container.html('<div class="ap-empty">Loading recommendations...</div>');

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.attendees.get_attendee_profile',
            args: {
                email: frappe.session.user,
                _: forceRefresh ? Date.now() : undefined
            },
            no_cache: forceRefresh,
            callback: function (r) {
                if (r.message?.success && r.message.data?.attendee) {
                    const attendeeId = r.message.data.attendee.name;

                    frappe.call({
                        method: 'conference_management_system.conference_management_system.api.v1.registrations.get_recommendations',
                        args: {
                            attendee_id: attendeeId,
                            _: forceRefresh ? Date.now() : undefined
                        },
                        no_cache: forceRefresh,
                        callback: function (rec_r) {
                            if (rec_r.message?.success && rec_r.message.data?.length) {
                                renderRecommendations(rec_r.message.data, container);
                            } else {
                                container.html('<div class="ap-empty">No recommendations available. Register for sessions to get personalized suggestions.</div>');
                            }
                        },
                        error: function () {
                            container.html('<div class="ap-empty">Failed to load recommendations.</div>');
                        }
                    });
                } else {
                    container.html('<div class="ap-empty">Please register for sessions first to get recommendations.</div>');
                }
            }
        });
    }

    function renderRecommendations(recommendations, container) {
        Promise.all([
            new Promise((resolve) => {
                frappe.call({
                    method: 'conference_management_system.conference_management_system.api.v1.registrations.get_attendee_registrations',
                    no_cache: true,
                    callback: function (r) {
                        const userRegistrations = new Set();
                        if (r.message?.success && r.message.data) {
                            r.message.data.forEach(reg => userRegistrations.add(reg.session));
                        }
                        resolve(userRegistrations);
                    },
                    error: () => resolve(new Set())
                });
            }),
            new Promise((resolve) => {
                frappe.call({
                    method: 'conference_management_system.conference_management_system.api.v1.attendees.get_attendee_profile',
                    args: { email: frappe.session.user },
                    no_cache: true,
                    callback: function (r) {
                        const preferences = new Map();
                        if (r.message?.success && r.message.data?.preferences) {
                            r.message.data.preferences.forEach(pref => {
                                preferences.set(pref.session_id, pref.preference_type);
                            });
                        }
                        resolve(preferences);
                    },
                    error: () => resolve(new Map())
                });
            })
        ]).then(([userRegistrations, userPreferences]) => {
            let html = '';
            recommendations.forEach(rec => {
                const availableSpots = rec.available_spots || 0;
                const isAvailable = availableSpots > 0;
                const userRegistered = userRegistrations.has(rec.name);
                const currentPreference = userPreferences.get(rec.name);

                let buttonText = 'Register';
                let disabledAttr = '';
                if (userRegistered) {
                    buttonText = 'Registered';
                    disabledAttr = 'disabled';
                } else if (!isAvailable) {
                    buttonText = 'Full';
                    disabledAttr = 'disabled';
                }

                let likeState = '';
                let neutralState = '';
                let dislikeState = '';
                if (currentPreference === 'Interested') {
                    likeState = 'active';
                } else if (currentPreference === 'Not Interested') {
                    dislikeState = 'active';
                } else {
                    neutralState = 'active';
                }

                html += `
                    <div class="ap-session-row">
                        <div class="ap-session-title">${frappe.utils.escape_html(rec.session_name)}</div>
                        <div class="ap-session-meta">
                            ${rec.speaker || 'TBA'} • ${rec.conference_name || 'Conference'}<br>
                            ${rec.start_time || ''} - ${rec.end_time || ''} •
                            ${availableSpots}/${rec.max_attendees || 'Unlimited'} spots
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <button class="ap-register-btn"
                                data-session="${rec.name}"
                                ${disabledAttr}>
                                ${buttonText}
                            </button>
                            <div class="ap-interest-bar" data-session="${rec.name}">
                                <button class="ap-interest-btn ${neutralState}" data-action="neutral">Neutral</button>
                                <button class="ap-interest-btn ${likeState}" data-action="interested">Like</button>
                                <button class="ap-interest-btn negative ${dislikeState}" data-action="not_interested">Skip</button>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.html(html || '<div class="ap-empty">No recommendations found.</div>');

            container.find('.ap-register-btn').on('click', function () {
                if ($(this).prop('disabled')) return;
                const sessionName = $(this).data('session');
                registerForSession(sessionName, null);
            });

            container.find('.ap-interest-btn').on('click', function () {
                const btn = $(this);
                const action = btn.data('action');
                const bar = btn.closest('.ap-interest-bar');
                const sessionId = bar.data('session');

                bar.find('.ap-interest-btn').removeClass('active');
                btn.addClass('active');

                if (action === 'neutral') {
                    updatePreference(sessionId, null, btn, true);
                } else {
                    const preferenceType = action === 'interested' ? 'Interested' : 'Not Interested';
                    updatePreference(sessionId, preferenceType, btn, false);
                }
            });
        });
    }

    function updatePreference(sessionId, preferenceType, button, neutral) {
        const originalText = button.text();
        button.text('...');

        if (neutral) {
            frappe.call({
                method: 'conference_management_system.conference_management_system.api.v1.attendees.update_preferences',
                args: {
                    email: frappe.session.user,
                    session_id: sessionId,
                    preference_type: ''
                },
                callback: function () {
                    button.text(originalText);
                },
                error: function () {
                    button.text(originalText);
                }
            });
            return;
        }

        frappe.call({
            method: 'conference_management_system.conference_management_system.api.v1.attendees.update_preferences',
            args: {
                email: frappe.session.user,
                session_id: sessionId,
                preference_type: preferenceType
            },
            callback: function (r) {
                button.text(originalText);
                if (r.message?.success) {
                    frappe.show_alert(
                        { message: `Marked as ${preferenceType}`, indicator: 'green' },
                        2
                    );
                } else {
                    frappe.msgprint({
                        title: 'Error',
                        message: r.message?.error || 'Failed to update preference',
                        indicator: 'red'
                    });
                }
            },
            error: function () {
                button.text(originalText);
                frappe.msgprint({
                    title: 'Error',
                    message: 'Failed to update preference',
                    indicator: 'red'
                });
            }
        });
    }

    renderPage();
};
