
import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

@pytest.mark.asyncio
async def test_signup_and_unregister():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act: Sign up
        signup_resp = await ac.post(f"/activities/{activity}/signup?email={test_email}")
        # Assert: Signup
        assert signup_resp.status_code == 200
        assert f"Signed up {test_email}" in signup_resp.json()["message"]

        # Act: Duplicate signup
        dup_resp = await ac.post(f"/activities/{activity}/signup?email={test_email}")
        # Assert: Duplicate signup
        assert dup_resp.status_code == 400
        assert "already signed up" in dup_resp.json()["detail"]

        # Act: Unregister
        del_resp = await ac.delete(f"/activities/{activity}/unregister?email={test_email}")
        # Assert: Unregister
        assert del_resp.status_code == 200
        assert f"Removed {test_email}" in del_resp.json()["message"]

        # Act: Unregister again (should fail)
        del_resp2 = await ac.delete(f"/activities/{activity}/unregister?email={test_email}")
        # Assert: Not found
        assert del_resp2.status_code == 404
        assert "Participant not found" in del_resp2.json()["detail"]

@pytest.mark.asyncio
async def test_root_redirect():
    # Arrange
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/")
    # Assert
    assert response.status_code in (200, 307, 302)  # Redirect or direct
    # Optionally check for redirect location
    if response.is_redirect:
        assert "/static/index.html" in response.headers.get("location", "")
