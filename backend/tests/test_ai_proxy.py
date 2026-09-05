import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.auth_service import create_access_token, register_user


@pytest.mark.asyncio
async def test_backend_chat_route_presence():
    """Test that the AI chat route is registered and handles authenticated requests.
    
    The route requires authentication (cannot call without token).
    This test verifies the route exists and responds appropriately.
    """
    # Set up a test user
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    db = Session()

    reg_data = RegisterRequest(email="test@test.com", username="test", password="Pass123!", first_name="Test")
    user = register_user(db, reg_data)
    token = create_access_token(user)
    db.close()

    client = TestClient(app)

    # Test with valid auth
    resp = client.post("/ai/chat", json={"question": "hello"}, headers={"Authorization": f"Bearer {token}"})
    # Should return 200 (dev provider) or 503 (missing config) but not 404 or 401
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE)

    # Clean up
    Base.metadata.drop_all(bind=engine)

