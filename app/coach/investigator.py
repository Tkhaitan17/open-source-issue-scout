import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.database.models import IssueItem

class InvestigationResult(BaseModel):
    repository: str
    repo_path: str
    relevant_files: List[str]
    test_files: List[str]
    likely_cause: str
    contributing_notes: Optional[str] = None

class Investigator:
    """
    Inspects repository files, reads contribution guidelines,
    and identifies candidate files related to the issue.
    """

    def clone_repository(self, repository: str, target_dir: Path) -> Path:
        """Shallow-clones repository (depth 1) into target directory."""
        clone_url = f"https://github.com/{repository}.git"
        dest = target_dir / repository.split("/")[-1]
        if not dest.exists():
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(dest)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
                timeout=60
            )
        return dest

    def find_relevant_files(self, repo_dir: Path, keywords: List[str], max_files: int = 5) -> List[str]:
        """Locates python files containing or named after issue keywords."""
        matched: List[str] = []
        clean_keywords = [k.lower().strip() for k in keywords if len(k.strip()) > 3]

        for p in repo_dir.rglob("*.py"):
            # Skip hidden dirs, virtualenvs, or caches
            p_str = str(p.relative_to(repo_dir))
            if any(part.startswith(".") or part in ("venv", ".venv", "__pycache__", "build", "dist") for part in p.parts):
                continue

            name_lower = p.name.lower()
            if any(k in name_lower for k in clean_keywords):
                matched.append(p_str)
                if len(matched) >= max_files:
                    break

        return matched

    def find_test_files(self, repo_dir: Path, max_tests: int = 5) -> List[str]:
        """Finds existing test files."""
        tests: List[str] = []
        for p in repo_dir.rglob("test_*.py"):
            p_str = str(p.relative_to(repo_dir))
            if not any(part.startswith(".") for part in p.parts):
                tests.append(p_str)
                if len(tests) >= max_tests:
                    break
        return tests

    def read_contributing_guide(self, repo_dir: Path) -> Optional[str]:
        """Reads contributing guideline file if present."""
        for name in ("CONTRIBUTING.md", "contributing.md", "docs/contributing.rst"):
            guide = repo_dir / name
            if guide.is_file():
                try:
                    return guide.read_text(encoding="utf-8", errors="ignore")[:1000]
                except Exception:
                    pass
        return None

    def investigate(self, issue: IssueItem, repo_dir: Path) -> InvestigationResult:
        # Extract keywords from title
        words = [w for w in issue.title.replace("_", " ").replace("-", " ").split() if len(w) > 3]
        relevant_files = self.find_relevant_files(repo_dir, words)
        test_files = self.find_test_files(repo_dir)
        contributing = self.read_contributing_guide(repo_dir)

        likely_cause = f"Issue '{issue.title}' suggests an unhandled edge case or logic error in related module."
        if relevant_files:
            likely_cause += f" Primary candidate files for review: {', '.join(relevant_files)}."

        return InvestigationResult(
            repository=issue.repository,
            repo_path=str(repo_dir),
            relevant_files=relevant_files,
            test_files=test_files,
            likely_cause=likely_cause,
            contributing_notes=contributing
        )
