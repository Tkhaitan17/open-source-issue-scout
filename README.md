# Open Source Issue Scout + Fix Coach (POC v2)

A developer assistant that finds suitable open-source issues, investigates root causes, proposes AI-assisted & sandboxed code patches, and tracks your open-source contributions.

---

## What's New in Phase 2

- **AI-Powered Fix Coach (Groq Integration):** Integrated with Groq's high-speed inference engine using `qwen/qwen3.8-27b` to automatically analyze issues and produce candidate unified diff patches.
- **Interactive LLM Toggle:** Switch seamlessly between AI-generated diffs and reproducible baseline patch stubs directly from the UI.
- **Polished Modern UI:** Redesigned responsive dark-theme dashboard with sidebar navigation, live LLM connectivity indicator, toast notifications, code syntax views, and shortlist cards.
- **Dedicated LLM Test Suite:** Added `test_step5_llm.py` covering unit and mocked integration tests for LLM generation, issue summarization, and graceful fallbacks.

---

## Core Architecture & Features

1. **Contributor Profile:** Store languages, topics/interests, and preferred issue types (`app/database/models.py`).
2. **Issue Collector & GitHub Client:** Queries real-time open-source issues via GitHub REST API without requiring upfront authentication (`app/github/`).
3. **Smart Eligibility Filters:** Eliminates closed, assigned, duplicate, or stale issues (`app/scout/filters.py`).
4. **Issue Ranker & Shortlist:** Transparent scoring (0–100) with difficulty tiering, time estimation, and clear rationale (`app/scout/ranker.py`).
5. **Fix Coach & LLM Client:** Inspects repository files, summarizes issues, generates candidate patches via Groq LLM, and creates unified diffs (`app/coach/`).
6. **Sandbox Test Runner:** Verifies proposed fixes with isolated execution and automatic credential scrubbing (`app/sandbox/runner.py`).
7. **Contribution Tracker:** Logs decisions (accepted, skipped), tracks PR progress, and computes acceptance metrics (`app/tracker/service.py`).
8. **Interactive Web Dashboard:** Clean, responsive UI with Scout Shortlist, Profile Settings, Fix Coach, and Contribution Tracker views (`app/ui/dashboard.py`).

---

## Configuration & Environment Variables

Copy or edit `.env` in the root directory:

```dotenv
# Groq API Key (free tier: https://groq.com)
GROQ_API_KEY=gsk_...

# Optional: GitHub token for higher API rate limits
GITHUB_TOKEN=your_personal_access_token

# Optional: Default target language
DEFAULT_LANGUAGE=python
```

*Note: If `GROQ_API_KEY` is not set or left as placeholder, the Fix Coach automatically falls back to clean baseline diff generation.*

---

## How to Run

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```powershell
   cd open-source-issue-scout
   python run.py
   ```
   *Or with Uvicorn directly:*
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Open the Dashboard:**
   Visit **`http://localhost:8000`** in your browser.  
   Interactive API docs are available at **`http://localhost:8000/docs`**.

---

## Verification Test Suite

Run the full end-to-end component verification suite:

```powershell
python test_step1.py        # Database & GitHub Collector
python test_step2.py        # Eligibility Filters & Ranker
python test_step3.py        # Fix Coach, Sandbox Isolation, & Patching
python test_step4.py        # Tracker Service & FastAPI Web Endpoints
python test_step5_llm.py    # Phase 2: LLM Client & Patch Generation
```
