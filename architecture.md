# Open Source Issue Scout + Fix Coach
## Implementation Plan and Proof of Concept

**Document status:** MVP implementation plan  
**Goal:** Build an agent that finds suitable open-source issues, helps investigate and test a possible fix, and supports the user in making a high-quality contribution.

---

## 1. Project overview

Open Source Issue Scout + Fix Coach helps a developer make meaningful open-source contributions without spending hours searching for issues or figuring out where to begin.

The system will:

1. Find potentially suitable GitHub issues.
2. Filter out issues that are closed, assigned, stale, or unsuitable.
3. Rank issues against the user’s skills and available time.
4. Explain why an issue is a good match.
5. Investigate a selected issue and suggest a fix.
6. Run checks in an isolated environment.
7. Show the proposed changes for the user to review.
8. Track the contribution and use outcomes to improve future recommendations.

**Core principle:** The agent assists with contributions; the user remains responsible for the fix and the PR. The MVP will not submit PRs automatically.

## 2. MVP scope

### Included

- GitHub issue discovery for selected repositories or languages.
- Profile-based issue filtering and ranking.
- A shortlist with issue links and explanations.
- Investigation of one selected issue.
- Relevant file discovery and a proposed fix plan.
- Test execution in a sandbox.
- A reviewable patch or diff.
- Manual PR submission by the user.
- Basic tracking of accepted, skipped, and contributed issues.

### Not included in the first version

- Automatically opening or merging PRs.
- Supporting every programming language and repository.
- Autonomous changes to the agent’s own code.
- Training or fine-tuning a model.
- Complex multi-agent orchestration.
- Fully automated daily email notifications.
- Guaranteed bug fixes or guaranteed PR acceptance.

---

## 3. Architecture

```text
User Profile
     |
     v
GitHub API --> Issue Collector
                    |
                    v
             Eligibility Filter
                    |
                    v
              Issue Ranker <--- LLM
                    |
                    v
              Issue Shortlist
                    |
                    v
                User Picks
                    |
                    v
              Fix Coach Agent
                    |
                    v
             Isolated Sandbox
                    |
                    v
          Proposed Fix + Test Results
                    |
                    v
              User Reviews
                    |
                    v
            User Submits PR
                    |
                    v
                 Tracker
                    |
                    v
              Local Database
                    |
                    +----> Feedback improves future ranking
```

### Main components

| Component | Responsibility |
|---|---|
| User profile | Stores languages, interests, repositories, and available time |
| GitHub API client | Retrieves issues, pull requests, labels, repo metadata, and contribution files |
| Issue collector | Finds candidate issues |
| Eligibility filter | Removes unsuitable or unavailable issues using clear rules |
| Issue ranker | Scores candidates against the user profile |
| LLM layer | Explains issue fit, summarizes context, and assists with code investigation |
| Fix Coach | Finds relevant files, suggests a plan, and proposes a patch |
| Sandbox | Runs repository tests and checks in an isolated environment |
| Tracker | Records user decisions and PR outcomes |
| Database | Stores profiles, issue metadata, scores, decisions, and contribution status |

---

## 4. Suggested technology stack

Use a simple stack that can be built and run locally.

| Area | Suggested choice | Why |
|---|---|---|
| Language | Python | Strong ecosystem for APIs, agents, and developer tools |
| API server | FastAPI | Simple backend and API endpoints |
| UI | Streamlit for the POC; React later if needed | Fast way to build a usable interface |
| GitHub access | GitHub REST API | Issue, PR, label, and repository data |
| LLM integration | Provider API wrapper with a local-model option | Lets the project switch between models |
| Embeddings | Optional; local embedding model later | Not necessary for the first version |
| Database | SQLite | Easy local setup and sufficient for an MVP |
| Git operations | Git CLI or GitPython | Clone repos, inspect branches, and prepare diffs |
| Test isolation | Docker | Runs project tests in a disposable environment |
| Scheduling | Manual “Run Scout” button initially | Avoids unnecessary infrastructure |
| Deployment | Local machine initially | Keeps the first version low-cost |

**Cost approach:** Aim for a $0 POC. Use GitHub’s API, SQLite, local execution, and a local model where practical. A hosted LLM API, cloud hosting, or heavier test workloads may introduce costs. Check current API and cloud pricing before depending on a paid service.

