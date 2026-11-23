from typing import List, Dict, Any, Optional
from app.database.repository import Repository

class TrackerService:
    def __init__(self, repo: Optional[Repository] = None):
        self.repo = repo or Repository()

    def record_decision(
        self,
        issue_id: int,
        decision: str, # "accepted" or "skipped"
        feedback: Optional[str] = None,
        patch_status: str = "none",
        test_status: str = "not_run"
    ) -> int:
        return self.repo.record_contribution(
            issue_id=issue_id,
            user_decision=decision,
            patch_status=patch_status,
            test_status=test_status,
            feedback=feedback
        )

    def record_pr_submission(self, issue_id: int, pr_url: str, pr_status: str = "open") -> None:
        self.repo.update_pr_status(issue_id=issue_id, pr_url=pr_url, pr_status=pr_status)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.repo.get_contributions()

    def get_stats(self) -> Dict[str, Any]:
        contributions = self.repo.get_contributions()
        total = len(contributions)
        accepted = sum(1 for c in contributions if c.get("user_decision") == "accepted")
        skipped = sum(1 for c in contributions if c.get("user_decision") == "skipped")
        prs_created = sum(1 for c in contributions if c.get("pr_url"))
        prs_merged = sum(1 for c in contributions if c.get("pr_status") == "merged")

        return {
            "total_reviewed": total,
            "accepted": accepted,
            "skipped": skipped,
            "prs_created": prs_created,
            "prs_merged": prs_merged,
            "acceptance_rate": round((accepted / total * 100), 1) if total > 0 else 0.0
        }
