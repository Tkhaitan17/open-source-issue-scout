import json
from typing import List, Optional, Dict, Any
from app.github.client import GitHubClient
from app.database.models import IssueItem

class IssueCollector:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def collect_candidates(
        self,
        repositories: Optional[List[str]] = None,
        language: str = "python",
        labels: Optional[List[str]] = None,
        max_results: int = 15
    ) -> List[IssueItem]:
        """
        Collect candidate issues from GitHub based on repositories or search criteria.
        Filters out pull requests and issues with assignees directly at retrieval.
        """
        query_parts = ["is:issue", "is:open", "no:assignee"]
        
        if repositories:
            repo_queries = [f"repo:{r}" for r in repositories]
            query_parts.append(f"({' OR '.join(repo_queries)})")
        elif language:
            query_parts.append(f"language:{language}")

        if labels:
            label_queries = [f'label:"{lbl}"' for lbl in labels]
            query_parts.append(f"({' OR '.join(label_queries)})")
        else:
            # Default to good-first-issue or help wanted
            query_parts.append('(label:"good first issue" OR label:"help wanted" OR label:"easy")')

        query = " ".join(query_parts)
        search_res = self.client.search_issues(query=query, per_page=max_results)
        
        items = search_res.get("items", [])
        collected: List[IssueItem] = []

        for item in items:
            # Skip if this is a PR disguised as an issue (GitHub search issues includes PRs unless is:issue is strict)
            if "pull_request" in item:
                continue

            # Skip if assigned
            if item.get("assignee") or item.get("assignees"):
                continue

            # Extract repository name from repository_url
            repo_url = item.get("repository_url", "")
            repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else "unknown"

            label_names = [lbl["name"] for lbl in item.get("labels", []) if "name" in lbl]

            issue = IssueItem(
                github_issue_id=item["id"],
                repository=repo_name,
                title=item["title"],
                url=item["html_url"],
                status="open",
                labels=label_names,
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at"),
                metadata=json.dumps({
                    "comments_count": item.get("comments", 0),
                    "body_snippet": (item.get("body") or "")[:500],
                    "author": item.get("user", {}).get("login", "")
                })
            )
            collected.append(issue)

        return collected