---

## 5. User profile

The user should be able to configure:

- GitHub username.
- Languages and frameworks they want to contribute in.
- Topics or project types they are interested in.
- Preferred issue types, such as bugs, tests, documentation, or good-first-issue tasks.
- Maximum issue difficulty.
- Time available per week.
- Repositories to include or exclude.

For the POC, store the profile in a local configuration file or SQLite. Do not require a complex account system.

---

## 6. Issue discovery and filtering

### Issue Collector

The collector should:

- Search selected repositories or GitHub issues by language, labels, and keywords.
- Retrieve issue title, body, labels, comments, creation date, update date, and repository metadata.
- Check whether an issue is open and whether it has an assignee.
- Check for linked or related pull requests where possible.
- Fetch `CONTRIBUTING.md` and other relevant repository contribution guidance.

### Eligibility Filter

Reject or flag issues when:

- The issue is closed.
- The issue is assigned or already has an active PR.
- The issue is too vague to investigate.
- The repository disallows the proposed type of contribution.
- The issue is outside the user’s selected languages or interests.
- The repository or issue appears inactive.
- The issue is a duplicate or already being addressed.

A rule-based filter should run before the LLM. The LLM should not be the only authority for whether an issue is available or suitable.

---

## 7. Ranking and shortlist

Use a transparent score rather than relying only on an LLM-generated number.

Possible scoring signals:

- Match with the user’s languages and interests.
- Issue labels and type.
- Estimated complexity.
- Whether the issue has a clear reproduction or test.
- Repository activity and contribution guidance.
- Whether the issue appears unclaimed.
- Estimated time required.

The first version can use weighted rules. The LLM can provide a short explanation and identify uncertainty.

### Shortlist output

Each result should show:

- Issue title and link.
- Repository name and language.
- Labels and current status.
- Match score.
- Estimated difficulty and time.
- Why it matches the user.
- Main uncertainty or risk.
- Recommended next step.

The shortlist should be small—around five candidates—so the user can choose one.

---

## 8. Fix Coach

After the user selects an issue, the Fix Coach should:

1. Read the issue, relevant discussion, and contribution guidance.
2. Clone the repository into a disposable working directory.
3. Inspect the project structure and identify relevant files.
4. Explain the likely cause in plain language.
5. Suggest a small, testable fix plan.
6. Identify existing tests and propose a regression test if appropriate.
7. Make a proposed patch in a separate branch or working copy.
8. Run relevant checks in the sandbox.
9. Show the diff, test results, and unresolved questions.

The agent must report honestly when it cannot reproduce the bug, understand the code, or run the tests. It should not claim a fix is verified when the evidence is incomplete.

---

## 9. Sandbox and security requirements

Repository code, issue text, and project instructions must be treated as untrusted input.

The sandbox should:

- Run tests in a disposable container or isolated environment.
- Avoid exposing personal files, credentials, or unrelated repositories.
- Use no secrets by default.
- Restrict network access where practical.
- Apply CPU, memory, and execution-time limits.
- Destroy the environment after the task or retain it only when the user explicitly asks.
- Require user approval before any action that writes to GitHub.

The agent must not follow instructions found inside repository content that attempt to override its permissions or safety rules.

---

## 10. Tracker and feedback loop

Store the following events:

- Issue recommended.
- User accepted or skipped it.
- Reason for skipping, if provided.
- Investigation started or completed.
- Tests passed or failed.
- User created a PR.
- PR status: open, merged, closed, or changes requested.

Use these signals to improve ranking and recommendations. For the MVP, this can be simple statistics and user preferences—not model training.

A merged PR is useful feedback, but it is not a perfect quality label. Maintainer availability, project priorities, and review time can affect the outcome.

---

## 11. Database design

Start with SQLite and these tables:

### `user_profile`
- `id`
- `github_username`
- `languages`
- `interests`
- `preferred_issue_types`
- `available_hours_per_week`

### `issues`
- `id`
- `github_issue_id`
- `repository`
- `title`
- `url`
- `status`
- `labels`
- `created_at`
- `updated_at`
- `metadata`

### `recommendations`
- `id`
- `issue_id`
- `score`
- `reason`
- `difficulty`
- `estimated_time`
- `created_at`

