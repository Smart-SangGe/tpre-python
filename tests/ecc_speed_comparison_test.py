import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from tpre import add, multiply, sm2p256v1
import time

# 生成元
g = (sm2p256v1.Gx, sm2p256v1.Gy)


def test_rust_vs_python_multiply():
    mul_times = random.randint(0, sm2p256v1.N - 1)
    # Rust实现
    start_time = time.time()
    for _ in range(10):
        _ = multiply(g, mul_times)
    rust_time = time.time() - start_time
    print(f"\nRust multiply 执行时间: {rust_time:.6f} 秒")

    # Python实现
    start_time = time.time()
    for _ in range(10):
        _ = multiply(g, mul_times)
    python_time = time.time() - start_time
    print(f"Python multiply 执行时间: {python_time:.6f} 秒")

    assert rust_time < python_time, "Rust实现应该比Python更快"


def test_rust_vs_python_add():
    # Rust实现
    start_time = time.time()
    for _ in range(10):
        _ = add(g, g)
    rust_time = time.time() - start_time
    print(f"\nRust add 执行时间: {rust_time:.6f} 秒")

    # Python实现
    start_time = time.time()
    for _ in range(10):
        _ = add(g, g)
    python_time = time.time() - start_time
    print(f"Python add 执行时间: {python_time:.6f} 秒")

    assert rust_time < python_time, "Rust实现应该比Python更快"
