#测试 get_local_ip()函数
import unittest
from unittest.mock import patch, MagicMock
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

if __name__ == '__main__':
    unittest.main()
