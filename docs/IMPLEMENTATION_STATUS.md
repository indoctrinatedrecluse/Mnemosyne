# Implementation Status

- **Current milestone:** 0 — Repository and architecture foundation
- **Completed:** Initial documentation, FastAPI liveness/readiness scaffold, Tauri + React desktop shell, local Compose service definitions, environment template, ignore rules, CI workflow.
- **In progress:** Local stack and native desktop launch remain unconfirmed.
- **Known limitations:** No world models or domain endpoints; no migrations; no Kafka consumers or NiFi flows; Compose and CI have not been run in this environment. Cloud Run readiness used temporary SQLite, so PostgreSQL connectivity has not been verified remotely.
- **Cloud smoke deployment:** `mnemosyne-api-smoke` in project `gen-lang-client-0527696821`, region `asia-south1`; IAM protected, scale-to-zero, maximum one instance. Liveness and readiness both returned HTTP 200. Anonymous access returned HTTP 403 after test access was removed.
- **Architecture decisions:** PostgreSQL is authoritative. NiFi integrates and orchestrates. Kafka provides durable event transport. Python owns domain rules. Spark is deferred. See `roadmap.md` for phase-level scope.

## Commands

- Copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`).
- Start local services: `docker compose up --build -d`.
- Stop local services: `docker compose down`.
- Install desktop dependencies: `npm --prefix apps/desktop install`.
- Run desktop: `npm --prefix apps/desktop run tauri dev`.

## Verification state

Cloud Build built the API image and Cloud Run reported the revision ready. Requests to `/health/live` and `/health/ready` returned HTTP 200 while a temporary invoker test binding was active; readiness used ephemeral SQLite. The temporary binding was removed, and an unauthenticated request then returned HTTP 403. No automated tests were run. See `README.md` for endpoints and local setup details.

## Next recommended task

Confirm Phase 0 startup on a machine with Docker Desktop, then begin Phase 1 with SQLAlchemy/Alembic and persistent world create/read endpoints.
