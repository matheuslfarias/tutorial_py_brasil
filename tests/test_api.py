from fastapi.testclient import TestClient
from http import HTTPStatus

import pytest

from api.api_pedidos import app
from api.api_magalu import recuperar_itens_por_pedido

from uuid import UUID
from api.esquema import Item
from api.excecao import PedidoNaoEncontradoError, FalhaDeComunicacaoError




@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sobreescreve_recuperar_itens_por_pedido():
    def _sobreescreve_recuperar_itens_por_pedido(itens_ou_erro):
        def duble(identificacao_do_pedido: UUID) -> list[Item]:
            if isinstance(itens_ou_erro, Exception):
                raise itens_ou_erro
            return itens_ou_erro
        app.dependency_overrides[recuperar_itens_por_pedido] = duble
    yield _sobreescreve_recuperar_itens_por_pedido
    app.dependency_overrides.clear()


class TestHealthCheck:
    # Testa a integridade da pagina
    def test_page_integrity(self,client):
        response = client.get("/healthcheck")
        assert response.status_code == HTTPStatus.OK
        

    # Testa se a aplicação tem formato json
    def test_content_type_json(self,client):
        response = client.get("/healthcheck")
        assert response.headers["Content-Type"] == "application/json"


    # Testa se o retorno do endpoint é {"status": "ok"}
    def test_status_response(self,client):
        response = client.get("/healthcheck")
        assert response.json() == {"status": "ok"}


class TestListOrders:
    # Enviar identificação de pedido inválido
    def test_unprocessable_entity_item(self,client):
        response = client.get("/orders/valor-invalido/items")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    
    def test_when_order_not_find_error_return(self, client,sobreescreve_recuperar_itens_por_pedido):
        sobreescreve_recuperar_itens_por_pedido(PedidoNaoEncontradoError())
        resposta = client.get("/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items")
        assert resposta.status_code == HTTPStatus.NOT_FOUND


    # Testar a obtenção de itens, retornar NOT_FOUND quando pedido não for encontrado
    def test_get_items_when_order_identification_not_found_an_error_should_be_returned(self,client,sobreescreve_recuperar_itens_por_pedido):
        sobreescreve_recuperar_itens_por_pedido([])
        resposta = client.get("/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items")
        assert resposta.status_code == HTTPStatus.OK

    def test_get_items_when_find_order_do_return_items(self,client,sobreescreve_recuperar_itens_por_pedido):
        items = [
            Item(sku='1', description='Item 1', image_url='http://url.com/img1', reference='ref1', quantity=1),
            Item(sku='2', description='Item 2', image_url='http://url.com/img2', reference='ref2', quantity=2),
        ]
        sobreescreve_recuperar_itens_por_pedido(items)
        resposta = client.get("/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items")
        assert resposta.json() == items

    def test_when_database_of_orders_fail_return_error(self,client, sobreescreve_recuperar_itens_por_pedido):
        sobreescreve_recuperar_itens_por_pedido(FalhaDeComunicacaoError())
        resposta = client.get("/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items")
        assert resposta.status_code == HTTPStatus.BAD_GATEWAY


