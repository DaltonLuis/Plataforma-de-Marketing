from fastapi.testclient import TestClient

from BACKEND.main import app

client = TestClient(app)


def test_list_seller():
    response = client.get('/see/addresses')
    assert response.status_code == 200
