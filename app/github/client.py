import requests
from typing import Dict, Any, List, Optional
from app.config import GITHUB_TOKEN

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "open-source-issue-scout"
        })
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

    def search_issues(self, query: str, sort: str = "updated", order: str = "desc", per_page: int = 20) -> Dict[str, Any]:
        """Search issues across GitHub repositories."""
        url = f"{self.BASE_URL}/search/issues"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        }
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Fetch full details for an issue."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository details."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_contributing_guide(self, owner: str, repo: str) -> Optional[str]:
        """Attempt to fetch CONTRIBUTING.md content."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/CONTRIBUTING.md"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("download_url")
        return None

    def check_linked_prs(self, owner: str, repo: str, issue_number: int) -> bool:
        """
        Check if an issue already has active pull requests.
        GitHub Timeline API provides connected PR events.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/timeline"
        headers = self.session.headers.copy()
        headers["Accept"] = "application/vnd.github.mockingbird-preview+json"
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                events = resp.json()
                for event in events:
                    if event.get("event") == "cross-referenced" and "source" in event:
                        issue_info = event["source"].get("issue", {})
                        if "pull_request" in issue_info and issue_info.get("state") == "open":
                            return True
        except Exception:
            pass
        return False
