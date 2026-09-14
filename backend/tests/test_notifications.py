"""Notifications API tests."""

from tests.conftest import auth


def seed_notification(client):
    """Create a notification directly in the DB for the test user (id=1)."""
    from sqlalchemy.orm import sessionmaker
    from app.database.database import engine
    from app.models.notification import Notification

    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(Notification(user_id=1, type="system", title="Test notice", body="hello"))
    db.commit()
    db.close()


def test_list_and_mark_read(client, user_token):
    seed_notification(client)
    listed = client.get("/notifications", headers=auth(user_token)).json()
    assert listed["total"] == 1
    nid = listed["items"][0]["id"]
    assert listed["items"][0]["is_read"] is False

    marked = client.post(f"/notifications/{nid}/read", headers=auth(user_token))
    assert marked.json()["is_read"] is True


def test_mark_all_read(client, user_token):
    seed_notification(client)
    result = client.post("/notifications/read-all", headers=auth(user_token))
    assert result.json()["marked_read"] == 1


def test_unread_filter(client, user_token):
    seed_notification(client)
    unread = client.get("/notifications?unread_only=true", headers=auth(user_token)).json()
    assert unread["total"] == 1


def test_notification_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "othernotif@example.com", "othernotif")
    seed_notification(client)
    nid = client.get("/notifications", headers=auth(user_token)).json()["items"][0]["id"]
    assert client.post(f"/notifications/{nid}/read", headers=auth(other_token)).status_code == 404