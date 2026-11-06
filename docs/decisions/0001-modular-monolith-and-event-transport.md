# ADR 0001: Modular monolith and event transport

- **Status:** Accepted
- **Date:** 2026-11-06

## Context

Mnemosyne is a single-user world simulation with a small initial workload. The architecture needs transactional world state, deterministic domain rules, durable event transport, and observable integration flows without introducing a distributed application backend prematurely.

## Decision

- Keep the Python/FastAPI application as a modular monolith. It owns domain rules, world state, and transactional mutations.
- Use PostgreSQL as the authoritative source for worlds, events, effects, and snapshots.
- Use a transactional outbox to publish committed events to Apache NiFi.
- Use NiFi for validation, routing, retries, dead-letter handling, archival, and pipeline visibility.
- Use Kafka for durable buffering and consumer decoupling. Consumers must be idempotent; Kafka is not the canonical event history.
- Keep Redis optional for cache and short-lived coordination.
- Defer Spark until a concrete streaming analytics workload justifies it. Do not add Kubernetes or split the backend into microservices for the MVP.

## Consequences

The MVP has more local infrastructure than a basic CRUD app, but NiFi and Kafka have explicit responsibilities in the event pipeline. The domain remains testable without running NiFi or Kafka. PostgreSQL transactions and idempotency protect world state from repeated delivery.

The current Cloud Run smoke service uses ephemeral SQLite solely to exercise API behavior. It does not replace PostgreSQL for a persistent deployment.
