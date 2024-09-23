#测试init()函数
import unittest
from unittest.mock import patch, AsyncMock
import node

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
