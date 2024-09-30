import os
import pytest
import sqlite3
import respx
import httpx
from fastapi.testclient import TestClient
from client import app, init_db, clean_env, get_own_ip

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # 设置测试环境
    init_db()
    yield
    # 清理测试环境
    clean_env()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_receive_messages():
    message = {
        "Tuple": (((1, 2), (3, 4), 5, (6, 7)), 8),
        "ip": "127.0.0.1"
    }
    response = client.post("/receive_messages", json=message)
    assert response.status_code == 200
    assert response.json().get("detail") == "Message received"

# @respx.mock
# def test_request_message():
#     request_message = {
#         "dest_ip": "124.70.165.73",  # 使用不同的 IP 地址
#         "message_name": "name"
#     }
#     respx.post("http://124.70.165.73:8002/receive_request").mock(return_value=httpx.Response(200, json={"threshold": 1, "public_key": "key"}))
#     response = client.post("/request_message", json=request_message)
#     assert response.status_code == 200
#     assert "threshold" in response.json()
#     assert "public_key" in response.json()

# @respx.mock
# def test_receive_request():
#     ip_message = {
#         "dest_ip": "124.70.165.73",  # 使用不同的 IP 地址
#         "message_name": "name",
#         "source_ip": "124.70.165.73",  # 使用不同的 IP 地址
#         "pk": (123, 456)
#     }
#     respx.post("http://124.70.165.73:8002/receive_request").mock(return_value=httpx.Response(200, json={"threshold": 1, "public_key": "key"}))
#     response = client.post("/receive_request", json=ip_message)
#     assert response.status_code == 200
#     assert "threshold" in response.json()
#     assert "public_key" in response.json()

def test_get_pk():
    response = client.get("/get_pk")
    assert response.status_code == 200
    assert "pkx" in response.json()
    assert "pky" in response.json()

def test_recieve_pk():
    pk_data = {
        "pkx": "123",
        "pky": "456",
        "ip": "127.0.0.1"
    }
    response = client.post("/recieve_pk", json=pk_data)
    assert response.status_code == 200
    assert response.json() == {"message": "save pk in database"}

if __name__ == "__main__":
    pytest.main()