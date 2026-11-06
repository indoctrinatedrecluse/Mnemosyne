# Mnemosyne

Mnemosyne is a desktop world simulation laboratory for creating persistent fictional worlds, observing how nations and factions evolve, and tracing changes through an inspectable event history.

## Current project state

The repository currently contains project documentation only. Application code and runnable installation steps have not been added yet.

## Project brief

Mnemosyne is designed as an observer-focused simulation sandbox rather than a conventional real-time strategy game. A user will configure a world, allow deterministic rules and faction decisions to evolve it over discrete monthly ticks, introduce events, and inspect their effects and causal history.

The initial product is single-user. It emphasizes explainable simulation, persistent history, and a polished desktop observatory interface. Multiplayer, tactical combat, LLM-driven decisions, and population-scale simulation are outside the initial scope.

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

For event processing, the backend writes canonical events and outbox records in one database transaction. An outbox dispatcher delivers committed envelopes to NiFi. NiFi validates and routes them to versioned Kafka topics, manages integration retries and dead-letter paths, and coordinates archival. Idempotent Python consumers apply simulation effects and persist results to PostgreSQL. Kafka provides transport and buffering; it is not the event history or domain engine.

Redis is optional infrastructure for cache and transient coordination. The desktop client does not connect directly to Kafka or NiFi, and NiFi administration remains private.

## Installation

**Status: TBD.** There is no runnable application or install script yet. Installation instructions will be added once the initial repository foundation and local Docker Compose environment are implemented.

The intended local setup is Docker Compose for backend services and the desktop development toolchain, with configuration supplied through an environment file. Do not put secrets in source control.

## Project documents

- `roadmap.md` tracks implementation phases, planned features, and future directions.
- `Mnemosyne_Project_Specification.md` is the detailed engineering specification and is intentionally excluded from Git history.
