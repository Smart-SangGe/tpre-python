# 测试 node.py 中的函数
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
import node

class TestGetLocalIP(unittest.TestCase):

    @patch.dict('os.environ', {'HOST_IP': '60.204.193.58'})  # 模拟设置 HOST_IP 环境变量
    def test_get_ip_from_env(self):
        # 调用被测函数
        node.get_local_ip()
        
        # 检查函数是否正确获取到 HOST_IP
        self.assertEqual(node.ip, '60.204.193.58')

    @patch('socket.socket')  # Mock socket 连接行为
    @patch.dict('os.environ', {})  # 模拟没有 HOST_IP 环境变量
    def test_get_ip_from_socket(self, mock_socket):
        # 模拟 socket 返回的 IP 地址
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.getsockname.return_value = ('110.41.155.96', 0)

        # 调用被测函数
        node.get_local_ip()

        # 确认 socket 被调用过
        mock_socket_instance.connect.assert_called_with(('8.8.8.8', 80))
        mock_socket_instance.close.assert_called_once()

        # 检查是否通过 socket 获取到正确的 IP 地址
        self.assertEqual(node.ip, '110.41.155.96')

class TestSendIP(unittest.TestCase):
    @patch.dict(os.environ, {'HOST_IP': '60.204.193.58'})  # 设置环境变量 HOST_IP
    @patch('requests.get')  # Mock requests.get 调用
    def test_send_ip(self, mock_get):
        # 设置模拟返回的 HTTP 响应
        mock_response = Mock()
        mock_response.text = "node123"  # 模拟返回的节点ID
        mock_response.status_code = 200
        mock_get.return_value = mock_response  # 设置 requests.get() 的返回值为 mock_response

        # 保存原始的全局 id 值
        original_id = node.id

        # 调用待测函数
        node.send_ip()

        # 确保 requests.get 被正确调用
        expected_url = f"{node.server_address}/get_node?ip={node.ip}"
        mock_get.assert_called_once_with(expected_url, timeout=3)

        # 检查 id 是否被正确更新
        self.assertIs(node.id, mock_response)  # 检查 id 是否被修改
        self.assertEqual(node.id.text, "node123")  # 检查更新后的 id 是否与 mock_response.text 匹配

class TestNode(unittest.TestCase):
    
    @patch('node.send_ip')
    @patch('node.get_local_ip')
    @patch('node.asyncio.create_task')
    def test_init(self, mock_create_task, mock_get_local_ip, mock_send_ip):
        # 调用 init 函数
        node.init()
        
        # 验证 get_local_ip 和 send_ip 被调用
        mock_get_local_ip.assert_called_once()
        mock_send_ip.assert_called_once()

        # 确保 create_task 被调用来启动心跳包
        mock_create_task.assert_called_once()

if __name__ == '__main__':
    unittest.main()