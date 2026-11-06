from uuid import uuid4


def create_assassination_fixture(client):
    world = client.post("/api/v1/worlds", json={"name": "Event World", "seed": 2}).json()
    nation_response = client.post(
        f"/api/v1/worlds/{world['id']}/nations",
        json={"name": "Oris", "government_type": "Theocracy", "stability": 72, "unrest": 12},
    )
    assert nation_response.status_code == 201
    nation = nation_response.json()
    character_response = client.post(
        f"/api/v1/worlds/{world['id']}/characters",
        json={"nation_id": nation["id"], "name": "High Priest of Oris", "role": "High Priest"},
    )
    assert character_response.status_code == 201
    return world, nation, character_response.json()


def assassination_payload(world_id, character_id, *, event_id=None, severity=8):
    return {
        "event_id": event_id or str(uuid4()),
        "world_id": world_id,
        "schema_version": 1,
        "event_type": "political.assassination",
        "simulation_date": {"year": 104, "month": 3},
        "target_character_id": character_id,
        "severity": severity,
        "payload": {"method": "poison"},
    }


def test_assassination_applies_effects_and_records_causal_followup(client):
    world, nation, character = create_assassination_fixture(client)
    payload = assassination_payload(world["id"], character["id"])

    submitted = client.post(f"/api/v1/worlds/{world['id']}/events", json=payload)
    assert submitted.status_code == 201
    event = submitted.json()
    assert event["status"] == "applied"
    assert event["event_type"] == "political.assassination"
    assert len(event["generated_event_ids"]) == 1

    changed_character = client.get(
        f"/api/v1/worlds/{world['id']}/characters/{character['id']}"
    ).json()
    changed_nation = client.get(f"/api/v1/worlds/{world['id']}/nations").json()[0]
    assert changed_character["status"] == "deceased"
    assert changed_nation["stability"] == 64
    assert changed_nation["unrest"] == 20

    effects = client.get(f"/api/v1/events/{event['id']}/effects")
    assert effects.status_code == 200
    assert len(effects.json()) == 3
    assert effects.json()[1]["before_value"] == 72
    assert effects.json()[1]["delta_value"] == -8
    assert effects.json()[1]["after_value"] == 64

    history = client.get(f"/api/v1/worlds/{world['id']}/events").json()
    follow_up = next(item for item in history if item["id"] == event["generated_event_ids"][0])
    assert follow_up["event_type"] == "political.unrest"
    assert follow_up["status"] == "pending"
    assert follow_up["parent_event_id"] == event["id"]


def test_repeated_event_id_is_idempotent_and_conflicting_reuse_is_rejected(client):
    world, nation, character = create_assassination_fixture(client)
    payload = assassination_payload(world["id"], character["id"], severity=4)
    path = f"/api/v1/worlds/{world['id']}/events"

    first = client.post(path, json=payload)
    duplicate = client.post(path, json=payload)
    conflicting_payload = {**payload, "severity": 5}
    conflict = client.post(path, json=conflicting_payload)

    assert first.status_code == 201
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True
    assert duplicate.json()["id"] == first.json()["id"]
    assert conflict.status_code == 409
    nation_after = client.get(f"/api/v1/worlds/{world['id']}/nations").json()[0]
    assert nation_after["stability"] == 68
    assert nation_after["unrest"] == 16
    history = client.get(f"/api/v1/worlds/{world['id']}/events").json()
    assert len(history) == 2


def test_event_rejects_world_mismatch_and_malformed_envelope(client):
    world, _, character = create_assassination_fixture(client)
    payload = assassination_payload(str(uuid4()), character["id"])
    mismatch = client.post(f"/api/v1/worlds/{world['id']}/events", json=payload)
    malformed = client.post(
        f"/api/v1/worlds/{world['id']}/events",
        json={"event_id": str(uuid4()), "world_id": world["id"], "schema_version": 2},
    )

    assert mismatch.status_code == 422
    assert malformed.status_code == 422
