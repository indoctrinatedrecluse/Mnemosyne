# Implementation Status

- **Current milestone:** 4 — NiFi and Kafka event pipeline
- **Completed:** World CRUD; nation and character CRUD; versioned assassination event contract and JSON Schema; transactional character/nation updates; event effects, causal pending unrest follow-up, event inspection, and idempotent event ID handling; Tauri + React world archive flow; initial Compose stack, environment template, secret ignore rules, and CI workflow.
- **In progress:** Transactional outbox and NiFi/Kafka delivery path; PostgreSQL-backed persistence verification.
- **Known limitations:** Current domain slice has nations and characters only; territories, factions, relationships, and resources remain. No live Kafka consumer or NiFi flow yet. Local Compose and GitHub Actions have not been run. PostgreSQL connectivity has not been verified in this environment.
- **Cloud smoke deployment:** `mnemosyne-api-smoke` in project `gen-lang-client-0527696821`, region `asia-south1`; revision `mnemosyne-api-smoke-00004-2lz`, internal ingress, no service-level invoker bindings, scale-to-zero, maximum one instance. World, nation, character, and assassination event flows returned expected results using a temporary test invoker binding. Anonymous access to the public URL returns 404 after internal ingress was applied. The deployed service uses ephemeral SQLite.
- **Architecture decisions:** PostgreSQL is authoritative. NiFi integrates and orchestrates. Kafka provides durable event transport. Python owns domain rules. Spark is deferred. See `roadmap.md` for phase-level scope.

## Commands

- Copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`).
- Start local services: `docker compose up --build -d`.
- Stop local services: `docker compose down`.
- Install desktop dependencies: `npm --prefix apps/desktop ci`.
- Run desktop: `npm --prefix apps/desktop run tauri dev`.

## Verification state

Ruff passed. Ten API tests pass on SQLite. Alembic upgraded a clean SQLite database and `alembic check` reported no model drift. The desktop production build passed. Cloud Run revision `mnemosyne-api-smoke-00004-2lz` verified world/nation/character creation, assassination application, duplicate delivery, effect history, and follow-up linkage; anonymous public ingress returns 404 after ingress was restricted. The service uses ephemeral SQLite. PostgreSQL and full Docker Compose remain unverified. See `README.md` for endpoints and local setup details.

## Next recommended task

Add the transactional outbox and NiFi/Kafka delivery path, then verify persistent PostgreSQL storage and local Compose startup.
