import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from tpre import add, multiply, sm2p256v1
import time

# 生成元
g = (sm2p256v1.Gx, sm2p256v1.Gy)

start_time = time.time()  # 获取开始时间
for i in range(10):
    result = multiply(g, 10000, 1)  # 执行函数
end_time = time.time()  # 获取结束时间
elapsed_time = end_time - start_time  # 计算执行时间
print(f"rust multiply 执行时间: {elapsed_time:.6f} 秒")

start_time = time.time()  # 获取开始时间
for i in range(10):
    result = multiply(g, 10000, 0)  # 执行函数
end_time = time.time()  # 获取结束时间
elapsed_time = end_time - start_time  # 计算执行时间
print(f"python multiply 执行时间: {elapsed_time:.6f} 秒")

start_time = time.time()  # 获取开始时间
for i in range(10):
    result = add(g, g, 1)  # 执行函数
end_time = time.time()  # 获取结束时间
elapsed_time = end_time - start_time  # 计算执行时间
print(f"rust add 执行时间: {elapsed_time:.6f} 秒")

start_time = time.time()  # 获取开始时间
for i in range(10):
    result = add(g, g, 0)  # 执行函数
end_time = time.time()  # 获取结束时间
elapsed_time = end_time - start_time  # 计算执行时间
print(f"python add 执行时间: {elapsed_time:.6f} 秒")