"""Profile + family history tests."""

from tests.conftest import auth


def test_profile_get_create_and_update(client, user_token):
    # No data yet → an empty profile is returned on first access
    resp = client.get("/profile", headers=auth(user_token))
    assert resp.status_code == 200
    assert resp.json()["height_cm"] is None

    # Update (upserts the profile)
    resp = client.put(
        "/profile",
        headers=auth(user_token),
        json={
            "height_cm": 175,
            "weight_kg": 70,
            "blood_type": "O_POSITIVE",
            "medical_conditions": "none",
            "allergies": "peanuts",
            "medications": "none",
            "lifestyle": "active",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["height_cm"] == 175
    assert resp.json()["blood_type"] == "O_POSITIVE"
    assert resp.json()["allergies"] == "peanuts"
    assert resp.json()["lifestyle"] == "active"

    # Read back
    assert client.get("/profile", headers=auth(user_token)).status_code == 200

    # Update
    resp = client.put(
        "/profile",
        headers=auth(user_token),
        json={"height_cm": 180, "weight_kg": 72, "allergies": "peanuts, shellfish"},
    )
    assert resp.json()["height_cm"] == 180
    assert resp.json()["allergies"] == "peanuts, shellfish"


def test_family_history_crud(client, user_token):
    # Create
    create = client.post(
        "/profile/family-history",
        headers=auth(user_token),
        json={"category": "DIABETES", "relation": "Father", "notes": "Type 2"},
    )
    assert create.status_code == 201
    fid = create.json()["id"]

    # Read all
    all_hist = client.get("/profile/family-history", headers=auth(user_token)).json()
    assert len(all_hist) == 1

    # Read by id
    detail = client.get(f"/profile/family-history/{fid}", headers=auth(user_token)).json()
    assert detail["relation"] == "Father"

    # Update
    update = client.put(
        f"/profile/family-history/{fid}",
        headers=auth(user_token),
        json={"relation": "Mother", "notes": "Type 1"},
    )
    assert update.json()["relation"] == "Mother"

    # Delete
    assert client.delete(f"/profile/family-history/{fid}", headers=auth(user_token)).status_code == 200
    assert len(client.get("/profile/family-history", headers=auth(user_token)).json()) == 0


def test_profile_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "otherprofile@example.com", "otherprofile")
    client.put("/profile", headers=auth(user_token), json={"height_cm": 175, "weight_kg": 70})
    client.post(
        "/profile/family-history",
        headers=auth(user_token),
        json={"category": "HYPERTENSION", "relation": "Parent"},
    )

    other_profile = client.get("/profile", headers=auth(other_token)).json()
    assert other_profile["height_cm"] is None  # Other user has no profile data

    other_hist = client.get("/profile/family-history", headers=auth(other_token)).json()
    assert len(other_hist) == 0