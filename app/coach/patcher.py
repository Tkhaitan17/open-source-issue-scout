import subprocess
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

class PatchPlan(BaseModel):
    summary: str
    steps: List[str]
    diff_content: str

class Patcher:
    """
    Applies unified diff patches and generates clean git diffs for user review.
    """

    def apply_patch(self, repo_dir: Path, diff_content: str) -> bool:
        """Applies a patch using git apply."""
        try:
            proc = subprocess.run(
                ["git", "apply", "--ignore-whitespace", "-"],
                input=diff_content,
                cwd=str(repo_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_git_diff(self, repo_dir: Path) -> str:
        """Returns the current git diff of the repository."""
        proc = subprocess.run(
            ["git", "diff"],
            cwd=str(repo_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc.stdout or ""
