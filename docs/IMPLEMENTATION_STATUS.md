# Implementation Status

- **Current milestone:** 1 — World persistence
- **Completed:** FastAPI liveness/readiness and world create/list/get/update endpoints; SQLAlchemy `World` model; Alembic migration; versioned Pydantic request/response schemas; Tauri + React world archive flow; initial Compose stack, environment template, secret ignore rules, and CI workflow.
- **In progress:** PostgreSQL-backed persistence verification remains.
- **Known limitations:** No nations, territories, factions, event history, Kafka consumers, or NiFi flows yet. Local Compose and GitHub Actions have not been run. PostgreSQL connectivity has not been verified in this environment.
- **Cloud smoke deployment:** `mnemosyne-api-smoke` in project `gen-lang-client-0527696821`, region `asia-south1`; revision `mnemosyne-api-smoke-00003-d7v`, IAM protected, scale-to-zero, maximum one instance. World CRUD and validation returned expected HTTP statuses using temporary test invoker access. The deployed service uses ephemeral SQLite.
- **Architecture decisions:** PostgreSQL is authoritative. NiFi integrates and orchestrates. Kafka provides durable event transport. Python owns domain rules. Spark is deferred. See `roadmap.md` for phase-level scope.

## Commands

- Copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`).
- Start local services: `docker compose up --build -d`.
- Stop local services: `docker compose down`.
- Install desktop dependencies: `npm --prefix apps/desktop ci`.
- Run desktop: `npm --prefix apps/desktop run tauri dev`.

## Verification state

Ruff passed. Seven API tests pass on SQLite, including CORS, calendar/seed validation, and idempotent demo seeding. Alembic upgraded a clean SQLite database and `alembic check` reported no model drift. The desktop production build passed. Cloud Build deployed revision `mnemosyne-api-smoke-00003-d7v`; Cloud CRUD smoke checks returned POST 201, list/get/patch 200, and invalid-calendar 422. The temporary public invoker binding was removed and the Cloud Run Invoker IAM check re-enabled. PostgreSQL and full Docker Compose remain unverified. See `README.md` for endpoints and local setup details.

## Next recommended task

Verify PostgreSQL-backed world persistence in Docker Compose or Cloud SQL, then add the first versioned event contract and event history.
