from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# SQLite Schema DDL
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_username TEXT NOT NULL UNIQUE,
    languages TEXT NOT NULL,
    interests TEXT,
    preferred_issue_types TEXT,
    available_hours_per_week INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_issue_id INTEGER NOT NULL UNIQUE,
    repository TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    labels TEXT,
    created_at TEXT,
    updated_at TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    score REAL DEFAULT 0.0,
    reason TEXT,
    difficulty TEXT,
    estimated_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(issue_id) REFERENCES issues(id)
);

CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    user_decision TEXT, -- accepted, skipped
    patch_status TEXT,  -- generated, failed, none
    test_status TEXT,   -- passed, failed, not_run
    pr_url TEXT,
    pr_status TEXT,     -- open, merged, closed
    feedback TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(issue_id) REFERENCES issues(id)
);
"""

# Pydantic Schemas for App Validation
class UserProfile(BaseModel):
    id: Optional[int] = None
    github_username: str
    languages: List[str] = Field(default_factory=lambda: ["python"])
    interests: List[str] = Field(default_factory=list)
    preferred_issue_types: List[str] = Field(default_factory=lambda: ["good first issue", "bug"])
    available_hours_per_week: int = 5

class IssueItem(BaseModel):
    id: Optional[int] = None
    github_issue_id: int
    repository: str
    title: str
    url: str
    status: str = "open"
    labels: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[str] = "{}"
