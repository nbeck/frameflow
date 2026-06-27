# Initial Issues

These are recommended issues to create after pushing the repository.

## Milestone 1

1. Define SQLAlchemy models for providers, albums, assets, originals, generated assets, displays, policies, sync runs, and display events.
2. Add initial Alembic migration for core schema.
3. Implement storage path planner for originals and generated assets.
4. Implement checksum utility and validation flow.
5. Add repository layer for core entities.
6. Add configuration loading for data root and database URL.
7. Add tests for storage path safety and immutability rules.
8. Add tests for migration upgrade and downgrade path where practical.

## Milestone 2

1. Define provider contract.
2. Implement local folder provider.
3. Implement sync run records.
4. Implement reconciliation planning.
5. Implement original import flow.
6. Implement missing upstream detection.
7. Add provider contract tests.

## Milestone 3

1. Implement display policy model.
2. Implement eligibility filtering.
3. Implement basic scoring.
4. Record display events.
5. Add selection explanation object.
6. Add rotation tests for repetition avoidance.

## Milestone 4

1. Implement display token model.
2. Implement `/next` delivery endpoint.
3. Add DAKboard setup documentation.
4. Add cache behavior tests.
5. Add display diagnostics endpoint.
