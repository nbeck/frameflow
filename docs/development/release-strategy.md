# Release Strategy

FrameFlow uses small, deliberate releases. Each release must be manually verified before the tag is pushed. There is no automated publishing pipeline for v1.

---

## Versioning policy

FrameFlow follows [Semantic Versioning](https://semver.org):

- **MAJOR** — incompatible API changes
- **MINOR** — backward-compatible new functionality
- **PATCH** — backward-compatible bug fixes

Before v1.0.0, minor versions may include breaking changes when documented in the changelog.

After v1.0.0, breaking changes require a major version bump.

---

## Where versions are defined

The project version is maintained in **two files** that must always match:

| File | Field |
|---|---|
| `pyproject.toml` | `version = "..."` (line 7) |
| `src/frameflow/__init__.py` | `__version__ = "..."` (line 4) |

There is no automated sync between these files. Both must be updated together in the release PR and verified before tagging.

---

## Changelog process

The changelog lives at `CHANGELOG.md` in the repo root and follows the [Keep a Changelog](https://keepachangelog.com) format.

**During development:** all notable changes are added under `[Unreleased]` as they land.

**At release time:**

1. Rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`.
2. Add a new empty `[Unreleased]` section above the versioned section.
3. Include the versioned section body verbatim in the GitHub release notes.

The `[Unreleased]` section should always be present so contributors know where to add entries.

---

## Release process

### Pre-release checklist

Before opening the release PR:

- [ ] CI is green on `main` (all jobs: Ruff, Black, MyPy, Pytest on Python 3.12 and 3.13, Docker build)
- [ ] `just check` passes locally
- [ ] All milestone issues are closed
- [ ] Operations runbook (`docs/operations.md`) reflects current behavior
- [ ] No open known regressions

### Release PR

The release PR is the only commit that bumps the version. It should contain exactly:

1. `pyproject.toml` — bump `version`
2. `src/frameflow/__init__.py` — bump `__version__` to match
3. `pyproject.toml` — update `Development Status` classifier if appropriate
4. `CHANGELOG.md` — move `[Unreleased]` content into `[X.Y.Z] - YYYY-MM-DD`, add new empty `[Unreleased]`

No feature changes, bug fixes, or refactors should be included in the release PR. If something needs to change, merge it first, then open the release PR.

**Title format:** `Release vX.Y.Z`

Wait for CI to pass on the release PR before merging. Squash merge.

### Tagging

After the release PR is merged and `main` is up to date locally:

```bash
git pull
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Use an **annotated tag** (not a lightweight tag). Annotated tags carry the tagger identity, timestamp, and message — they are the canonical release markers.

Pushing the tag triggers the Docker workflow automatically (`.github/workflows/docker.yml` is configured to respond to `v*` tags).

**Tags are immutable by convention.** Never delete, force-move, or re-push a published tag.

### GitHub release notes

1. Go to the repository on GitHub → Releases → Draft a new release.
2. Select the `vX.Y.Z` tag.
3. Set the release title to `vX.Y.Z`.
4. Paste the `[X.Y.Z]` section from `CHANGELOG.md` as the release body.
5. Mark as latest release.
6. Publish.

### Docker build verification

The Docker workflow (`.github/workflows/docker.yml`) runs on every `v*` tag push and verifies the image builds successfully. The current configuration does **not** push to a registry (`push: false`). Check the workflow run on the tag to confirm the build passed before announcing the release.

When a container registry is configured in the future, the push step will be enabled and the workflow will handle image publishing automatically. The tag trigger is already wired.

---

## Post-release verification

After the tag is pushed and the GitHub release is published:

1. Confirm CI checks on the tagged commit are green (GitHub → Actions, filter by tag).
2. Pull the repo fresh: `git pull && git fetch --tags`
3. Run `just check` on the tagged commit.
4. Start the server with production settings and verify:
   - `GET /health` returns `{"status": "ok"}`
   - `GET /status` returns correct library path and photo count
   - `POST /sync` completes without error
   - `GET /photos/next?client_id=test` returns a photo file

---

## Rollback guidance

FrameFlow does not have a rollback mechanism — it has a **forward fix** process.

**Do not** delete or move published tags. Tags are the permanent record of what was released.

If a critical bug is found after a release:

1. Fix the bug on a branch off `main`.
2. Merge the fix to `main` via the normal PR process.
3. Cut a patch release by incrementing the patch version, for example `v1.0.1` after `v1.0.0`, following this process from the beginning.

**Operational rollback** (redeploying the previous version):

1. Stop the running service.
2. Restore the database from the backup taken immediately before the upgrade. The database is the only stateful artifact — original photo files are unchanged.
3. Start the previous version of the service.

Database backups should always be taken before upgrading. See `docs/operations/backup-restore.md` for backup procedures.

---

## Development status classifier

The `pyproject.toml` classifiers include a Development Status that should be updated as the project matures:

| Status | Classifier | When |
|---|---|---|
| Pre-Alpha | `2 - Pre-Alpha` | Repository scaffold, pre-v1 work in progress |
| Alpha | `3 - Alpha` | First public release (v1.0.0), functional but may have rough edges |
| Beta | `4 - Beta` | Feature-complete, stabilizing for production |
| Stable | `5 - Production/Stable` | Mature, production-recommended |

The classifier update belongs in the release PR alongside the version bump.

---

## Future automation opportunities

The following are **not** implemented for v1 and should only be added when the operational need is clear:

- **Docker registry push** — enable `push: true` in `docker.yml` and configure `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` secrets once a target registry is chosen.
- **PyPI publishing** — add a `publish` job to a release workflow triggered on `v*` tags if distribution via `pip install` becomes a goal.
- **Automated changelog** — tools like `towncrier` or `git-cliff` can generate changelogs from conventional commits. Adopt only if manual changelog maintenance becomes a friction point.
- **Semantic release** — automated version bumping from commit messages. Adds process overhead; only worth it if release cadence is high enough to justify it.

The manual process described here is the correct choice for v1.
