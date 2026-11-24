def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Issue Scout + Fix Coach</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #09090b;
            --surface: #18181b;
            --surface2: #27272a;
            --border: #3f3f46;
            --accent: #6366f1;
            --accent-light: #818cf8;
            --accent-glow: rgba(99,102,241,0.15);
            --green: #22c55e;
            --green-bg: rgba(34,197,94,0.1);
            --red: #ef4444;
            --red-bg: rgba(239,68,68,0.1);
            --yellow: #eab308;
            --yellow-bg: rgba(234,179,8,0.1);
            --blue: #3b82f6;
            --text: #fafafa;
            --text-muted: #a1a1aa;
            --text-dim: #71717a;
            --radius: 10px;
            --shadow: 0 4px 24px rgba(0,0,0,0.5);
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }

        /* ── Sidebar layout ── */
        .layout { display: flex; min-height: 100vh; }
        .sidebar {
            width: 220px;
            background: var(--surface);
            border-right: 1px solid var(--border);
            padding: 24px 0;
            display: flex;
            flex-direction: column;
            gap: 4px;
            flex-shrink: 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar-logo {
            padding: 0 20px 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 8px;
        }
        .sidebar-logo .logo-icon { font-size: 1.4rem; }
        .sidebar-logo h1 { font-size: 0.95rem; font-weight: 700; color: var(--text); line-height: 1.3; margin-top: 6px; }
        .sidebar-logo p { font-size: 0.72rem; color: var(--text-dim); margin-top: 2px; }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 20px;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
            border-radius: 0;
            transition: background 0.15s, color 0.15s;
        }
        .nav-item:hover { background: var(--surface2); color: var(--text); }
        .nav-item.active { background: var(--accent-glow); color: var(--accent-light); border-right: 2px solid var(--accent); }
        .nav-item .nav-icon { font-size: 1rem; width: 20px; }
        .sidebar-bottom {
            margin-top: auto;
            padding: 16px 20px 0;
            border-top: 1px solid var(--border);
        }
        .llm-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: var(--surface2);
            border-radius: 8px;
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
        .dot-green { background: var(--green); box-shadow: 0 0 6px var(--green); }
        .dot-red { background: var(--red); }
        .dot-grey { background: var(--border); }

        /* ── Main content ── */
        .main { margin-left: 220px; padding: 32px 36px; max-width: 1000px; }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        /* ── Page header ── */
        .page-header { margin-bottom: 28px; }
        .page-header h2 { font-size: 1.4rem; font-weight: 700; }
        .page-header p { color: var(--text-muted); font-size: 0.875rem; margin-top: 4px; }

        /* ── Cards ── */
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            margin-bottom: 20px;
        }
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border);
        }
        .card-header h3 { font-size: 1rem; font-weight: 600; }

        /* ── Buttons ── */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: opacity 0.15s, transform 0.1s;
        }
        .btn:hover { opacity: 0.88; transform: translateY(-1px); }
        .btn:active { transform: translateY(0); }
        .btn-primary { background: var(--accent); color: #fff; }
        .btn-ghost { background: var(--surface2); color: var(--text); border: 1px solid var(--border); }
        .btn-success { background: var(--green); color: #000; }
        .btn-danger { background: var(--red); color: #fff; }
        .btn-sm { padding: 5px 12px; font-size: 0.8rem; }

        /* ── Issue Cards ── */
        .issue-card {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 12px;
            transition: border-color 0.15s, box-shadow 0.15s;
        }
        .issue-card:hover { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent-glow); }
        .issue-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 10px; }
        .issue-title a { color: var(--text); text-decoration: none; }
        .issue-title a:hover { color: var(--accent-light); }
        .issue-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 10px;
            font-size: 0.72rem;
            font-weight: 600;
            border-radius: 20px;
            border: 1px solid transparent;
        }
        .badge-score { background: rgba(99,102,241,0.15); color: var(--accent-light); border-color: rgba(99,102,241,0.3); }
        .badge-easy { background: var(--green-bg); color: var(--green); border-color: rgba(34,197,94,0.3); }
        .badge-medium { background: var(--yellow-bg); color: var(--yellow); border-color: rgba(234,179,8,0.3); }
        .badge-time { background: rgba(59,130,246,0.1); color: var(--blue); border-color: rgba(59,130,246,0.3); }
        .badge-repo { background: var(--surface2); color: var(--text-muted); border-color: var(--border); }
        .issue-reason { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px; }
        .issue-risk { font-size: 0.8rem; color: var(--yellow); }
        .issue-actions { display: flex; gap: 8px; margin-top: 14px; }

        /* ── Stats ── */
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
        .stat-card {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .stat-val { font-size: 1.8rem; font-weight: 700; color: var(--accent-light); }
        .stat-label { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }

        /* ── Form ── */
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; letter-spacing: 0.03em; text-transform: uppercase; }
        .form-input {
            width: 100%;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 9px 14px;
            color: var(--text);
            font-size: 0.875rem;
            font-family: inherit;
            transition: border-color 0.15s, box-shadow 0.15s;
        }
        .form-input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }

        /* ── Code blocks ── */
        pre {
            background: #05050a;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #a5f3fc;
            line-height: 1.6;
            margin-top: 10px;
            white-space: pre-wrap;
            word-break: break-all;
        }

        /* ── Toggle ── */
        .toggle-row {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .toggle-label { font-size: 0.875rem; font-weight: 500; }
        .toggle-desc { font-size: 0.775rem; color: var(--text-muted); }
        .switch { position: relative; display: inline-block; width: 42px; height: 24px; flex-shrink: 0; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; inset: 0; background: var(--border);
            border-radius: 24px; cursor: pointer;
            transition: background 0.2s;
        }
        .slider::before {
            content: ""; position: absolute;
            width: 18px; height: 18px;
            left: 3px; bottom: 3px;
            background: #fff; border-radius: 50%;
            transition: transform 0.2s;
        }
        input:checked + .slider { background: var(--accent); }
        input:checked + .slider::before { transform: translateX(18px); }

        /* ── Alerts ── */
        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            margin-bottom: 14px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        .alert-success { background: var(--green-bg); color: var(--green); border: 1px solid rgba(34,197,94,0.25); }
        .alert-warn { background: var(--yellow-bg); color: var(--yellow); border: 1px solid rgba(234,179,8,0.25); }
        .alert-info { background: var(--accent-glow); color: var(--accent-light); border: 1px solid rgba(99,102,241,0.25); }
        .alert-error { background: var(--red-bg); color: var(--red); border: 1px solid rgba(239,68,68,0.25); }

        /* ── Spinner ── */
        .spinner {
            display: inline-block;
            width: 16px; height: 16px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Divider ── */
        .divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

        /* ── Empty state ── */
        .empty {
            text-align: center;
            padding: 48px 24px;
            color: var(--text-dim);
        }
        .empty .empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
        .empty p { font-size: 0.875rem; }

        /* ── Section label ── */
        .section-label {
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0 20px;
            margin: 10px 0 4px;
        }
    </style>
</head>
<body>
<div class="layout">

    <!-- ── Sidebar ── -->
    <nav class="sidebar">
        <div class="sidebar-logo">
            <div class="logo-icon">🔍</div>
            <h1>Issue Scout<br>+ Fix Coach</h1>
            <p>Open Source POC</p>
        </div>

        <div class="section-label">Navigation</div>
        <button class="nav-item active" onclick="switchTab('scout', this)">
            <span class="nav-icon">📋</span> Scout Shortlist
        </button>
        <button class="nav-item" onclick="switchTab('profile', this)">
            <span class="nav-icon">👤</span> Profile
        </button>
        <button class="nav-item" onclick="switchTab('coach', this)">
            <span class="nav-icon">🛠</span> Fix Coach
        </button>
        <button class="nav-item" onclick="switchTab('tracker', this)">
            <span class="nav-icon">📊</span> Tracker
        </button>

        <div class="sidebar-bottom">
            <div class="llm-pill">
                <div class="dot dot-grey" id="llm-dot"></div>
                <div>
                    <div style="font-weight:600;" id="llm-pill-label">LLM</div>
                    <div id="llm-pill-model" style="font-size:0.68rem;color:var(--text-dim)">Checking...</div>
                </div>
            </div>
        </div>
    </nav>

    <!-- ── Main ── -->
    <main class="main">

        <!-- ── Scout Tab ── -->
        <div id="tab-scout" class="tab-panel active">
            <div class="page-header">
                <h2>Candidate Issues</h2>
                <p>Top-ranked open source issues that match your contributor profile.</p>
            </div>
            <div class="card">
                <div class="card-header">
                    <h3>Shortlist <span id="issue-count" style="color:var(--text-dim);font-weight:400;font-size:0.85rem;"></span></h3>
                    <button class="btn btn-primary btn-sm" onclick="runScout()">
                        <span>⟳</span> Refresh
                    </button>
                </div>
                <div id="shortlist-container">
                    <div class="empty">
                        <div class="empty-icon">🔍</div>
                        <p>Loading issues from GitHub...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Profile Tab ── -->
        <div id="tab-profile" class="tab-panel">
            <div class="page-header">
                <h2>Contributor Profile</h2>
                <p>Personalise the scout to find issues that fit your skills and interests.</p>
            </div>
            <div class="card">
                <div class="card-header"><h3>Your Settings</h3></div>
                <div class="form-group">
                    <label class="form-label">GitHub Username</label>
                    <input class="form-input" type="text" id="prof-username" value="user_contributor" placeholder="e.g. octocat">
                </div>
                <div class="form-group">
                    <label class="form-label">Languages (comma separated)</label>
                    <input class="form-input" type="text" id="prof-languages" value="python" placeholder="python, javascript, go">
                </div>
                <div class="form-group">
                    <label class="form-label">Topics / Interests</label>
                    <input class="form-input" type="text" id="prof-interests" value="cli, api, fastapi, requests" placeholder="api, testing, cli, ...">
                </div>
                <div class="form-group">
                    <label class="form-label">Preferred Issue Types</label>
                    <input class="form-input" type="text" id="prof-types" value="good first issue, bug, documentation">
                </div>
                <div class="form-group">
                    <label class="form-label">Available Hours / Week</label>
                    <input class="form-input" type="number" id="prof-hours" value="5" min="1" max="40">
                </div>
                <button class="btn btn-primary" onclick="saveProfile()">Save Profile</button>
            </div>
        </div>

        <!-- ── Fix Coach Tab ── -->
        <div id="tab-coach" class="tab-panel">
            <div class="page-header">
                <h2>Fix Coach</h2>
                <p>AI-powered investigation and patch generation for selected issues.</p>
            </div>

            <!-- LLM toggle -->
            <div class="toggle-row">
                <label class="switch">
                    <input type="checkbox" id="llm-toggle" checked onchange="updateToggleUI()">
                    <span class="slider"></span>
                </label>
                <div>
                    <div class="toggle-label">Use Groq LLM for patch generation</div>
                    <div class="toggle-desc" id="toggle-desc">When enabled, the Fix Coach calls the Groq API to generate a real diff.</div>
                </div>
                <span id="llm-toggle-badge" class="badge badge-score" style="margin-left:auto;"></span>
            </div>

            <div class="card" id="coach-card">
                <div class="card-header"><h3>Investigation</h3></div>
                <div id="coach-active-issue">
                    <div class="empty">
                        <div class="empty-icon">🛠</div>
                        <p>No issue selected. Go to <strong>Scout Shortlist</strong> and click <em>Investigate</em>.</p>
                    </div>
                </div>

                <div id="coach-results" style="display:none;">
                    <div id="llm-used-banner" style="display:none;" class="alert"></div>

                    <div style="margin-bottom:16px;">
                        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-dim);margin-bottom:6px;">Root Cause Analysis</div>
                        <p id="coach-cause" style="color:var(--text-muted);font-size:0.875rem;line-height:1.6;"></p>
                    </div>

                    <hr class="divider">

                    <div style="margin-bottom:16px;">
                        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-dim);margin-bottom:6px;">Proposed Patch</div>
                        <pre id="coach-diff">No diff generated.</pre>
                    </div>

                    <hr class="divider">

                    <div style="margin-bottom:20px;">
                        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-dim);margin-bottom:6px;">Sandbox Verification</div>
                        <p id="coach-assessment" style="font-size:0.875rem;font-weight:600;margin-bottom:8px;"></p>
                        <pre id="coach-test-output"></pre>
                    </div>

                    <div style="display:flex;gap:10px;">
                        <button class="btn btn-success" onclick="recordDecision('accepted')">✓ Accept Fix &amp; Ready PR</button>
                        <button class="btn btn-danger" onclick="recordDecision('skipped')">✕ Skip Issue</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Tracker Tab ── -->
        <div id="tab-tracker" class="tab-panel">
            <div class="page-header">
                <h2>Contribution Tracker</h2>
                <p>Track all your reviewed and accepted fixes across sessions.</p>
            </div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-val" id="stat-reviewed">–</div><div class="stat-label">Reviewed</div></div>
                <div class="stat-card"><div class="stat-val" id="stat-accepted">–</div><div class="stat-label">Accepted</div></div>
                <div class="stat-card"><div class="stat-val" id="stat-prs">–</div><div class="stat-label">PRs Created</div></div>
                <div class="stat-card"><div class="stat-val" id="stat-rate">–</div><div class="stat-label">Acceptance Rate</div></div>
            </div>
            <div class="card">
                <div class="card-header"><h3>History</h3></div>
                <div id="history-container">
                    <div class="empty"><div class="empty-icon">📊</div><p>No contributions tracked yet.</p></div>
                </div>
            </div>
        </div>

    </main>
