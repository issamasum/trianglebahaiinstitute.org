# Deployment

## Database migrations

Schema changes are managed with Alembic
(`packages/trianglebahaiinstitute-core/migrations`).

**Run migrations once per deploy, before the new API version starts serving
traffic**, as a separate step (pre-deploy job or init container), not as part
of API startup:

```bash
cd packages/trianglebahaiinstitute-core
ENVIRONMENT=production DATABASE_URL=... alembic upgrade head
```

Properties the migration setup guarantees (covered by
`test/test_migrations.py`):


Guidelines for writing migrations that are safe during a rolling deploy
(old and new API versions run side by side briefly):

- Make changes backwards compatible: add nullable columns/tables first;
  remove or rename in a later release once no running version uses them
  (expand/contract).
- Don't make long-locking changes (e.g. adding a non-null column with a
  default on a large table) without planning for it.
- Never edit a migration that has been deployed; add a new one.

Creating a migration after changing models:

```bash
alembic revision --autogenerate -m "describe change"
```

Review the generated file, then run the backend tests.

