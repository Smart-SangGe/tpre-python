import sys
import os
import time


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from tpre import (
    GenerateKeyPair,
    Encrypt,
    GenerateReKey,
    ReEncrypt,
    MergeCFrag,
    DecryptFrags,
)


def test_tpre_full_workflow_speed():
    """测试TPRE完整工作流程的运行速度"""
    N = 20
    T = N // 2
    print(f"当前门限值: N = {N}, T = {T}")
    total_time = 0

    # 1. 密钥生成
    start_time = time.time()
    pk_a, sk_a = GenerateKeyPair()
    m = b"hello world"
    end_time = time.time()
    elapsed_time = end_time - start_time
    total_time += elapsed_time
    print(f"密钥生成运行时间:{elapsed_time}秒")

    # 2. 加密
    start_time = time.time()
    capsule_ct = Encrypt(pk_a, m)
    end_time = time.time()
    elapsed_time = end_time - start_time
    total_time += elapsed_time
    print(f"加密算法运行时间:{elapsed_time}秒")

    # 3. 接收方密钥生成
    pk_b, sk_b = GenerateKeyPair()

    # 4. 重加密密钥生成
    start_time = time.time()
    id_tuple = tuple(range(N))
    rekeys = GenerateReKey(sk_a, pk_b, N, T, id_tuple)
    end_time = time.time()
    elapsed_time = end_time - start_time
    total_time += elapsed_time
    print(f"重加密密钥生成算法运行时间:{elapsed_time}秒")

    # 5. 重加密
    start_time = time.time()
    cfrag_cts = []
    for rekey in rekeys:
        cfrag_ct = ReEncrypt(rekey, capsule_ct)
        cfrag_cts.append(cfrag_ct)
    end_time = time.time()
    elapsed_time = (end_time - start_time) / len(rekeys)
    total_time += elapsed_time
    print(f"重加密算法运行时间:{elapsed_time}秒")

    # 6. 合并和解密
    start_time = time.time()
    cfrags = MergeCFrag(cfrag_cts)
    decrypted_m = DecryptFrags(sk_b, pk_b, pk_a, cfrags)
    end_time = time.time()
    elapsed_time = end_time - start_time
    total_time += elapsed_time
    print(f"解密算法运行时间:{elapsed_time}秒")

    # 验证解密结果
    assert decrypted_m == m, "解密结果与原始消息不匹配"
    print(f"成功解密: {decrypted_m}")
