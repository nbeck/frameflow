# Engineering Principles

FrameFlow is a self-hosted photo server optimized for digital displays. These principles guide architecture, implementation, roadmap decisions, and tradeoffs.

## 1. Self-hosted first

FrameFlow should not require paid cloud services or proprietary infrastructure to operate.

## 2. Offline capable

Core photo serving, scheduling, and rotation should continue working without internet access once the library is available locally.

## 3. Non-destructive by default

FrameFlow must never modify, overwrite, or delete original photos unless the user explicitly requests that behavior.

## 4. Incremental synchronization

FrameFlow should detect additions, updates, and deletions without requiring full rescans whenever practical.

## 5. Idempotent operations

Repeated sync, scan, migration, and bootstrap operations should be safe to rerun.

## 6. API-first architecture

Every administrative action should be available through the API, even if a UI later exposes it.

## 7. Explainable rotation

Photo selection should be understandable, testable, and debuggable. FrameFlow should avoid repeated photos through explicit scheduling rules, not opaque randomness.

## 8. Observability from day one

Logging, health checks, diagnostics, and metrics should be treated as core product capabilities.

## 9. Configuration over code

Common deployment and behavior changes should be handled through configuration rather than code changes.

## 10. Portfolio-quality execution

FrameFlow should favor clarity, maintainability, documentation, and reproducibility over clever shortcuts.
