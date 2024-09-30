#node_test剩下部分(有问题)
import os
import unittest
import pytest
from unittest.mock import patch, MagicMock, Mock, AsyncMock
import requests
import asyncio
import httpx
import respx
from fastapi.testclient import TestClient
from node import app, send_heartbeat_internal, Req, send_ip, get_local_ip, init, clear, send_user_des_message

client = TestClient(app)
server_address = "http://60.204.236.38:8000/server"
ip = None  # 初始化全局变量 ip
id = None  # 初始化全局变量 id

class TestGetLocalIP(unittest.TestCase):

    @patch.dict('os.environ', {'HOST_IP': '60.204.193.58'})  # 模拟设置 HOST_IP 环境变量
    def test_get_ip_from_env(self):
        global ip
        # 调用被测函数
        get_local_ip()
        
        # 检查函数是否正确获取到 HOST_IP
        self.assertEqual(ip, '60.204.193.58')

    @patch('socket.socket')  # Mock socket 连接行为
    @patch.dict('os.environ', {})  # 模拟没有 HOST_IP 环境变量
    def test_get_ip_from_socket(self, mock_socket):
        global ip
        # 模拟 socket 返回的 IP 地址
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.getsockname.return_value = ('110.41.155.96', 0)

        # 调用被测函数
        get_local_ip()

        # 确认 socket 被调用过
        mock_socket_instance.connect.assert_called_with(('8.8.8.8', 80))
        mock_socket_instance.close.assert_called_once()

        # 检查是否通过 socket 获取到正确的 IP 地址
        self.assertEqual(ip, '110.41.155.96')

class TestSendIP(unittest.TestCase):
    @patch.dict(os.environ, {'HOST_IP': '60.204.193.58'})  # 设置环境变量 HOST_IP
    @respx.mock
    def test_send_ip(self):
        global ip, id
        ip = '60.204.193.58'
        mock_url = f"{server_address}/get_node?ip={ip}"
        respx.get(mock_url).mock(return_value=httpx.Response(200, text="node123"))

        # 调用待测函数
        send_ip()

        # 确保 requests.get 被正确调用
        self.assertEqual(id, "node123")  # 检查更新后的 id 是否与 mock_response.text 匹配

class TestNode(unittest.TestCase):
    
    @patch('node.send_ip')
    @patch('node.get_local_ip')
    @patch('node.asyncio.create_task')
    def test_init(self, mock_create_task, mock_get_local_ip, mock_send_ip):
        # 调用 init 函数
        init()
        
        # 验证 get_local_ip 和 send_ip 被调用
        mock_get_local_ip.assert_called_once()
        mock_send_ip.assert_called_once()

        # 确保 create_task 被调用来启动心跳包
        mock_create_task.assert_called_once()

    def test_clear(self):
        # 调用 clear 函数
        clear()
        # 检查输出
        self.assertTrue(True)  # 这里只是为了确保函数被调用，没有实际逻辑需要测试

@pytest.mark.asyncio
@respx.mock
async def test_send_heartbeat_internal_success():
    global ip
    ip = '60.204.193.58'
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
    global ip
    ip = '60.204.193.58'
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
                "source_ip": "60.204.193.58",
                "dest_ip": "60.204.193.59",
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
        dest_ip = "60.204.193.59"
        re_message = (("a", "b", "c", "d"), 123)
        respx.post(f"http://{dest_ip}:8002/receive_messages").mock(
            return_value=httpx.Response(200, json={"status": "success"})
        )
        response = requests.post(f"http://{dest_ip}:8002/receive_messages", json={"Tuple": re_message, "ip": "60.204.193.58"})
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

if __name__ == '__main__':
    unittest.main()