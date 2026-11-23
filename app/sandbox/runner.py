import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel

class SandboxResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False

class SandboxRunner:
    """
    Executes commands in an isolated directory with clean environment variables.
    Treats repository scripts and tests as untrusted input.
    """
    
    # Sensitive environment variables to strip from execution
    BLOCKED_ENV_PREFIXES = ("GITHUB_", "TOKEN", "SECRET", "KEY", "AWS_", "SSH_", "PASSWORD")

    def __init__(self, default_timeout: int = 60):
        self.default_timeout = default_timeout

    def _sanitize_environment(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Provides a safe, minimal environment without user tokens or credentials."""
        safe_env = {}
        for k, v in os.environ.items():
            k_upper = k.upper()
            if not any(k_upper.startswith(prefix) or prefix in k_upper for prefix in self.BLOCKED_ENV_PREFIXES):
                safe_env[k] = v

        # Default standard path
        safe_env["PYTHONDONTWRITEBYTECODE"] = "1"
        safe_env["PYTHONUNBUFFERED"] = "1"
        if custom_env:
            safe_env.update(custom_env)
        return safe_env

    def run(self, cmd: List[str], cwd: Path, timeout: Optional[int] = None) -> SandboxResult:
        timeout = timeout or self.default_timeout
        env = self._sanitize_environment()
        start = time.time()

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=timeout,
                errors="replace"
            )
            duration = round(time.time() - start, 2)
            return SandboxResult(
                exit_code=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                duration_seconds=duration,
                timed_out=False
            )
        except subprocess.TimeoutExpired as exc:
            duration = round(time.time() - start, 2)
            return SandboxResult(
                exit_code=-1,
                stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
                stderr=f"Command timed out after {timeout} seconds",
                duration_seconds=duration,
                timed_out=True
            )
        except Exception as exc:
            duration = round(time.time() - start, 2)
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=f"Sandbox execution error: {str(exc)}",
                duration_seconds=duration,
                timed_out=False
            )
