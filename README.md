# Open Source Issue Scout + Fix Coach (POC v1)

A developer assistant that finds suitable open-source issues, investigates root causes, proposes verified code patches, and tracks your open-source contributions.

---

## Features Built in POC v1

1. **Contributor Profile:** Store your languages, interests, and preferred issue types (`app/database/models.py`).
2. **Issue Collector & GitHub Client:** Queries real-time open-source issues via GitHub REST API without requiring upfront tokens (`app/github/`).
3. **Smart Eligibility Filters:** Eliminates closed, assigned, duplicate, or stale issues (`app/scout/filters.py`).
4. **Issue Ranker & Shortlist:** Transparent scoring (0–100) with difficulty rating and plain-language match explanations (`app/scout/ranker.py`).
5. **Fix Coach:** Automatically inspects repos, finds relevant files, suggests fix plans, and generates unified diffs (`app/coach/`).
6. **Sandbox Test Runner:** Runs tests with strict isolation and automatic credential scrubbing (`app/sandbox/runner.py`).
7. **Contribution Tracker:** Logs decisions (accepted, skipped) and calculates stats (`app/tracker/service.py`).
8. **Interactive Web Dashboard:** Modern, responsive UI with built-in Scout, Profile, Fix Coach, and Tracker views (`app/ui/dashboard.py`).

---

## How to Run

Activate your environment and run:

```powershell
cd open-source-issue-scout
python run.py
```

Then open your browser at **`http://localhost:8000`**.
API documentation is also available at **`http://localhost:8000/docs`**.

---

## Verification Test Suite

You can run individual component verification tests:

```powershell
python test_step1.py   # Database & GitHub Collector
python test_step2.py   # Eligibility Filters & Ranker
python test_step3.py   # Fix Coach, Sandbox Isolation, & Patching
python test_step4.py   # Tracker Service & FastAPI Web Endpoints
```
