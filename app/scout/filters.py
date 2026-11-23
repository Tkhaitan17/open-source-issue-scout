import json
from typing import List, Tuple, Dict, Any, Optional
from app.database.models import IssueItem, UserProfile

DISQUALIFYING_LABELS = {
    "duplicate", "invalid", "wontfix", "won't fix", 
    "blocked", "stale", "needs reproduction", "in progress", "assigned"
}

class EligibilityFilter:
    def __init__(self, min_description_length: int = 30):
        self.min_description_length = min_description_length

    def is_eligible(self, issue: IssueItem, profile: Optional[UserProfile] = None) -> Tuple[bool, str]:
        """
        Determines if an issue is eligible for investigation.
        Returns (is_eligible, reason_if_ineligible).
        """
        # 1. Status check
        if issue.status.lower() != "open":
            return False, "Issue is not open."

        # 2. Parse metadata
        meta: Dict[str, Any] = {}
        if issue.metadata:
            try:
                meta = json.loads(issue.metadata)
            except Exception:
                pass

        # 3. Label inspection
        lower_labels = {lbl.lower() for lbl in issue.labels}
        for disq in DISQUALIFYING_LABELS:
            if disq in lower_labels:
                return False, f"Flagged with disqualifying label '{disq}'."

        # 4. Description depth check
        snippet = meta.get("body_snippet", "")
        if len(snippet.strip()) < self.min_description_length:
            return False, "Issue description is too vague or empty to investigate."

        # 5. Check user-defined exclusions if profile provided
        if profile:
            # Check excluded repos or languages if applicable
            pass

        return True, "Eligible"

    def filter_candidates(self, issues: List[IssueItem], profile: Optional[UserProfile] = None) -> List[IssueItem]:
        """Filters a list of issues and returns only eligible ones."""
        eligible = []
        for issue in issues:
            ok, _ = self.is_eligible(issue, profile)
            if ok:
                eligible.append(issue)
        return eligible
