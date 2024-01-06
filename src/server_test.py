import unittest
import sqlite3
import os
from server import *


class TestServer(unittest.TestCase):
    def test_init_creates_table(self):
        # 执行初始化函数
        init_db()

        conn = sqlite3.connect("server.db")
        cursor = conn.cursor()
        # 检查表是否被正确创建
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
        )
        tables = cursor.fetchall()

        self.assertTrue(any("nodes" in table for table in tables))
        # 关闭数据库连接
        conn.close()
        os.remove("server.db")
        
        


if __name__ == "__main__":
    unittest.main()
