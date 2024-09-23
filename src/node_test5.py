import pytest
import httpx
import respx
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from node import app, send_heartbeat_internal, Req

client = TestClient(app)
server_address = "http://60.204.236.38:8000/server"
ip = "127.0.0.1"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
@respx.mock
async def test_send_heartbeat_internal_success():
    # 模拟心跳请求
    heartbeat_route = respx.get(f"{server_address}/heartbeat?ip={ip}").mock(
        return_value=httpx.Response(200)
    )

    # 模拟 requests.get 以避免实际请求
    with patch("requests.get", return_value=httpx.Response(200)) as mock_get:
        # 模拟 asyncio.sleep 以避免实际延迟
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            task = asyncio.create_task(send_heartbeat_internal())
            await asyncio.sleep(0.1)  # 允许任务运行一段时间
            task.cancel()  # 取消任务以停止无限循环
            try:
                await task  # 确保任务被等待
            except asyncio.CancelledError:
                pass  # 捕获取消错误

    assert mock_get.called
    assert mock_get.call_count > 0

@pytest.mark.asyncio
@respx.mock
async def test_send_heartbeat_internal_failure():
    # 模拟心跳请求以引发异常
    heartbeat_route = respx.get(f"{server_address}/heartbeat?ip={ip}").mock(
        side_effect=httpx.RequestError("Central server error")
    )

    # 模拟 requests.get 以避免实际请求
    with patch("requests.get", side_effect=httpx.RequestError("Central server error")) as mock_get:
        # 模拟 asyncio.sleep 以避免实际延迟
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            task = asyncio.create_task(send_heartbeat_internal())
            await asyncio.sleep(0.1)  # 允许任务运行一段时间
            task.cancel()  # 取消任务以停止无限循环
            try:
                await task  # 确保任务被等待
            except asyncio.CancelledError:
                pass  # 捕获取消错误

    assert mock_get.called
    assert mock_get.call_count > 0

def test_user_src():
    # 模拟 ReEncrypt 函数
    with patch("node.ReEncrypt", return_value=(("a", "b", "c", "d"), b"encrypted_data")):
        # 模拟 send_user_des_message 函数
        with patch("node.send_user_des_message", new_callable=AsyncMock) as mock_send_user_des_message:
            message = {
                "source_ip": "127.0.0.1",
                "dest_ip": "127.0.0.2",
                "capsule": (("x1", "y1"), ("x2", "y2"), 123),
                "ct": 456,
                "rk": ["rk1", "rk2"]
            }
            response = client.post("/user_src", json=message)
            assert response.status_code == 200
            assert response.json() == {"detail": "message received"}
            mock_send_user_des_message.assert_called_once()

def test_send_user_des_message():
    with respx.mock:
        dest_ip = "127.0.0.2"
        re_message = (("a", "b", "c", "d"), 123)
        respx.post(f"http://{dest_ip}:8002/receive_messages").mock(
            return_value=httpx.Response(200, json={"status": "success"})
        )
        response = client.post(f"http://{dest_ip}:8002/receive_messages", json={"Tuple": re_message, "ip": "127.0.0.1"})
        assert response.status_code == 200
        assert response.json() == {"status": "success"}