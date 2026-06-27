---
name: github
description: "Complete GitHub operations — auth, issues, PRs, code review, repo management, releases, Actions, and secrets. One-stop skill for all GitHub workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Issues, Code-Review, Actions, Repositories, CI/CD]
    related_skills: [systematic-debugging, writing-plans]
---

# GitHub Workflows

Complete class-level skill for all GitHub operations. This umbrella covers **authentication**, **issues**, **pull requests**, **code review**, **repo management**, **releases**, **GitHub Actions**, and **secrets** — all with shared auth detection and consistent `gh`-first, `curl`-fallback patterns.

## Structure

| Section | File | Purpose |
|---------|------|---------|
| Auth & Setup | (embedded below) | Shared auth detection once, not duplicated |
| Issues | `references/issues.md` | Create, triage, label, assign, search issues |
| PR Workflow | `references/pr-workflow.md` | Branch, commit, open, CI monitor, merge |
| Code Review | `references/code-review.md` | Local and PR review, inline comments, formal reviews |
| Repo Management | `references/repo-management.md` | Clone, create, fork, settings, releases, secrets, Actions |
| Actions & Workflows | `references/repo-management.md` | CI monitoring, workflow dispatch, secrets |
| API Cheatsheet | `references/github-api-cheatsheet.md` | Quick curl REST API reference |

## Prerequisites

- Authenticated with GitHub
- Inside a git repo (for repo-specific operations)

### Shared Auth Detection (Used By All Subsections)

```bash
# Determine auth method
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    elif git credential-manager version &>/dev/null; then
      GITHUB_TOKEN=$(echo "protocol=https
host=github.com" | git credential-manager get 2>/dev/null | grep "^password=" | sed 's/^password=//')
    fi
  fi
fi
echo "Auth method: $AUTH"
```

### Extract Owner/Repo from Remote

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

## Quick Reference Table

| Action | `gh` command | curl endpoint |
|--------|-------------|--------------|
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| View issue | `gh issue view N` | `GET /repos/{o}/{r}/issues/N` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| List PRs | `gh pr list --author @me` | `GET /repos/{o}/{r}/pulls` |
| View PR diff | `gh pr diff` | `GET /repos/{o}/{r}/pulls/N` |
| Create PR | `gh pr create ...` | `POST /repos/{o}/{r}/pulls` |
| Merge PR | `gh pr merge --squash` | `PUT /repos/{o}/{r}/pulls/N/merge` |
| CI status | `gh pr checks` | `GET /repos/{o}/{r}/commits/{sha}/status` |
| Re-run CI | `gh run rerun ID` | `POST /repos/{o}/{r}/actions/runs/ID/rerun` |
| Clone repo | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `POST /repos/o/r/forks` + clone |
| Edit repo settings | `gh repo edit --...` | `PATCH /repos/o/r` |
| Create release | `gh release create v1.0` | `POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `GET /repos/o/r/actions/workflows` |
| Set secret | `gh secret set KEY` | `PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |
| Gists | `gh gist create file.py --public` | `POST /gists` |

## Which Tool to Load

- **Authentication issues** → `references/auth-setup.md` (HTTPS tokens, SSH, gh CLI, credential helpers)
- **Reviewing changes** → `references/code-review.md` (pre-push review, PR review checklist, inline comments)
- **Issues & triage** → `references/issues.md` (create, label, assign, close, templates)
- **PR lifecycle** → `references/pr-workflow.md` (branch, commit, push, create PR, CI, merge)
- **Repo admin** → `references/repo-management.md` (clone, create, fork, settings, secrets, releases, Actions, gists)
