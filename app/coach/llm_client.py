"""
LLM Client Wrapper — Phase 2 of POC
Uses Groq (qwen/qwen3.8-27b) to generate real unified diff patches for the Fix Coach.

Pattern:
    from app.coach.llm_client import LLMClient
    client = LLMClient()
    diff = client.generate_fix(issue_title, issue_body, file_path, file_content)
"""

import os
from typing import Optional

GROQ_MODEL = "qwen/qwen3.8-27b"

FIX_SYSTEM_PROMPT = """\
You are an expert open-source contributor and code-review assistant.
Given a GitHub issue description and a source file, produce a minimal,
correct unified-diff patch that fixes the described problem.

Rules:
- Output ONLY the unified diff (starting with --- a/<file> and +++ b/<file>).
- Do NOT include markdown fences, explanations, or any other text.
- Keep the change as small as possible.
- If you cannot determine the fix with confidence, output an empty string.
"""

FIX_USER_TEMPLATE = """\
=== GitHub Issue ===
Title: {title}
Body:
{body}

=== Source File: {filepath} ===
{content}

Generate a unified diff patch to fix this issue. Output only the diff.
"""


class LLMClient:
    """Calls Groq API to generate unified diff patches."""

    def __init__(self, api_key: Optional[str] = None, model: str = GROQ_MODEL):
        # Load key from env if not passed explicitly
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("groq package not installed. Run: pip install groq")
        return self._client

    def is_available(self) -> bool:
        """Returns True if a usable API key is configured."""
        return bool(self.api_key and self.api_key not in ("", "YOUR_GROQ_API_KEY_HERE"))

    def generate_fix(
        self,
        issue_title: str,
        issue_body: str,
        file_path: str,
        file_content: str,
        max_tokens: int = 800,
    ) -> str:
        """
        Calls the LLM to generate a unified diff patch.

        Returns the diff string, or an empty string if the LLM cannot help.
        Raises RuntimeError on API errors.
        """
        if not self.is_available():
            return ""

        prompt = FIX_USER_TEMPLATE.format(
            title=issue_title,
            body=(issue_body or "No additional details provided.")[:1500],
            filepath=file_path,
            content=file_content[:3000],  # cap to avoid token overflows
        )

        client = self._get_client()
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": FIX_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        result = completion.choices[0].message.content.strip()

        # Only return if it looks like a real diff
        if result.startswith("---") or result.startswith("@@"):
            return result
        # Sometimes the model wraps in backticks — strip them
        if "```" in result:
            lines = result.split("\n")
            inner = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(inner).strip()
            if cleaned.startswith("---") or cleaned.startswith("@@"):
                return cleaned
        return result  # return whatever we got; verifier will evaluate

    def summarise_issue(self, issue_title: str, issue_body: str) -> str:
        """Generates a brief plain-English summary of what the issue is about."""
        if not self.is_available():
            return issue_title

        client = self._get_client()
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Summarise the following GitHub issue in 2-3 sentences. Be concise and technical.",
                },
                {
                    "role": "user",
                    "content": f"Title: {issue_title}\n\n{(issue_body or '')[:1000]}",
                },
            ],
            max_tokens=150,
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
