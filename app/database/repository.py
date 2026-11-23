import sqlite3
import json
from typing import Optional, List, Dict, Any
from app.config import DATABASE_PATH
from app.database.models import CREATE_TABLES_SQL, UserProfile, IssueItem

class Repository:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._shared_conn = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._shared_conn:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)

    # User Profile Operations
    def save_profile(self, profile: UserProfile) -> int:
        query = """
        INSERT INTO user_profile (github_username, languages, interests, preferred_issue_types, available_hours_per_week)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(github_username) DO UPDATE SET
            languages = excluded.languages,
            interests = excluded.interests,
            preferred_issue_types = excluded.preferred_issue_types,
            available_hours_per_week = excluded.available_hours_per_week;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                profile.github_username,
                json.dumps(profile.languages),
                json.dumps(profile.interests),
                json.dumps(profile.preferred_issue_types),
                profile.available_hours_per_week
            ))
            return cursor.lastrowid or 0

    def get_profile(self, username: str) -> Optional[UserProfile]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profile WHERE github_username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return None
            return UserProfile(
                id=row["id"],
                github_username=row["github_username"],
                languages=json.loads(row["languages"]) if row["languages"] else [],
                interests=json.loads(row["interests"]) if row["interests"] else [],
                preferred_issue_types=json.loads(row["preferred_issue_types"]) if row["preferred_issue_types"] else [],
                available_hours_per_week=row["available_hours_per_week"]
            )

    # Issue Operations
    def save_issues(self, issues: List[IssueItem]) -> int:
        query = """
        INSERT INTO issues (github_issue_id, repository, title, url, status, labels, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(github_issue_id) DO UPDATE SET
            title = excluded.title,
            status = excluded.status,
            labels = excluded.labels,
            updated_at = excluded.updated_at,
            metadata = excluded.metadata;
        """
        saved_count = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for issue in issues:
                cursor.execute(query, (
                    issue.github_issue_id,
                    issue.repository,
                    issue.title,
                    issue.url,
                    issue.status,
                    json.dumps(issue.labels),
                    issue.created_at,
                    issue.updated_at,
                    issue.metadata
                ))
                saved_count += 1
        return saved_count

    def get_open_issues(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM issues WHERE status = 'open' ORDER BY updated_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # Recommendation Operations
    def save_recommendation(self, issue_id: int, score: float, reason: str, difficulty: str, estimated_time: str) -> int:
        query = """
        INSERT INTO recommendations (issue_id, score, reason, difficulty, estimated_time)
        VALUES (?, ?, ?, ?, ?);
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (issue_id, score, reason, difficulty, estimated_time))
            return cursor.lastrowid or 0

    def get_top_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        query = """
        SELECT r.*, i.title, i.repository, i.url, i.labels
        FROM recommendations r
        JOIN issues i ON r.issue_id = i.id
        ORDER BY r.score DESC, r.created_at DESC
        LIMIT ?;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # Contribution Tracker Operations
    def record_contribution(
        self,
        issue_id: int,
        user_decision: str,
        patch_status: str = "none",
        test_status: str = "not_run",
        pr_url: Optional[str] = None,
        pr_status: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> int:
        query = """
        INSERT INTO contributions (issue_id, user_decision, patch_status, test_status, pr_url, pr_status, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (issue_id, user_decision, patch_status, test_status, pr_url, pr_status, feedback))
            return cursor.lastrowid or 0

    def update_pr_status(self, issue_id: int, pr_url: str, pr_status: str) -> None:
        query = """
        UPDATE contributions
        SET pr_url = ?, pr_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE issue_id = ?;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (pr_url, pr_status, issue_id))

    def get_contributions(self, limit: int = 50) -> List[Dict[str, Any]]:
        query = """
        SELECT c.*, i.title, i.repository, i.url as issue_url
        FROM contributions c
        LEFT JOIN issues i ON c.issue_id = i.id
        ORDER BY c.updated_at DESC
        LIMIT ?;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
