"""
Verification test for Step 4: Tracker & Full Application Endpoints
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.models import UserProfile, IssueItem
from app.tracker.service import TrackerService
from app.main import (
    app,
    index,
    get_user_profile,
    save_user_profile,
    scout_issues,
    investigate_issue,
    record_decision,
    get_tracker_stats,
    DecisionPayload
)

def test_tracker_service():
    print("--> Testing Tracker Service...")
    tracker = TrackerService()
    
    # 1. Record decision
    cid = tracker.record_decision(
        issue_id=1,
        decision="accepted",
        patch_status="generated",
        test_status="passed"
    )
    assert cid > 0, "Failed to record decision"

    # 2. Update PR
    tracker.record_pr_submission(issue_id=1, pr_url="https://github.com/org/repo/pull/1", pr_status="open")

    # 3. Stats
    stats = tracker.get_stats()
    assert stats["total_reviewed"] >= 1
    assert stats["accepted"] >= 1
    assert stats["prs_created"] >= 1
    assert stats["acceptance_rate"] > 0
    print(f"[PASS] Tracker stats: {stats}")

def test_fastapi_endpoints():
    print("\n--> Testing FastAPI Application Endpoints...")
    
    # 1. Dashboard HTML
    html_resp = index()
    html_content = html_resp if isinstance(html_resp, str) else html_resp.body.decode()
    assert "Issue Scout" in html_content
    print("[PASS] GET / serves the interactive dashboard HTML.")

    # 2. Profile endpoints
    prof = UserProfile(
        github_username="lead_developer",
        languages=["python"],
        interests=["backend", "fastapi"],
        preferred_issue_types=["good first issue"],
        available_hours_per_week=10
    )
    save_resp = save_user_profile(prof)
    assert save_resp["status"] == "ok"
    fetched_prof = get_user_profile(username="lead_developer")
    assert fetched_prof.github_username == "lead_developer"
    print("[PASS] POST & GET /api/profile works correctly.")

    # 3. Scout Shortlist
    shortlist = scout_issues()
    assert isinstance(shortlist, list)
    print(f"[PASS] GET /api/scout returned {len(shortlist)} candidates in shortlist.")

    # 4. Fix Coach Investigation
    sample_issue = IssueItem(
        id=1,
        github_issue_id=999,
        repository="psf/requests",
        title="Handle timeout exception properly",
        url="https://github.com/psf/requests/issues/999"
    )
    coach_resp = investigate_issue(sample_issue)
    assert "investigation" in coach_resp
    assert "patch_plan" in coach_resp
    assert "verification" in coach_resp
    print("[PASS] POST /api/coach/investigate produced investigation, patch plan, and verification.")

    # 5. Tracker decision
    dec_resp = record_decision(DecisionPayload(
        issue_id=1,
        decision="accepted",
        patch_status="generated",
        test_status="passed"
    ))
    assert dec_resp["status"] == "ok"
    print("[PASS] POST /api/tracker/decision successfully tracked decision.")

if __name__ == "__main__":
    test_tracker_service()
    test_fastapi_endpoints()
    print("\nAll Step 4 tests completed successfully!")
