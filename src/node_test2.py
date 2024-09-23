#测试send_ip()函数
import os
import unittest
from unittest.mock import patch, Mock
import node  # 导入要测试的模块

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

if __name__ == "__main__":
    unittest.main()
#node.py中
#print("中心服务器返回节点ID为: ", id.text)即可看到测试代码返回的节点
