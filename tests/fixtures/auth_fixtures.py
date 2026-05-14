import time
import pytest

from tests.utils.api_client import APIClient


@pytest.fixture
def auth_api(api_url):

    return APIClient(api_url)


@pytest.fixture
def existing_user(auth_api):

    payload = {
        "full_name": "Người Dùng Gốc",
        "email": f"test_{int(time.time())}@example.com",
        "password": "StrongPassw0rd!"
    }

    response = auth_api.post(
        "/auth/register",
        json=payload
    )

    assert response.status_code in [200, 201], (
        f"Không tạo được user: "
        f"{response.status_code} {response.text}"
    )

    user = response.json()

    user["password"] = payload["password"]

    yield user

    if "id" in user:
        auth_api.delete(f"/auth/users/{user['id']}")