</div>

<script>
    let currentIssue = null;

    // ── Tab navigation ──
    function switchTab(name, btn) {
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-' + name).classList.add('active');
        btn.classList.add('active');
        if (name === 'tracker') loadTracker();
    }

    // ── LLM status ──
    async function checkLLMStatus() {
        try {
            const r = await fetch('/api/llm/status');
            const d = await r.json();
            const dot = document.getElementById('llm-dot');
            const label = document.getElementById('llm-pill-label');
            const model = document.getElementById('llm-pill-model');
            const badge = document.getElementById('llm-toggle-badge');
            if (d.available) {
                dot.className = 'dot dot-green';
                label.textContent = d.provider + ' ✓';
                model.textContent = d.model.length > 20 ? d.model.slice(0, 20) + '…' : d.model;
                badge.textContent = '✓ ' + d.provider + ' Connected';
                badge.className = 'badge badge-easy';
            } else {
                dot.className = 'dot dot-red';
                label.textContent = 'LLM Offline';
                model.textContent = 'No API key set';
                badge.textContent = 'LLM Not Configured';
                badge.className = 'badge';
                badge.style.background = 'var(--red-bg)';
                badge.style.color = 'var(--red)';
                document.getElementById('llm-toggle').checked = false;
                updateToggleUI();
            }
        } catch(e) {
            document.getElementById('llm-pill-label').textContent = 'LLM Offline';
        }
    }

    function updateToggleUI() {
        const on = document.getElementById('llm-toggle').checked;
        document.getElementById('toggle-desc').textContent = on
            ? 'Groq will generate a real code diff for this issue.'
            : 'Using stub diff (no LLM call). Enable to get AI-generated patches.';
    }

    // ── Profile ──
    async function saveProfile() {
        const data = {
            github_username: document.getElementById('prof-username').value,
            languages: document.getElementById('prof-languages').value.split(',').map(s => s.trim()),
            interests: document.getElementById('prof-interests').value.split(',').map(s => s.trim()),
            preferred_issue_types: document.getElementById('prof-types').value.split(',').map(s => s.trim()),
            available_hours_per_week: parseInt(document.getElementById('prof-hours').value)
        };
        const res = await fetch('/api/profile', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
        });
        if (res.ok) showToast('✓ Profile saved!', 'success');
    }

    // ── Scout ──
    async function runScout() {
        const container = document.getElementById('shortlist-container');
        container.innerHTML = '<div class="empty"><div class="spinner"></div><p style="margin-top:14px;">Fetching issues from GitHub...</p></div>';
        document.getElementById('issue-count').textContent = '';
        try {
            const res = await fetch('/api/scout');
            const issues = await res.json();
            if (!issues.length) {
                container.innerHTML = '<div class="empty"><div class="empty-icon">🕵️</div><p>No matching issues found right now. Try adjusting your profile.</p></div>';
                return;
            }
            document.getElementById('issue-count').textContent = `(${issues.length} found)`;
            container.innerHTML = issues.map((item) => {
                const diffBadge = item.difficulty === 'Beginner'
                    ? `<span class="badge badge-easy">● Beginner</span>`
                    : `<span class="badge badge-medium">● ${item.difficulty}</span>`;
                return `
                <div class="issue-card">
                    <div class="issue-title">
                        <a href="${item.issue.url}" target="_blank">#${item.issue.github_issue_id}: ${escHtml(item.issue.title)}</a>
                    </div>
                    <div class="issue-meta">
                        <span class="badge badge-score">⚡ ${item.score}</span>
                        ${diffBadge}
                        <span class="badge badge-time">🕐 ${item.estimated_time}</span>
                        <span class="badge badge-repo">📦 ${escHtml(item.issue.repository)}</span>
                    </div>
                    <div class="issue-reason">💡 ${escHtml(item.match_reason)}</div>
                    <div class="issue-risk">⚠ ${escHtml(item.risk_or_uncertainty)}</div>
                    <div class="issue-actions">
                        <button class="btn btn-primary btn-sm" onclick='startCoach(${JSON.stringify(item).replace(/'/g, "&#39;")})'>🛠 Investigate</button>
                        <button class="btn btn-ghost btn-sm" onclick="recordSkip(${item.issue.github_issue_id})">Skip</button>
                    </div>
                </div>`;
            }).join('');
        } catch (err) {
            container.innerHTML = `<div class="alert alert-error">⚠ Failed to fetch issues: ${err}</div>`;
        }
    }

    // ── Fix Coach ──
    function startCoach(item) {
        currentIssue = item;
        // Switch to coach tab
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-coach').classList.add('active');
        document.querySelectorAll('.nav-item')[2].classList.add('active');

        document.getElementById('coach-active-issue').innerHTML = `
            <div class="issue-card" style="margin-bottom:20px;">
                <div class="issue-title">📌 ${escHtml(item.issue.repository)} — ${escHtml(item.issue.title)}</div>
                <div class="issue-meta">
                    <span class="badge badge-score">⚡ ${item.score}</span>
                    <span class="badge badge-time">🕐 ${item.estimated_time}</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;margin-top:12px;font-size:0.85rem;color:var(--text-muted);">
                    <div class="spinner"></div> Running investigation...
                </div>
            </div>`;
        document.getElementById('coach-results').style.display = 'none';
        runInvestigation(item);
    }

    async function runInvestigation(item) {
        const useLLM = document.getElementById('llm-toggle').checked;
        try {
            const res = await fetch('/api/coach/investigate?use_llm=' + useLLM, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(item.issue)
            });
            const report = await res.json();
            const resultsDiv = document.getElementById('coach-results');
            resultsDiv.style.display = 'block';

            // LLM banner
            const banner = document.getElementById('llm-used-banner');
            if (report.llm_used) {
                banner.style.display = 'flex';
                banner.className = 'alert alert-info';
                banner.textContent = '✦ Patch generated by Groq LLM (' + report.patch_plan.summary.slice(0, 60) + ')';
            } else {
                banner.style.display = 'flex';
                banner.className = 'alert alert-warn';
                banner.textContent = '⚠ LLM not used — showing stub patch. Enable the toggle above and re-investigate.';
            }

            document.getElementById('coach-cause').textContent = report.investigation.likely_cause;
            document.getElementById('coach-diff').textContent = report.verification.diff || report.patch_plan.diff_content || 'No diff generated.';

            const asmEl = document.getElementById('coach-assessment');
            asmEl.textContent = report.verification.confidence_assessment;
            asmEl.style.color = report.verification.tests_passed ? 'var(--green)' : 'var(--yellow)';

            document.getElementById('coach-test-output').textContent = report.verification.test_output || '(No test output)';

            // Update active-issue header (without spinner)
            document.getElementById('coach-active-issue').innerHTML = `
                <div class="issue-card" style="margin-bottom:20px;">
                    <div class="issue-title">📌 ${escHtml(item.issue.repository)} — ${escHtml(item.issue.title)}</div>
                    <div class="issue-meta">
                        <span class="badge badge-score">⚡ ${item.score}</span>
                        <span class="badge badge-time">🕐 ${item.estimated_time}</span>
                    </div>
                </div>`;
        } catch (err) {
            document.getElementById('coach-active-issue').innerHTML = `<div class="alert alert-error">⚠ Investigation failed: ${err}</div>`;
        }
    }

    async function recordDecision(decision) {
        if (!currentIssue) return;
        await fetch('/api/tracker/decision', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ issue_id: currentIssue.issue.id || 1, decision, patch_status: 'generated', test_status: 'run' })
        });
        showToast(decision === 'accepted' ? '✓ Fix accepted! Ready for PR.' : 'Issue skipped.', decision === 'accepted' ? 'success' : 'warn');
    }

    async function recordSkip(githubId) {
        await fetch('/api/tracker/decision', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ issue_id: 1, decision: 'skipped', feedback: 'Skipped from shortlist' })
        });
        showToast('Issue skipped.', 'warn');
    }

    async function loadTracker() {
        try {
            const [sRes, hRes] = await Promise.all([fetch('/api/tracker/stats'), fetch('/api/tracker/history')]);
            const stats = await sRes.json();
            document.getElementById('stat-reviewed').textContent = stats.total_reviewed;
            document.getElementById('stat-accepted').textContent = stats.accepted;
            document.getElementById('stat-prs').textContent = stats.prs_created;
            document.getElementById('stat-rate').textContent = stats.acceptance_rate + '%';

            const hist = await hRes.json();
            const container = document.getElementById('history-container');
            if (!hist.length) {
                container.innerHTML = '<div class="empty"><div class="empty-icon">📊</div><p>No contributions tracked yet.</p></div>';
                return;
            }
            container.innerHTML = hist.map(h => `
                <div class="issue-card">
                    <div class="issue-title">${escHtml(h.title || 'Issue #' + h.issue_id)}</div>
                    <div class="issue-meta">
                        <span class="badge ${h.user_decision === 'accepted' ? 'badge-easy' : ''}">${h.user_decision}</span>
                        <span class="badge badge-repo">Tests: ${h.test_status}</span>
                        ${h.pr_status ? '<span class="badge badge-score">PR: ' + h.pr_status + '</span>' : ''}
                    </div>
                </div>`).join('');
        } catch(e) {}
    }

    // ── Toast ──
    function showToast(msg, type = 'info') {
        const t = document.createElement('div');
        t.className = 'alert alert-' + (type === 'success' ? 'success' : type === 'warn' ? 'warn' : 'info');
        t.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;min-width:220px;animation:fadeIn 0.2s;';
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 3000);
    }

    function escHtml(s) {
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ── Init ──
    checkLLMStatus();
    updateToggleUI();
    runScout();
</script>
</body>
</html>"""
