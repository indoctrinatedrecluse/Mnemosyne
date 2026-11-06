from uuid import uuid4


def test_world_create_list_get_and_update(client):
    created = client.post(
        "/api/v1/worlds",
        json={
            "name": "  The Shattered Meridian  ",
            "description": "A deterministic demo world.",
            "seed": 73421,
            "calendar_start_year": 104,
            "calendar_start_month": 7,
            "tick_interval_seconds": 10,
        },
    )

    assert created.status_code == 201
    world = created.json()
    assert world["name"] == "The Shattered Meridian"
    assert world["seed"] == 73421
    assert world["calendar_start_year"] == 104
    assert world["calendar_start_month"] == 7

    listed = client.get("/api/v1/worlds")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == world["id"]

    loaded = client.get(f"/api/v1/worlds/{world['id']}")
    assert loaded.status_code == 200
    assert loaded.json()["seed"] == world["seed"]

    updated = client.patch(
        f"/api/v1/worlds/{world['id']}",
        json={"name": "The Meridian", "description": None},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "The Meridian"
    assert updated.json()["description"] is None


def test_world_creation_rejects_invalid_calendar(client):
    response = client.post(
        "/api/v1/worlds",
        json={"name": "Invalid Calendar", "seed": 1, "calendar_start_month": 13},
    )

    assert response.status_code == 422
    assert response.json()["detail"]


def test_world_creation_rejects_seed_outside_javascript_safe_range(client):
    response = client.post(
        "/api/v1/worlds",
        json={"name": "Unsafe Seed", "seed": 9_007_199_254_740_992},
    )

    assert response.status_code == 422
    assert response.json()["detail"]


def test_world_update_rejects_empty_or_null_required_fields(client):
    created = client.post("/api/v1/worlds", json={"name": "Valid", "seed": 1})
    world_id = created.json()["id"]

    empty_patch = client.patch(f"/api/v1/worlds/{world_id}", json={})
    null_name_patch = client.patch(f"/api/v1/worlds/{world_id}", json={"name": None})

    assert empty_patch.status_code == 422
    assert null_name_patch.status_code == 422


def test_missing_world_returns_structured_not_found(client):
    response = client.get(f"/api/v1/worlds/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "World not found"}


def test_desktop_dev_origin_is_allowed_by_cors(client):
    response = client.options(
        "/api/v1/worlds",
        headers={
            "Origin": "http://127.0.0.1:1420",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:1420"
