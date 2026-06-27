# AI Implementation Guide

FrameFlow is intentionally structured so implementation can proceed with Claude Code, OpenClaw, Codex-style tools, or similar AI coding assistants.

## Working pattern

Use one milestone at a time. Do not ask an AI coding tool to implement the entire product in one pass.

Recommended prompt structure:

1. State the current milestone.
2. Link or paste the relevant docs.
3. Define files that may be modified.
4. Define files that must not be modified.
5. Require tests.
6. Require documentation updates.
7. Require a summary of changes.

## Guardrails

- Do not implement future milestones early.
- Do not bypass ADRs without creating a new ADR.
- Do not add provider-specific assumptions to core modules.
- Do not put file system path logic outside the storage layer.
- Do not introduce network access in tests unless explicitly marked integration or contract.
- Do not commit personal photos or provider credentials.

## Milestone 1 starter prompt

```text
You are implementing FrameFlow Milestone 1: Core Domain and Storage.
Read docs/architecture/data-model.md, docs/architecture/storage.md, docs/architecture/photo-lifecycle.md, and docs/roadmap/milestone-1-core-domain-storage.md.
Implement only the domain model, database schema foundation, Alembic migration, and storage path planning needed for Milestone 1.
Do not implement provider sync, rotation, or DAKboard delivery yet.
Add tests and keep CI passing.
```

## Review checklist for AI-generated PRs

- Does the change stay within the milestone?
- Are docs and tests updated?
- Are secrets avoided?
- Are provider, storage, rotation, and delivery boundaries preserved?
- Are errors explicit and testable?
- Are migrations included for schema changes?
