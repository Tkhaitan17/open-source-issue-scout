"""
Verification test for Step 2: Eligibility Filtering & Ranking Engine
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.models import UserProfile, IssueItem
from app.database.repository import Repository
from app.scout.filters import EligibilityFilter
from app.scout.ranker import IssueRanker

def test_filters():
    print("--> Testing Eligibility Filter...")
    filter_engine = EligibilityFilter(min_description_length=20)
    
    # 1. Closed issue
    issue1 = IssueItem(github_issue_id=1, repository="test/repo", title="Bug 1", url="http://", status="closed")
    ok1, reason1 = filter_engine.is_eligible(issue1)
    assert not ok1 and "not open" in reason1

    # 2. Issue with disqualifying label
    issue2 = IssueItem(github_issue_id=2, repository="test/repo", title="Bug 2", url="http://", labels=["wontfix"], metadata=json.dumps({"body_snippet": "Valid length body description here"}))
    ok2, reason2 = filter_engine.is_eligible(issue2)
    assert not ok2 and "wontfix" in reason2

    # 3. Issue with very short/vague body
    issue3 = IssueItem(github_issue_id=3, repository="test/repo", title="Bug 3", url="http://", metadata=json.dumps({"body_snippet": "too short"}))
    ok3, reason3 = filter_engine.is_eligible(issue3)
    assert not ok3 and "too vague" in reason3

    # 4. Valid issue
    issue4 = IssueItem(github_issue_id=4, repository="test/repo", title="Fix parser crash", url="http://", labels=["good first issue"], metadata=json.dumps({"body_snippet": "When calling parser with None it crashes. Here is repro: ```python parse(None)```"}))
    ok4, reason4 = filter_engine.is_eligible(issue4)
    assert ok4, f"Valid issue failed: {reason4}"
    print("[PASS] Eligibility filter passed all negative and positive checks.")

def test_ranker_and_db():
    print("\n--> Testing Ranker & Recommendation Persistence...")
    profile = UserProfile(
        github_username="dev_user",
        languages=["python"],
        interests=["cli", "fastapi"],
        preferred_issue_types=["bug", "good first issue"],
        available_hours_per_week=5
    )

    issue_low = IssueItem(
        github_issue_id=10,
        repository="org/backend",
        title="Update random config",
        url="http://low",
        labels=["enhancement"],
        metadata=json.dumps({"body_snippet": "Some config value should be changed.", "comments_count": 2})
    )

    issue_high = IssueItem(
        github_issue_id=11,
        repository="org/cli-tool",
        title="CLI parser crashes on empty args",
        url="http://high",
        labels=["good first issue", "bug"],
        metadata=json.dumps({"body_snippet": "Steps to reproduce: run `cli-tool` with empty arguments. Expected help message.", "comments_count": 0})
    )

    ranker = IssueRanker()
    ranked = ranker.rank([issue_low, issue_high], profile=profile, top_n=2)
    
    assert ranked[0].issue.github_issue_id == 11, "High match issue should be ranked #1"
    assert ranked[0].score > ranked[1].score
    assert "CLI" in ranked[0].issue.title
    print(f"[PASS] Ranking order confirmed. Top score: {ranked[0].score} vs Lower score: {ranked[1].score}")
    print(f"       Match Reason: {ranked[0].match_reason}")
    print(f"       Difficulty: {ranked[0].difficulty} | Est. Time: {ranked[0].estimated_time}")

    # Test saving recommendations in DB
    db = Repository(db_path=":memory:")
    db.save_issues([issue_high, issue_low])
    saved_issues = db.get_open_issues()
    high_db_id = saved_issues[0]["id"]
    
    rec_id = db.save_recommendation(
        issue_id=high_db_id,
        score=ranked[0].score,
        reason=ranked[0].match_reason,
        difficulty=ranked[0].difficulty,
        estimated_time=ranked[0].estimated_time
    )
    assert rec_id > 0
    top_recs = db.get_top_recommendations()
    assert len(top_recs) == 1
    assert top_recs[0]["title"] == issue_high.title
    print("[PASS] Recommendations stored and queried from database successfully.")

if __name__ == "__main__":
    test_filters()
    test_ranker_and_db()
    print("\nAll Step 2 tests passed successfully!")
