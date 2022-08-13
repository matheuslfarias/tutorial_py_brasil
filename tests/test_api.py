from fastapi.testclient import TestClient
from http import HTTPStatus

import pytest

from api.api_pedidos import app

@pytest.fixture
def client():
    return TestClient(app)

# Testa a integridade da pagina
def test_page_integrity(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK
    

# Testa se a aplicação tem formato json
def test_content_type_json(client):
    response = client.get("/healthcheck")
    assert response.headers["Content-Type"] == "application/json"


# Testa se o retorno do endpoint é {"status": "ok"}
def test_status_response(client):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}






