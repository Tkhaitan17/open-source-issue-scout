"""
Smoke test for Step 1: Database and GitHub Collector
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.repository import Repository
from app.database.models import UserProfile, IssueItem
from app.github.issue_collector import IssueCollector

def test_database():
    print("--> Testing Database operations...")
    repo = Repository(db_path=":memory:")
    
    # Save Profile
    test_profile = UserProfile(
        github_username="octocat",
        languages=["python"],
        interests=["cli", "api"],
        preferred_issue_types=["good first issue"],
        available_hours_per_week=5
    )
    repo.save_profile(test_profile)
    fetched = repo.get_profile("octocat")
    assert fetched is not None, "Profile fetch failed!"
    assert fetched.github_username == "octocat"
    assert "python" in fetched.languages
    print("[PASS] User Profile saved and fetched successfully.")

    # Save Issues
    test_issues = [
        IssueItem(
            github_issue_id=101,
            repository="psf/requests",
            title="Fix retry logic",
            url="https://github.com/psf/requests/issues/101",
            labels=["bug"]
        )
    ]
    count = repo.save_issues(test_issues)
    assert count == 1, "Issue save count mismatch!"
    saved = repo.get_open_issues()
    assert len(saved) == 1
    assert saved[0]["title"] == "Fix retry logic"
    print("[PASS] Issues saved and fetched successfully.")

def test_github_collector():
    print("\n--> Testing GitHub Collector (Public Search API)...")
    collector = IssueCollector()
    try:
        candidates = collector.collect_candidates(
            language="python",
            labels=["good first issue"],
            max_results=3
        )
        print(f"[PASS] Successfully fetched {len(candidates)} candidate issues from GitHub.")
        for idx, item in enumerate(candidates, 1):
            print(f"  {idx}. [{item.repository}] {item.title[:60]}... ({item.url})")
    except Exception as e:
        print(f"[NOTE] GitHub API returned: {e} (This is normal if unauthenticated rate limit is reached).")

if __name__ == "__main__":
    test_database()
    test_github_collector()
    print("\nAll Step 1 tests finished!")
