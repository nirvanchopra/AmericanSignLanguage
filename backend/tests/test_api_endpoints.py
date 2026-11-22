import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "SignBridge" in data["service"]

@pytest.mark.asyncio
async def test_auth_login_and_me():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login demo user
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "demo@signbridge.ai",
            "password": "DemoPass123!"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # Call /me
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        user_data = me_res.json()
        assert user_data["email"] == "demo@signbridge.ai"
        assert user_data["role"] == "user"

@pytest.mark.asyncio
async def test_models_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/recognition/models")
        assert res.status_code == 200
        models = res.json()
        assert len(models) >= 3
        tags = [m["version_tag"] for m in models]
        assert "landmarknet-v1.0" in tags
        assert "cnn8grps-legacy" in tags

@pytest.mark.asyncio
async def test_translation_engine():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test letter spelling into word and sentence
        tokens = ["H", "E", "L", "L", "O", "SPACE", "W", "O", "R", "L", "D"]
        res = await ac.post("/api/v1/translation/process", json={"tokens": tokens})
        assert res.status_code == 200
        data = res.json()
        assert "Hello world." in data["sentence"]
        assert data["current_word"] == "WORLD"
        assert "tts_text" in data

@pytest.mark.asyncio
async def test_recognition_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        mock_lms = [{"x": 0.5 + 0.01 * i, "y": 0.5 - 0.02 * i, "z": 0.0} for i in range(21)]
        res = await ac.post("/api/v1/recognition/recognize", json={
            "landmarks": mock_lms,
            "handedness": "Right",
            "model_preference": "landmarknet"
        })
        assert res.status_code == 200
        data = res.json()
        assert "stabilized_label" in data
        assert "top3" in data
        assert "latency_ms" in data

if __name__ == "__main__":
    asyncio.run(test_health_check())
    asyncio.run(test_auth_login_and_me())
    asyncio.run(test_models_list())
    asyncio.run(test_translation_engine())
    asyncio.run(test_recognition_endpoint())
    print("All API integration tests verified successfully!")
