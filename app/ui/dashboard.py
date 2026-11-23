def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Source Issue Scout + Fix Coach</title>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #4ade80;
            --warning: #facc15;
            --danger: #f87171;
            --border: #475569;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg-primary); color: var(--text-main); line-height: 1.5; padding: 24px; }
        .container { max-width: 1100px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
        h1 { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
        .subtitle { font-size: 0.875rem; color: var(--text-muted); }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 24px; border-bottom: 1px solid var(--border); }
        .tab-btn { background: none; border: none; color: var(--text-muted); font-size: 0.95rem; font-weight: 600; padding: 8px 16px; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        .card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 16px; }
        .card h2 { font-size: 1.2rem; margin-bottom: 12px; color: var(--accent); }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 4px; }
        input, select, textarea { width: 100%; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; color: var(--text-main); font-size: 0.9rem; }
        .btn { background: var(--accent); color: #000; border: none; font-weight: 600; padding: 9px 18px; border-radius: 6px; cursor: pointer; transition: background 0.2s; }
        .btn:hover { background: var(--accent-hover); }
        .btn-secondary { background: var(--border); color: var(--text-main); }
        .btn-success { background: var(--success); color: #000; }
        .btn-danger { background: var(--danger); color: #000; }
        .issue-card { background: var(--bg-card); border-radius: 6px; padding: 16px; margin-bottom: 12px; border-left: 4px solid var(--accent); }
        .issue-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; }
        .issue-title a { color: var(--text-main); text-decoration: none; }
        .issue-title a:hover { color: var(--accent); }
        .badge { display: inline-block; padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; margin-right: 6px; font-weight: 600; background: var(--border); }
        .badge-score { background: #0369a1; color: #fff; }
        .badge-easy { background: #166534; color: #fff; }
        .badge-time { background: #854d0e; color: #fff; }
        .meta-text { font-size: 0.85rem; color: var(--text-muted); margin-top: 8px; }
        .action-row { display: flex; gap: 8px; margin-top: 12px; }
        pre { background: #090d16; padding: 12px; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 0.85rem; color: #38bdf8; margin-top: 8px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }
        .stat-card { background: var(--bg-card); padding: 14px; border-radius: 6px; text-align: center; }
        .stat-val { font-size: 1.6rem; font-weight: 700; color: var(--accent); }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Open Source Issue Scout + Fix Coach</h1>
                <div class="subtitle">Proof of Concept (POC) Dashboard</div>
            </div>
            <button class="btn" onclick="runScout()">Run Scout</button>
        </header>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="openTab('scout')">Scout Shortlist</button>
            <button class="tab-btn" onclick="openTab('profile')">Profile Settings</button>
            <button class="tab-btn" onclick="openTab('coach')">Fix Coach</button>
            <button class="tab-btn" onclick="openTab('tracker')">Contribution Tracker</button>
        </div>

        <!-- Tab 1: Scout -->
        <div id="tab-scout" class="tab-panel active">
            <div class="card">
                <h2>Candidate Issues Shortlist (Top 5)</h2>
                <div id="shortlist-container">
                    <p class="meta-text">Loading recommended candidate issues...</p>
                </div>
            </div>
        </div>

        <!-- Tab 2: Profile -->
        <div id="tab-profile" class="tab-panel">
            <div class="card">
                <h2>Your Contributor Profile</h2>
                <div class="form-group">
                    <label>GitHub Username</label>
                    <input type="text" id="prof-username" value="user_contributor">
                </div>
                <div class="form-group">
                    <label>Languages (comma separated)</label>
                    <input type="text" id="prof-languages" value="python">
                </div>
                <div class="form-group">
                    <label>Interests / Topics (comma separated)</label>
                    <input type="text" id="prof-interests" value="cli, api, fastapi, requests">
                </div>
                <div class="form-group">
                    <label>Preferred Issue Types</label>
                    <input type="text" id="prof-types" value="good first issue, bug, documentation">
                </div>
                <div class="form-group">
                    <label>Available Hours / Week</label>
                    <input type="number" id="prof-hours" value="5">
                </div>
                <button class="btn" onclick="saveProfile()">Save Profile</button>
            </div>
        </div>

        <!-- Tab 3: Fix Coach -->
        <div id="tab-coach" class="tab-panel">
            <div class="card">
                <h2>Fix Coach Investigation</h2>
                <div id="coach-active-issue">
                    <p class="meta-text">No issue selected yet. Pick an issue from the <strong>Scout Shortlist</strong> tab and click "Investigate with Fix Coach".</p>
                </div>
                <div id="coach-results" style="display:none; margin-top: 16px;">
                    <h3>Investigation Summary</h3>
                    <p id="coach-cause" class="meta-text" style="color:#e2e8f0; margin-top: 6px;"></p>
                    
                    <h3 style="margin-top: 16px;">Proposed Unified Diff Patch</h3>
                    <pre id="coach-diff"></pre>

                    <h3 style="margin-top: 16px;">Sandbox Test Verification</h3>
                    <p id="coach-assessment" style="font-weight:600; margin-top: 4px;"></p>
                    <pre id="coach-test-output"></pre>

                    <div class="action-row" style="margin-top: 16px;">
                        <button class="btn btn-success" onclick="recordDecision('accepted')">Accept Fix & Ready PR</button>
                        <button class="btn btn-danger" onclick="recordDecision('skipped')">Skip Issue</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 4: Tracker -->
        <div id="tab-tracker" class="tab-panel">
            <div class="card">
                <h2>Contribution Outcomes & Tracker</h2>
                <div class="stats-grid" id="stats-grid">
                    <div class="stat-card"><div class="stat-val" id="stat-reviewed">0</div><div class="stat-label">Reviewed</div></div>
                    <div class="stat-card"><div class="stat-val" id="stat-accepted">0</div><div class="stat-label">Accepted</div></div>
                    <div class="stat-card"><div class="stat-val" id="stat-prs">0</div><div class="stat-label">PRs Created</div></div>
                    <div class="stat-card"><div class="stat-val" id="stat-rate">0%</div><div class="stat-label">Acceptance Rate</div></div>
                </div>

                <h3>Tracked Issues</h3>
                <div id="history-container" style="margin-top: 12px;">
                    <p class="meta-text">No tracked contributions yet.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentIssue = null;

        function openTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
            if(tabName === 'tracker') loadTracker();
        }

        async function saveProfile() {
            const data = {
                github_username: document.getElementById('prof-username').value,
                languages: document.getElementById('prof-languages').value.split(',').map(s=>s.trim()),
                interests: document.getElementById('prof-interests').value.split(',').map(s=>s.trim()),
                preferred_issue_types: document.getElementById('prof-types').value.split(',').map(s=>s.trim()),
                available_hours_per_week: parseInt(document.getElementById('prof-hours').value)
            };
            const res = await fetch('/api/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if(res.ok) alert('Profile saved successfully!');
        }

        async function runScout() {
            const container = document.getElementById('shortlist-container');
            container.innerHTML = '<p class="meta-text">Fetching and ranking candidate issues from GitHub...</p>';
            try {
                const res = await fetch('/api/scout');
                const issues = await res.json();
                if(!issues.length) {
                    container.innerHTML = '<p class="meta-text">No eligible issues found matching current criteria.</p>';
                    return;
                }
                container.innerHTML = issues.map((item, idx) => `
                    <div class="issue-card">
                        <div class="issue-title">
                            <a href="${item.issue.url}" target="_blank">#${item.issue.github_issue_id}: ${item.issue.title}</a>
                        </div>
                        <div>
                            <span class="badge badge-score">Match Score: ${item.score}</span>
                            <span class="badge badge-easy">${item.difficulty}</span>
                            <span class="badge badge-time">${item.estimated_time}</span>
                            <span class="badge">${item.issue.repository}</span>
                        </div>
                        <div class="meta-text"><strong>Why it matches:</strong> ${item.match_reason}</div>
                        <div class="meta-text" style="color:var(--warning)"><strong>Risk / Uncertainty:</strong> ${item.risk_or_uncertainty}</div>
                        <div class="action-row">
                            <button class="btn" onclick="startCoach(${JSON.stringify(item).replace(/"/g, '&quot;')})">Investigate with Fix Coach</button>
                            <button class="btn btn-secondary" onclick="recordSkip(${item.issue.github_issue_id})">Skip</button>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                container.innerHTML = '<p class="meta-text" style="color:var(--danger)">Error fetching scout candidates: ' + err + '</p>';
            }
        }

        function startCoach(item) {
            currentIssue = item;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-btn')[2].classList.add('active');
            document.getElementById('tab-coach').classList.add('active');

            document.getElementById('coach-active-issue').innerHTML = `
                <div class="issue-card" style="border-left-color:var(--accent);">
                    <div class="issue-title">[${item.issue.repository}] ${item.issue.title}</div>
                    <div class="meta-text">Investigating codebase and generating testable fix plan...</div>
                </div>
            `;
            runInvestigation(item);
        }

        async function runInvestigation(item) {
            const resultsDiv = document.getElementById('coach-results');
            resultsDiv.style.display = 'none';
            try {
                const res = await fetch('/api/coach/investigate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(item.issue)
                });
                const report = await res.json();
                resultsDiv.style.display = 'block';
                document.getElementById('coach-cause').innerText = report.investigation.likely_cause;
                document.getElementById('coach-diff').innerText = report.verification.diff || "No diff generated.";
                const assessElem = document.getElementById('coach-assessment');
                assessElem.innerText = report.verification.confidence_assessment;
                assessElem.style.color = report.verification.tests_passed ? "var(--success)" : "var(--danger)";
                document.getElementById('coach-test-output').innerText = report.verification.test_output;
            } catch (err) {
                alert('Investigation error: ' + err);
            }
        }

        async function recordDecision(decision) {
            if(!currentIssue) return;
            await fetch('/api/tracker/decision', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    issue_id: currentIssue.issue.id || 1,
                    decision: decision,
                    patch_status: 'generated',
                    test_status: 'passed'
                })
            });
            alert('Decision recorded: ' + decision);
            loadTracker();
        }

        async function recordSkip(githubId) {
            await fetch('/api/tracker/decision', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    issue_id: 1,
                    decision: 'skipped',
                    feedback: 'User skipped from shortlist'
                })
            });
            alert('Issue marked as skipped.');
        }

        async function loadTracker() {
            const statsRes = await fetch('/api/tracker/stats');
            const stats = await statsRes.json();
            document.getElementById('stat-reviewed').innerText = stats.total_reviewed;
            document.getElementById('stat-accepted').innerText = stats.accepted;
            document.getElementById('stat-prs').innerText = stats.prs_created;
            document.getElementById('stat-rate').innerText = stats.acceptance_rate + '%';

            const histRes = await fetch('/api/tracker/history');
            const hist = await histRes.json();
            const container = document.getElementById('history-container');
            if(!hist.length) {
                container.innerHTML = '<p class="meta-text">No tracked contributions yet.</p>';
                return;
            }
            container.innerHTML = hist.map(h => `
                <div class="issue-card">
                    <div class="issue-title">${h.title || 'Issue #' + h.issue_id}</div>
                    <div class="meta-text">Decision: <strong>${h.user_decision}</strong> | Tests: ${h.test_status} | PR Status: ${h.pr_status || 'None'}</div>
                </div>
            `).join('');
        }

        // Initialize shortlist on start
        runScout();
    </script>
</body>
</html>
"""
