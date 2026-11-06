# Mnemosyne Roadmap

This file tracks planned and in-progress work. Completed capabilities should be reflected in `README.md`; keep implementation claims there limited to what exists and works.

## Status key

- **Current** — actively being implemented
- **Next** — the next intended phase
- **Planned** — accepted scope with no active implementation
- **Future** — post-MVP or dependent on a demonstrated need

## Current state

- **Current:** Phase 0 — repository and architecture foundation
- Added initial API and Tauri desktop scaffolds, local service definitions, environment template, and CI workflow.
- Compose startup and CI execution have not yet been confirmed in this environment.
- The simulation engine, persistence models, and NiFi/Kafka event flow are not implemented.

## MVP development phases

### Phase 0 — Repository and architecture foundation

**Current**

- [x] Initialize Python and desktop frontend tooling.
- [x] Add Docker Compose definitions for PostgreSQL, Redis, Kafka, NiFi, and FastAPI.
- [x] Add environment configuration template and secret/build ignore rules.
- [x] Add FastAPI liveness and database readiness endpoints.
- [x] Add initial CI workflow.
- [x] Build and deploy an isolated Cloud Run smoke instance with the explicit project target; confirm liveness and readiness responses.
- [x] Confirm the smoke instance requires Cloud Run Invoker access after testing.
- [ ] Start the full Compose stack and confirm service health checks.
- [ ] Confirm the desktop native shell builds on the development machine.
- [ ] Record architecture decisions and complete local setup notes.

**Done when:** a clean checkout can start the local stack, the API reports healthy, and database connectivity is verified. NiFi administration is accessible only locally or privately.

### Phase 1 — World persistence

**Next**

- Add SQLAlchemy models, Alembic migrations, and world create/list/get/update endpoints.
- Persist world seed and calendar configuration.
- Add a minimal world creation UI and demo world fixture.

**Done when:** a world can be created through the API and desktop UI, survives container restart, and can be loaded with useful validation errors for invalid requests.

### Phase 2 — Entities and event contracts

**Planned**

- Add nations, territories, factions, characters, relationships, and resources.
- Define versioned Pydantic event envelopes and export JSON Schema.
- Add event history, schema validation, and idempotency records.

**Done when:** entities can be created and referenced within a world, malformed events are rejected, and duplicate submissions do not repeat changes.

### Phase 3 — First simulation event

**Planned**

- Implement transactional event application and effect records.
- Add one initial political event with a follow-up event.
- Expose event details and causal links through the API.

**Done when:** the event changes state transactionally, records before/delta/after effects, links generated events to their cause, and safely tolerates redelivery.

### Phase 4 — NiFi and Kafka event pipeline

**Planned**

- Dispatch committed outbox envelopes to NiFi.
- Configure NiFi validation, routing, Kafka publication/consumption, retry, and dead-letter flows.
- Add an idempotent Python Kafka consumer and internal service authentication.
- Expose pipeline health and processing status.

**Done when:** events move through NiFi and Kafka to the Python consumer, transient failures retry, exhausted failures are inspectable, duplicate delivery is harmless, and persisted queues recover after restart.

### Phase 5 — Simulation clock and faction behavior

**Planned**

- Add per-world tick, pause, resume, and step controls.
- Protect concurrent ticks and record tick history.
- Implement explainable faction candidate scoring and seeded decisions.

**Done when:** each manual tick advances exactly once, concurrent requests are safe, and decision candidates and scores are recorded reproducibly.

### Phase 6 — Desktop vertical slice

**Planned**

- Build the Tauri and React shell, world selector, and World Observatory.
- Add event creation, timeline, nation detail, REST integration, and WebSocket updates.

**Done when:** a user can select a world, inspect its entities, issue an event, and see the server-confirmed result, including after reconnect.

### Phase 7 — Relationships, analytics, and history

**Planned**

- Add diplomacy graph and accessible relationship list.
- Add event filtering/search, causal graph, stability/resource charts, and snapshots.

**Done when:** stored relationship and event history can be inspected and snapshot creation/validation works.

### Phase 8 — Operational resilience

**Planned**

- Add structured logs, pipeline metrics, NiFi operational summary, dead-letter inspection, controlled replay, and archival.
- Document and verify backup and restore.

**Done when:** failures can be inspected and safely replayed, archives are tracked, and restoration is demonstrated in a test environment.

### Phase 9 — Deployment and release polish

**Planned**

- Prepare production Compose configuration and GCP Compute Engine deployment.
- Configure Cloud Storage archive destination, HTTPS, private NiFi administration, desktop packaging, and operator documentation.

**Done when:** the stack deploys securely, persistent data survives restart, and backup/recovery steps are verified.

## Future directions

These are outside the initial MVP and should be reconsidered after the core simulation is working:

- Spark Structured Streaming for concrete high-volume analytics or event-time aggregations.
- Mythological and historical world presets.
- Dynasties, family trees, inheritance, marriages, and succession.
- Religion, cults, belief systems, and schisms.
- Warfare, campaigns, sieges, and conquest.
- Trade routes and deeper economic simulation.
- Procedural map generation and narrative chronicles.
- Optional LLM-assisted descriptions and diplomatic messages.
- Modding API, world export/import, and advanced branching/replay.

## Architecture guardrails

- Python owns simulation rules and all authoritative state mutations.
- PostgreSQL is the canonical source of truth; Kafka is transport and buffering.
- NiFi owns integration flow, validation/routing, retries, dead-letter handling, archival, and operational visibility.
- Consumers and tick requests must be idempotent; world mutations must be transactional.
- Add infrastructure only when a specific workload or acceptance criterion justifies it. Spark, Kubernetes, Neo4j, and multiplayer remain out of MVP scope.
