# Mnemosyne

Mnemosyne is a desktop world simulation laboratory for creating persistent fictional worlds, observing how nations and factions evolve, and tracing changes through an inspectable event history.

## Current project state

The repository now has an initial development scaffold: a FastAPI service, a Tauri 2 + React desktop shell, and a local Docker Compose definition for PostgreSQL, Redis, Kafka, and NiFi. The simulation domain, world persistence, event flows, and user-facing world features have not been implemented yet.

## Project brief

Mnemosyne is an observer-focused simulation sandbox rather than a conventional real-time strategy game. The intended experience is to configure a world, let deterministic rules and faction decisions evolve it over monthly ticks, introduce events, and inspect their effects and causal history.

The initial product is single-user. It emphasizes explainable simulation, persistent history, and a polished desktop observatory interface. Multiplayer, tactical combat, LLM-driven decisions, and population-scale simulation are outside the initial scope.

## Current scaffold

- FastAPI liveness and PostgreSQL readiness endpoints.
- Minimal Tauri desktop window with a React/TypeScript landing screen.
- Docker Compose definitions for the API, PostgreSQL, Redis, single-node Kafka, and NiFi.
- GitHub Actions workflow for API lint/compile checks and desktop production build.
- Environment-variable template and ignore rules for local secrets and build output.

The Compose stack and CI workflow have not yet been run in this environment.

## Technology stack

- **Desktop:** Tauri 2, React, TypeScript, and Vite
- **Backend:** Python and FastAPI, structured as a modular monolith
- **Domain and API contracts:** Pydantic
- **Persistence:** PostgreSQL, SQLAlchemy 2, and Alembic (Alembic is planned for the next persistence slice)
- **Transient coordination:** Redis where useful
- **Event transport:** Apache Kafka for durable buffering and decoupled consumers
- **Integration and orchestration:** Apache NiFi for validation, routing, retries, dead-letter handling, scheduled integration, and archival
- **Visualization:** MapLibre GL JS or SVG for maps; Cytoscape.js for relationship graphs; Apache ECharts for charts
- **Local infrastructure:** Docker Compose
- **Hosted target:** Google Cloud Compute Engine and Cloud Storage

Apache Spark is not part of the current MVP stack. It may be evaluated if future analytics or event throughput calls for distributed stream processing.

## Architecture

The desktop client talks only to FastAPI over REST and WebSockets. The Python backend owns world state, simulation rules, event effects, and transactional persistence. PostgreSQL is the source of truth.

The planned event path is: FastAPI transaction/outbox → NiFi validation and routing → Kafka topic → idempotent Python consumer → PostgreSQL state and event history. NiFi handles integration retries, dead-letter routing, and archival. Kafka provides transport and buffering; it is not the event history or domain engine. The application scaffold currently exposes health endpoints only; event processing is not implemented yet.

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

The desktop shell expects the API to be available at `http://127.0.0.1:8000` for future integration. Its first screen is a scaffold and does not yet load world data.

### Stop local services

```powershell
docker compose down
```

Persistent local data is stored in named Docker volumes. To remove that data as well, run `docker compose down --volumes`.

## Project documents

- [Roadmap](roadmap.md) tracks implementation phases, planned features, and future directions.
- `Mnemosyne_Project_Specification.md` is the detailed engineering specification and is intentionally excluded from Git history.
