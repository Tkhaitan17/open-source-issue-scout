from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from app.sandbox.runner import SandboxRunner
from app.coach.investigator import InvestigationResult
from app.coach.patcher import PatchPlan, Patcher

class VerificationReport(BaseModel):
    repository: str
    patch_applied: bool
    tests_ran: bool
    tests_passed: bool
    test_output: str
    diff: str
    confidence_assessment: str

class Verifier:
    """
    Coordinates applying the proposed patch, running the test suite in the sandbox,
    and generating an honest verification report.
    """

    def __init__(self, sandbox: Optional[SandboxRunner] = None, patcher: Optional[Patcher] = None):
        self.sandbox = sandbox or SandboxRunner(default_timeout=60)
        self.patcher = patcher or Patcher()

    def verify(
        self,
        investigation: InvestigationResult,
        patch_plan: Optional[PatchPlan] = None,
        test_command: Optional[List[str]] = None
    ) -> VerificationReport:
        repo_dir = Path(investigation.repo_path)
        patch_applied = False
        diff_text = ""

        # 1. Apply patch if provided
        if patch_plan and patch_plan.diff_content:
            patch_applied = self.patcher.apply_patch(repo_dir, patch_plan.diff_content)
            diff_text = self.patcher.get_git_diff(repo_dir)

        # 2. Determine test command
        cmd = test_command
        if not cmd:
            import sys
            python_bin = sys.executable
            # Support both pytest and builtin unittest
            if investigation.test_files:
                test_file = investigation.test_files[0]
                cmd = [python_bin, "-m", "unittest", test_file]
            else:
                cmd = [python_bin, "-m", "unittest", "discover"]

        # 3. Run in sandbox
        result = self.sandbox.run(cmd=cmd, cwd=repo_dir, timeout=45)
        
        tests_passed = (result.exit_code == 0)
        output = (result.stdout + "\n" + result.stderr).strip()

        # 4. Honest confidence assessment
        if not patch_applied and patch_plan:
            assessment = "Patch could not be applied cleanly. Manual inspection required."
        elif tests_passed:
            assessment = "Fix verified! Relevant tests executed and passed without regressions."
        else:
            assessment = "Tests failed or tests could not be discovered. Do NOT claim the fix is verified."

        return VerificationReport(
            repository=investigation.repository,
            patch_applied=patch_applied,
            tests_ran=True,
            tests_passed=tests_passed,
            test_output=output[:1500],
            diff=diff_text or (patch_plan.diff_content if patch_plan else ""),
            confidence_assessment=assessment
        )
