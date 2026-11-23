"""
Verification test for Step 3: Fix Coach and Isolated Sandbox
"""
import sys
import tempfile
import subprocess
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.sandbox.runner import SandboxRunner
from app.coach.investigator import Investigator, InvestigationResult
from app.coach.patcher import Patcher, PatchPlan
from app.coach.verifier import Verifier
from app.database.models import IssueItem

def test_sandbox_security():
    print("--> Testing Sandbox Isolation & Secret Scrubbing...")
    # Inject a dummy sensitive token into current environment
    os.environ["GITHUB_TOKEN"] = "sensitive_super_secret_token"
    
    runner = SandboxRunner(default_timeout=5)
    # Command prints out GITHUB_TOKEN if it exists
    with tempfile.TemporaryDirectory() as tmpdir:
        res = runner.run(["python", "-c", "import os; print('TOKEN_FOUND:' + os.getenv('GITHUB_TOKEN', 'NONE'))"], cwd=Path(tmpdir))
        assert "TOKEN_FOUND:NONE" in res.stdout, f"Sandbox failed to scrub secret! Got: {res.stdout}"
        print("[PASS] Sensitive tokens successfully scrubbed from sandbox environment.")

def test_coach_end_to_end():
    print("\n--> Testing Fix Coach (Investigate -> Patch -> Verify)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "sample_repo"
        repo_dir.mkdir()
        
        # Initialize a real git repo
        subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo_dir), check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo_dir), check=True)

        # Create sample files
        calculator_py = repo_dir / "calculator.py"
        calculator_py.write_text("def add(a, b):\n    return a - b  # BUG: minus instead of plus\n")
        
        test_py = repo_dir / "test_calculator.py"
        test_py.write_text("import unittest\nfrom calculator import add\n\nclass TestCalc(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n")

        subprocess.run(["git", "add", "."], cwd=str(repo_dir), check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(repo_dir), check=True, stdout=subprocess.DEVNULL)

        # 1. Investigate
        issue = IssueItem(
            github_issue_id=42,
            repository="sample/calculator",
            title="Calculator add function returns incorrect sum",
            url="https://github.com/sample/calculator/issues/42"
        )
        investigator = Investigator()
        inv_res = investigator.investigate(issue, repo_dir)
        assert "calculator.py" in inv_res.relevant_files
        assert "test_calculator.py" in inv_res.test_files
        print(f"[PASS] Investigator detected candidate files: {inv_res.relevant_files} and tests: {inv_res.test_files}")

        # 2. Patch & Verify
        # Patch fixing the bug
        patch_diff = """--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b  # BUG: minus instead of plus
+    return a + b
"""
        plan = PatchPlan(
            summary="Fix subtraction bug in add function",
            steps=["Change minus to plus in calculator.py"],
            diff_content=patch_diff
        )

        # Verification using pytest in virtual environment or python unittest
        python_exe = sys.executable
        test_cmd = [python_exe, "-m", "unittest", "test_calculator.py"]
        
        # Test runs with unittest
        verifier = Verifier()
        report = verifier.verify(inv_res, patch_plan=plan, test_command=test_cmd)
        
        assert report.patch_applied is True, "Patch application failed"
        assert report.tests_passed is True, f"Tests failed! Output: {report.test_output}"
        assert "Fix verified!" in report.confidence_assessment
        print("[PASS] Patch applied cleanly and tests passed successfully!")
        print(f"       Assessment: {report.confidence_assessment}")
        print(f"       Diff Preview:\n{report.diff}")

if __name__ == "__main__":
    test_sandbox_security()
    test_coach_end_to_end()
    print("\nAll Step 3 tests passed successfully!")
