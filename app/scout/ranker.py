import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.database.models import IssueItem, UserProfile

class ScoredIssue(BaseModel):
    issue: IssueItem
    score: float
    difficulty: str
    estimated_time: str
    match_reason: str
    risk_or_uncertainty: str
    recommended_next_step: str

class IssueRanker:
    """
    Ranks eligible issues using transparent scoring signals:
    - Match with user profile's languages & interests
    - Beginner-friendly labels
    - Clarity and reproducibility cues
    """

    def score_issue(self, issue: IssueItem, profile: UserProfile) -> ScoredIssue:
        score = 50.0  # Base score
        match_reasons: List[str] = []
        risks: List[str] = []

        labels_lower = [lbl.lower() for lbl in issue.labels]
        title_lower = issue.title.lower()
        
        meta: Dict[str, Any] = {}
        if issue.metadata:
            try:
                meta = json.loads(issue.metadata)
            except Exception:
                pass

        body = meta.get("body_snippet", "").lower()
        comments_count = meta.get("comments_count", 0)

        # 1. Beginner friendly label bonus (+20)
        beginner_tags = {"good first issue", "easy", "beginner", "help wanted", "starter"}
        matched_beginner_tags = [t for t in beginner_tags if any(t in lbl for lbl in labels_lower)]
        if matched_beginner_tags:
            score += 20.0
            match_reasons.append(f"Marked with friendly labels ({', '.join(matched_beginner_tags)})")

        # 2. Preferred issue types bonus (+15)
        matched_pref_types = []
        for pref in profile.preferred_issue_types:
            if any(pref.lower() in lbl for lbl in labels_lower) or pref.lower() in title_lower:
                matched_pref_types.append(pref)
        if matched_pref_types:
            score += 15.0
            match_reasons.append(f"Matches preferred type: {', '.join(matched_pref_types)}")

        # 3. User interests bonus (+15)
        matched_interests = []
        for interest in profile.interests:
            intr = interest.lower()
            if intr in title_lower or intr in body or any(intr in lbl for lbl in labels_lower):
                matched_interests.append(interest)
        if matched_interests:
            score += 15.0
            match_reasons.append(f"Aligns with your interests: {', '.join(matched_interests)}")

        # 4. Clarity & Repro signals (+10)
        if "```" in body or "reproduce" in body or "expected" in body:
            score += 10.0
            match_reasons.append("Contains clear reproduction details or code snippets")

        # 5. Comment clutter penalty (-10)
        if comments_count > 15:
            score -= 10.0
            risks.append("High comment count; multiple people may already be debating a fix")
        elif comments_count == 0:
            match_reasons.append("Unclaimed with zero prior discussions")

        # Determine difficulty
        if any("good first issue" in lbl or "easy" in lbl for lbl in labels_lower):
            difficulty = "Beginner"
            estimated_time = "1-2 hours"
        elif any("documentation" in lbl or "docs" in lbl for lbl in labels_lower):
            difficulty = "Beginner"
            estimated_time = "1 hour"
        elif any("enhancement" in lbl or "feature" in lbl for lbl in labels_lower):
            difficulty = "Intermediate"
            estimated_time = "3-5 hours"
        else:
            difficulty = "Intermediate"
            estimated_time = "2-4 hours"

        # Default fallback messages
        reason_str = "; ".join(match_reasons) if match_reasons else "General open issue fitting language preferences."
        risk_str = "; ".join(risks) if risks else "Standard contribution risks apply (maintainer response time)."
        next_step = f"Inspect repository {issue.repository} and run Fix Coach to verify reproducibility."

        return ScoredIssue(
            issue=issue,
            score=min(100.0, max(0.0, round(score, 1))),
            difficulty=difficulty,
            estimated_time=estimated_time,
            match_reason=reason_str,
            risk_or_uncertainty=risk_str,
            recommended_next_step=next_step
        )

    def rank(self, issues: List[IssueItem], profile: UserProfile, top_n: int = 5) -> List[ScoredIssue]:
        """Ranks eligible issues and returns top N candidates."""
        scored = [self.score_issue(issue, profile) for issue in issues]
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_n]
