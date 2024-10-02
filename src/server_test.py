import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import sqlite3
import pytest
from fastapi.testclient import TestClient
from server import app, validate_ip

# 创建 TestClient 实例
client = TestClient(app)


# 准备测试数据库数据
def setup_db():
    # 创建数据库并插入测试数据
    with sqlite3.connect("server.db") as db:
        db.execute(
            """
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY, 
            ip TEXT NOT NULL, 
            last_heartbeat INTEGER NOT NULL
        )
        """
        )
        db.execute(
            "INSERT INTO nodes (ip, last_heartbeat) VALUES ('192.168.0.1', 1234567890)"
        )
        db.execute(
            "INSERT INTO nodes (ip, last_heartbeat) VALUES ('192.168.0.2', 1234567890)"
        )
        db.commit()


# 清空数据库
def clear_db():
    with sqlite3.connect("server.db") as db:
        db.execute("DROP TABLE IF EXISTS nodes")  # 删除旧表
        db.commit()


# 测试 IP 验证功能
def test_validate_ip():
    assert validate_ip("192.168.0.1") is True
    assert validate_ip("256.256.256.256") is False
    assert validate_ip("::1") is True
    assert validate_ip("invalid_ip") is False


# 测试首页路由
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


# 测试 show_nodes 路由
def test_show_nodes():
    setup_db()

    response = client.get("/server/show_nodes")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0][1] == "192.168.0.1"
    assert data[1][1] == "192.168.0.2"


# 测试 get_node 路由
def test_get_node():
    # 确保数据库和表的存在
    setup_db()

    valid_ip = "192.168.0.3"
    invalid_ip = "256.256.256.256"

    # 测试有效的 IP 地址
    response = client.get(f"/server/get_node?ip={valid_ip}")
    assert response.status_code == 200

    # 测试无效的 IP 地址
    response = client.get(f"/server/get_node?ip={invalid_ip}")
    assert response.status_code == 400


# 测试 delete_node 路由
def test_delete_node():
    setup_db()

    valid_ip = "192.168.0.1"
    invalid_ip = "192.168.0.255"

    response = client.get(f"/server/delete_node?ip={valid_ip}")
    assert response.status_code == 200
    assert "Node with IP 192.168.0.1 deleted successfully." in response.text

    response = client.get(f"/server/delete_node?ip={invalid_ip}")
    assert response.status_code == 404


# 测试 heartbeat 路由
def test_receive_heartbeat():
    setup_db()

    valid_ip = "192.168.0.2"
    invalid_ip = "256.256.256.256"

    response = client.get(f"/server/heartbeat?ip={valid_ip}")
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

    response = client.get(f"/server/heartbeat?ip={invalid_ip}")
    assert response.status_code == 400
    assert response.json() == {"message": "invalid ip format"}


# 测试 send_nodes_list 路由
def test_send_nodes_list():
    setup_db()

    response = client.get("/server/send_nodes_list?count=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0] == "192.168.0.1"

    response = client.get("/server/send_nodes_list?count=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# 运行完测试后清理数据库
@pytest.fixture(autouse=True)
def run_around_tests():
    clear_db()
    yield
    clear_db()
