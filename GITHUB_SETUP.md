# GitHub Setup

Use this guide after unpacking the repository scaffold and before writing application code.

## 1. Create repository

Recommended repository name: `frameflow`

Recommended description:

> Self-hosted photo delivery for digital displays, with explainable rotation and provider reconciliation.

Recommended visibility: public, once you are ready for portfolio use.

Do not initialize GitHub with a README, license, or gitignore because this scaffold already includes them.

## 2. Push first commit

```bash
git init
git add .
git commit -m "chore: initialize FrameFlow repository"
git branch -M main
git remote add origin git@github.com:<owner>/frameflow.git
git push -u origin main
```

## 3. Configure repository settings

Recommended settings:

- Enable Issues
- Enable Discussions later, after first working release
- Enable Projects
- Enable Dependabot alerts
- Enable Dependabot security updates
- Require signed commits later, optional initially
- Disable Wikis because docs live in the repository

## 4. Branch protection

For `main`:

- Require pull request before merging
- Require status checks to pass
- Require branches to be up to date before merging
- Require conversation resolution
- Restrict force pushes
- Restrict deletions

## 5. Labels

Create labels from `docs/github/labels.md`.

## 6. Milestones

Create milestones from `docs/github/milestones.md`.

## 7. Project board

Create a GitHub Project using the recommendations in `docs/github/project-board.md`.

## 8. First issues

Create issues for Milestone 1 from `docs/github/initial-issues.md`.
