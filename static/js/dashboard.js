document.addEventListener('DOMContentLoaded', async () => {
    const navLinks = document.getElementById('nav-links');
    const welcomeMessage = document.getElementById('welcome-message');
    const userRoleInfo = document.getElementById('user-role-info');
    const dashboardContent = document.getElementById('dashboard-content');

    try {
        const response = await fetch('/api/session_data');
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        const user = await response.json();

        welcomeMessage.textContent = `Welcome, ${user.fullName || user.email}!`;
        navLinks.innerHTML = `<a href="/dashboard">Dashboard</a><button id="logout-btn">Logout</button>`;
        
        document.getElementById('logout-btn').addEventListener('click', async () => {
            await fetch('/api/logout', { method: 'POST' });
            // Use firebase.auth() instead of just auth
            await firebase.auth().signOut();
            window.location.href = '/login';
        });

        if (user.role === 'intern' || user.role === 'student') {
            userRoleInfo.textContent = `Role: ${user.role.charAt(0).toUpperCase() + user.role.slice(1)} at ${user.company || user.school || 'N/A'}`;
            renderInternDashboard(dashboardContent);
        } else if (user.role === 'supervisor') {
            userRoleInfo.textContent = `Role: Supervisor at ${user.company || 'N/A'}`;
            renderSupervisorDashboard(dashboardContent);
        } else if (user.role === 'lecturer') {
            userRoleInfo.textContent = `Role: Lecturer at ${user.school || 'N/A'}`;
            renderSupervisorDashboard(dashboardContent); // Use same dashboard as supervisor
        } else {
            userRoleInfo.textContent = `Role: ${user.role || 'User'}`;
            renderInternDashboard(dashboardContent); // Default to intern dashboard
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        window.location.href = '/login';
    }
});

// --- The rest of the dashboard.js file does not use 'auth' directly, ---
// --- so it doesn't need changes. Just copy the original functions     ---
// --- for renderInternDashboard and renderSupervisorDashboard below.  ---

function renderInternDashboard(container) {
    container.innerHTML = `
        <div class="card clock-in-card">
            <div id="clock-display">00:00:00</div>
            <div id="date-display"></div>
            <button id="clock-in-btn" class="cta-button-large">Clock In for Today</button>
            <p id="status-message"></p>
        </div>
        <h3>Your Recent Activity</h3>
        <div class="table-container" id="personal-history"><div class="loader"></div></div>
    `;

    const clockDisplay = document.getElementById('clock-display');
    const dateDisplay = document.getElementById('date-display');
    
    function updateClock() {
        const now = new Date();
        clockDisplay.textContent = now.toLocaleTimeString('en-US');
        dateDisplay.textContent = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }
    setInterval(updateClock, 1000);
    updateClock();

    document.getElementById('clock-in-btn').addEventListener('click', async (e) => {
        const btn = e.target;
        btn.disabled = true;
        btn.textContent = 'Processing...';

        const response = await fetch('/api/clock_in', { method: 'POST' });
        const result = await response.json();
        const statusMessage = document.getElementById('status-message');

        if (response.ok) {
            statusMessage.textContent = `Success! Clocked in at ${result.time}.`;
            statusMessage.style.color = 'var(--success-color)';
            btn.style.display = 'none';
        } else {
            statusMessage.textContent = `Error: ${result.message}`;
            statusMessage.style.color = 'var(--error-color)';
            btn.disabled = false;
            btn.textContent = 'Clock In for Today';
        }
    });

    fetch('/api/dashboard_data')
        .then(res => res.json())
        .then(data => {
            const historyContainer = document.getElementById('personal-history');
            if (data.records && data.records.length > 0) {
                let tableHtml = `<table class="data-table">
                                    <thead><tr><th>Date</th><th>Clock-In Time</th><th>Status</th></tr></thead>
                                    <tbody>`;
                data.records.forEach(rec => {
                    const clockIn = new Date(rec.clock_in_time);
                    tableHtml += `<tr>
                        <td>${rec.date}</td>
                        <td>${clockIn.toLocaleTimeString()}</td>
                        <td>${rec.is_late ? '<span class="late-tag">Late</span>' : '<span class="ontime-tag">On Time</span>'}</td>
                    </tr>`;
                });
                tableHtml += `</tbody></table>`;
                historyContainer.innerHTML = tableHtml;
            } else {
                historyContainer.innerHTML = `<p>No attendance records found.</p>`;
            }
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
            document.getElementById('personal-history').innerHTML = `<p>Error loading attendance data.</p>`;
        });
}

function renderSupervisorDashboard(container) {
    container.innerHTML = `
        <div class="supervisor-grid" id="summary-cards">
            <div class="loader"></div>
        </div>
        <div class="table-container">
            <h3>Today's Attendance</h3>
            <table class="data-table">
                <thead><tr><th>Name</th><th>Clock-In Time</th><th>Status</th></tr></thead>
                <tbody id="attendance-table-body">
                    <tr><td colspan="3"><div class="loader"></div></td></tr>
                </tbody>
            </table>
        </div>
    `;

    fetch('/api/dashboard_data')
        .then(res => res.json())
        .then(data => {
            const summaryContainer = document.getElementById('summary-cards');
            const tableBody = document.getElementById('attendance-table-body');
            
            const presentCount = data.present ? data.present.length : 0;
            const totalCount = data.all_interns_count || 0;
            const onTimeCount = data.present ? data.present.filter(p => !p.is_late).length : 0;

            summaryContainer.innerHTML = `
                <div class="summary-card card"><h3>Present Today</h3><div class="count">${presentCount} / ${totalCount}</div></div>
                <div class="summary-card card"><h3>On Time</h3><div class="count">${onTimeCount}</div></div>
                <div class="summary-card card"><h3>Late</h3><div class="count">${presentCount - onTimeCount}</div></div>
            `;
            
            if (data.present && presentCount > 0) {
                let tableHtml = '';
                data.present.sort((a, b) => new Date(a.clock_in_time) - new Date(b.clock_in_time));
                data.present.forEach(rec => {
                    const clockIn = new Date(rec.clock_in_time);
                    tableHtml += `<tr>
                        <td>${rec.fullName}</td>
                        <td>${clockIn.toLocaleTimeString()}</td>
                        <td>${rec.is_late ? '<span class="late-tag">Late</span>' : '<span class="ontime-tag">On Time</span>'}</td>
                    </tr>`;
                });
                tableBody.innerHTML = tableHtml;
            } else {
                tableBody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No interns have clocked in today.</td></tr>`;
            }
        })
        .catch(error => {
            console.error('Error loading supervisor dashboard data:', error);
            document.getElementById('summary-cards').innerHTML = `<p>Error loading dashboard data.</p>`;
            document.getElementById('attendance-table-body').innerHTML = `<tr><td colspan="3" style="text-align:center;">Error loading attendance data.</td></tr>`;
        });
}