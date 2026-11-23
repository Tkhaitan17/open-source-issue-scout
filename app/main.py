from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.config import DEFAULT_LANGUAGE
from app.database.models import UserProfile, IssueItem
from app.database.repository import Repository
from app.github.client import GitHubClient
from app.github.issue_collector import IssueCollector
from app.scout.filters import EligibilityFilter
from app.scout.ranker import IssueRanker, ScoredIssue
from app.coach.investigator import Investigator, InvestigationResult
from app.coach.patcher import Patcher, PatchPlan
from app.coach.verifier import Verifier, VerificationReport
from app.tracker.service import TrackerService
from app.ui.dashboard import get_dashboard_html

app = FastAPI(title="Open Source Issue Scout + Fix Coach", version="0.1.0")

# Services
repo = Repository()
github_client = GitHubClient()
collector = IssueCollector(github_client)
filters = EligibilityFilter()
ranker = IssueRanker()
investigator = Investigator()
verifier = Verifier()
tracker = TrackerService(repo)

class DecisionPayload(BaseModel):
    issue_id: int
    decision: str
    feedback: Optional[str] = None
    patch_status: str = "none"
    test_status: str = "not_run"

class PRSubmissionPayload(BaseModel):
    issue_id: int
    pr_url: str
    pr_status: str = "open"

@app.get("/", response_class=HTMLResponse)
def index():
    """Serves the interactive web dashboard."""
    return get_dashboard_html()

@app.get("/api/profile", response_model=Optional[UserProfile])
def get_user_profile(username: str = "user_contributor"):
    prof = repo.get_profile(username)
    if not prof:
        # Return default profile
        return UserProfile(
            github_username=username,
            languages=[DEFAULT_LANGUAGE],
            interests=["cli", "api", "fastapi"],
            preferred_issue_types=["good first issue", "bug"],
            available_hours_per_week=5
        )
    return prof

@app.post("/api/profile")
def save_user_profile(profile: UserProfile):
    repo.save_profile(profile)
    return {"status": "ok", "message": "Profile saved successfully"}

@app.get("/api/scout", response_model=List[ScoredIssue])
def scout_issues(language: str = DEFAULT_LANGUAGE, max_candidates: int = 10):
    """
    Finds open candidate issues from GitHub, filters them,
    and returns the top ranked shortlist.
    """
    profile = get_user_profile()
    try:
        raw_candidates = collector.collect_candidates(
            language=profile.languages[0] if profile.languages else language,
            labels=profile.preferred_issue_types,
            max_results=max_candidates
        )
    except Exception:
        # Fallback to local DB if unauthenticated rate limit reached
        cached = repo.get_open_issues(limit=max_candidates)
        raw_candidates = [
            IssueItem(
                id=c["id"],
                github_issue_id=c["github_issue_id"],
                repository=c["repository"],
                title=c["title"],
                url=c["url"],
                status=c["status"],
                labels=[]
            ) for c in cached
        ]

    # Save candidates to local DB
    if raw_candidates:
        repo.save_issues(raw_candidates)

    # Filter candidates
    eligible = filters.filter_candidates(raw_candidates, profile)

    # Rank and generate shortlist
    shortlist = ranker.rank(eligible, profile, top_n=5)
    return shortlist

@app.post("/api/coach/investigate")
def investigate_issue(issue: IssueItem) -> Dict[str, Any]:
    """
    Fix Coach endpoint: inspects candidate files, generates fix plan & patch,
    and runs sandbox verification.
    """
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / (issue.repository.split("/")[-1] if "/" in issue.repository else "repo")
        repo_dir.mkdir(exist_ok=True)
        
        # In a real environment with Git, we clone:
        # repo_dir = investigator.clone_repository(issue.repository, Path(tmpdir))
        # For fast local POC demonstration without full remote clone overhead:
        inv_result = investigator.investigate(issue, repo_dir)
        
        # Simulated patch and verification
        plan = PatchPlan(
            summary=f"Fix identified issue in {issue.repository}",
            steps=["Locate edge-case handling in primary module", "Add defensive check and tests"],
            diff_content=f"--- a/core.py\n+++ b/core.py\n@@ -10,3 +10,4 @@\n def execute():\n+    # Defensive validation\n     pass\n"
        )
        report = verifier.verify(inv_result, patch_plan=plan)

        return {
            "investigation": inv_result.dict(),
            "patch_plan": plan.dict(),
            "verification": report.dict()
        }

@app.post("/api/tracker/decision")
def record_decision(payload: DecisionPayload):
    cid = tracker.record_decision(
        issue_id=payload.issue_id,
        decision=payload.decision,
        feedback=payload.feedback,
        patch_status=payload.patch_status,
        test_status=payload.test_status
    )
    return {"status": "ok", "contribution_id": cid}

@app.post("/api/tracker/pr")
def record_pr(payload: PRSubmissionPayload):
    tracker.record_pr_submission(
        issue_id=payload.issue_id,
        pr_url=payload.pr_url,
        pr_status=payload.pr_status
    )
    return {"status": "ok"}

@app.get("/api/tracker/history")
def get_tracker_history():
    return tracker.get_history()

@app.get("/api/tracker/stats")
def get_tracker_stats():
    return tracker.get_stats()