### `contributions`
- `id`
- `issue_id`
- `user_decision`
- `patch_status`
- `test_status`
- `pr_url`
- `pr_status`
- `feedback`

Store only the data needed for the product. Avoid storing repository contents or user secrets unnecessarily.

---

## 12. Proof of Concept (POC)

### POC objective

Demonstrate that the system can find a real issue that matches the user, explain why it is suitable, investigate it, and produce a testable proposed fix for review.

### POC limits

- One user profile.
- One or two programming languages.
- A small set of selected repositories.
- A handful of candidate issues per run.
- One issue investigated end-to-end.
- No automatic PR submission.
- Local execution and SQLite.

### POC workflow

1. Enter a GitHub username, languages, and interests.
2. Select a repository or run a limited issue search.
3. Fetch candidate issues from GitHub.
4. Apply eligibility rules.
5. Rank the remaining issues and show a shortlist.
6. Select one issue.
7. Clone the repository and inspect relevant files.
8. Produce a fix plan and a proposed patch.
9. Run the relevant tests in an isolated environment.
10. Display the diff and test results for the user to review.

### POC success criteria

The POC is successful when it can:

- Retrieve valid issue data from GitHub.
- Exclude closed and clearly unsuitable issues.
- Explain why a recommended issue matches the profile.
- Show the repository files and reasoning used during investigation.
- Produce a reviewable patch for at least one suitable issue.
- Run relevant tests and accurately report the results.
- Avoid submitting a PR without user approval.

The POC does not need to solve every issue. A clear, honest “unable to verify” result is better than a false claim that a fix works.

---

## 13. Implementation phases

### Phase 1 — Issue Scout
- Create the Python project.
- Connect to GitHub’s API.
- Build the profile and issue collector.
- Add rule-based filtering.
- Store data in SQLite.
- Show a ranked shortlist.

### Phase 2 — Fix Coach
- Clone a selected repository.
- Read contribution guidance.
- Find relevant files.
- Generate an investigation summary and fix plan.
- Produce a proposed patch.

### Phase 3 — Verification
- Add the sandbox.
- Run tests and checks.
- Capture logs and test results.
- Show the diff and verification status.

### Phase 4 — Tracker
- Record accept/skip decisions.
- Track PR URLs and statuses.
- Use outcomes to improve ranking.
- Add a contribution history page.

### Phase 5 — Improvements
- Support more languages and repositories.
- Add optional embeddings for issue and code retrieval.
- Add scheduled issue discovery.
- Consider draft PR creation only after explicit user approval and repo-policy checks.

---

## 14. Suggested project structure

```text
open-source-issue-scout/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── github/
│   │   ├── client.py
│   │   └── issue_collector.py
│   ├── scout/
│   │   ├── filters.py
│   │   └── ranker.py
│   ├── coach/
│   │   ├── investigator.py
│   │   ├── patcher.py
│   │   └── verifier.py
│   ├── sandbox/
│   │   └── runner.py
│   ├── tracker/
│   │   └── service.py
│   ├── database/
│   │   ├── models.py
│   │   └── repository.py
│   └── ui/
│       └── dashboard.py
├── tests/
├── data/
├── docs/
├── .env.example
├── requirements.txt
└── README.md
```

Keep API keys and tokens in environment variables, never in source code or committed files.

---

## 15. Key risks and mitigations

| Risk | Mitigation |
|---|---|
| Recommends issues that are already being fixed | Check issue status, assignees, linked PRs, and recent discussion |
| Suggests incorrect fixes | Require reproduction or tests where possible; show uncertainty |
| Produces broad or unnecessary changes | Keep patches small and show the diff |
| Executes unsafe repository code | Use an isolated sandbox with limited permissions |
| Creates unwanted PRs | Keep PR creation manual in the MVP |
| Learns from misleading outcomes | Use multiple feedback signals and allow user corrections |
| API rate limits or model costs | Cache results, limit searches, and support local models |

---

## 16. Final recommendation

Build the project in this order:

**Issue Scout → ranked shortlist → Fix Coach → sandbox verification → tracker.**

Do not begin with a fully autonomous coding agent. First prove that the system consistently finds a worthwhile issue and helps produce a small, tested, reviewable contribution. That is the core value of the project; automation can come later.

