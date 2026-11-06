# Mnemosyne

Mnemosyne is a desktop world simulation laboratory for creating persistent fictional worlds, observing how nations and factions evolve, and tracing changes through an inspectable event history.

## Current project state

The repository has a working API slice for worlds, nations, and characters, plus a versioned political assassination event with transactional state changes, effect history, causal follow-up events, and idempotent delivery. The Tauri 2 + React desktop currently supports creating and selecting worlds. Kafka and NiFi are scaffolded in the local Compose stack; live event transport through them is not yet implemented.

## Project brief

Mnemosyne is an observer-focused simulation sandbox rather than a conventional real-time strategy game. The intended experience is to configure a world, let deterministic rules and faction decisions evolve it over monthly ticks, introduce events, and inspect their effects and causal history.

The initial product is single-user. It emphasizes explainable simulation, persistent history, and a polished desktop observatory interface. Multiplayer, tactical combat, LLM-driven decisions, and population-scale simulation are outside the initial scope.

## Current scaffold

- FastAPI liveness/readiness plus versioned world, nation, character, and event endpoints.
- SQLAlchemy persistence with Alembic startup migrations for world state and event history.
- Versioned `political.assassination` Pydantic contract with an exported JSON Schema.
- Transactional assassination handling that updates character and nation state, records before/delta/after effects, and links a generated unrest event to its cause.
- Event ID idempotency: identical redelivery returns the prior result without repeating effects; conflicting reuse is rejected.
- Tauri desktop world archive with create, select, and inspect summary flows.
- Idempotent demo-world seed command.
- Docker Compose definitions for the API, PostgreSQL, Redis, single-node Kafka, and NiFi.
- GitHub Actions workflow for API lint/compile checks and desktop production build.
- Environment-variable template and ignore rules for local secrets and build output.

The backend API test suite passes on SQLite, and the migrations have been applied and checked against SQLite. The desktop production build passes. Cloud Run has been used to smoke-test the earlier world API; the latest event API deployment is pending verification. The service uses ephemeral SQLite, so PostgreSQL integration and restart persistence remain unverified. The local Compose stack and GitHub Actions workflow have not yet been run.

## Technology stack

- **Desktop:** Tauri 2, React, TypeScript, and Vite
- **Backend:** Python and FastAPI, structured as a modular monolith
- **Domain and API contracts:** Pydantic
- **Persistence:** PostgreSQL, SQLAlchemy 2, and Alembic
- **Transient coordination:** Redis where useful
- **Event transport:** Apache Kafka for durable buffering and decoupled consumers
- **Integration and orchestration:** Apache NiFi for validation, routing, retries, dead-letter handling, scheduled integration, and archival
- **Visualization:** MapLibre GL JS or SVG for maps; Cytoscape.js for relationship graphs; Apache ECharts for charts
- **Local infrastructure:** Docker Compose
- **Hosted target:** Google Cloud Compute Engine and Cloud Storage

Apache Spark is not part of the current MVP stack. It may be evaluated if future analytics or event throughput calls for distributed stream processing.

## Architecture

The desktop client talks only to FastAPI over REST and WebSockets. The Python backend owns world state, simulation rules, event effects, and transactional persistence. PostgreSQL is the source of truth.

The API reads and writes through SQLAlchemy with versioned routes under `/api/v1`. On startup, Alembic applies migrations before Uvicorn starts. The current first event path applies synchronously in one database transaction and records an inspectable history. The planned transport path is: transactional outbox → NiFi validation and routing → Kafka topic → idempotent Python consumer. NiFi handles integration retries, dead-letter routing, and archival. Kafka provides transport and buffering; it is not the event history or domain engine.

World endpoints currently available:

- `POST /api/v1/worlds` — create a seeded world with calendar and tick configuration.
- `GET /api/v1/worlds` — list worlds, with `limit` and `offset` pagination.
- `GET /api/v1/worlds/{world_id}` — load a world.
- `PATCH /api/v1/worlds/{world_id}` — rename or update world configuration.
- `POST/GET /api/v1/worlds/{world_id}/nations` — create and list nations.
- `POST/GET /api/v1/worlds/{world_id}/characters` — create and list characters.
- `POST /api/v1/worlds/{world_id}/events` — apply a versioned assassination event.
- `GET /api/v1/worlds/{world_id}/events` and `GET /api/v1/events/{event_id}` — inspect event history and causal links.
- `GET /api/v1/events/{event_id}/effects` — inspect recorded entity changes.

Seed the demo world in the local Docker stack with `docker compose exec api python -m mnemosyne_api.seed_demo`. Running the command again reports the existing demo world instead of creating a duplicate.

Redis is optional infrastructure for cache and transient coordination. The desktop client does not connect directly to Kafka or NiFi, and NiFi administration is bound to localhost in the local Compose configuration.

## Installation

### Prerequisites

- Docker Desktop with Docker Compose
- Node.js 22 or newer and npm
- Rust toolchain and the platform prerequisites for Tauri 2 when running the native desktop shell. On Windows, install Microsoft C++ Build Tools and WebView2; other platforms need their native Tauri prerequisites.

### Start local services

1. Copy `.env.example` to `.env` and keep `.env` local. The example values are for development only.

   ```powershell
   Copy-Item .env.example .env
   ```
2. Start the containers:

   ```powershell
   docker compose up --build -d
   ```

3. Check the API health endpoints:

   - Liveness: <http://localhost:8000/health/live>
   - Readiness (includes PostgreSQL): <http://localhost:8000/health/ready>
   - API docs: <http://localhost:8000/docs>

4. Open the local NiFi UI at <https://localhost:8443>. The development credentials are in `.env`.

### Run the desktop shell

From the repository root:

```powershell
npm --prefix apps/desktop ci
npm --prefix apps/desktop run tauri dev
```

The desktop shell expects the API to be available at `http://127.0.0.1:8000`. It loads the world archive and supports creating/selecting worlds.

### Cloud Run smoke instance

The API is deployed as the scale-to-zero `mnemosyne-api-smoke` service in `asia-south1`, explicitly targeting project `gen-lang-client-0527696821`. The service uses internal ingress and has no public invoker binding; its URL is not accessible from the public internet. World CRUD and the assassination event flow were smoke-tested with a temporary invoker binding before ingress was restricted. The deployment uses ephemeral SQLite and is not connected to PostgreSQL; it is not a production deployment.

### Stop local services

```powershell
docker compose down
```

Persistent local data is stored in named Docker volumes. To remove that data as well, run `docker compose down --volumes`.

## Project documents

- [Roadmap](roadmap.md) tracks implementation phases, planned features, and future directions.
- `Mnemosyne_Project_Specification.md` is the detailed engineering specification and is intentionally excluded from Git history.
