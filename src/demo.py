from tpre import *
import time

# 1
start_time = time.time()
pk_a, sk_a = GenerateKeyPair()
m = b"hello world"
end_time = time.time()
elapsed_time = end_time - start_time
print(f"代码块1运行时间:{elapsed_time}秒")

# 2
start_time = time.time()
capsule_ct = Encrypt(pk_a, m)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"代码块2运行时间:{elapsed_time}秒")

# 3
pk_b, sk_b = GenerateKeyPair()

N = 10
T = 5

# 5
start_time = time.time()
rekeys = GenerateReKey(sk_a, pk_b, N, T)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"代码块5运行时间:{elapsed_time}秒")

# 7
start_time = time.time()
cfrag_cts = []

for rekey in rekeys:
    cfrag_ct = ReEncrypt(rekey, capsule_ct)
    cfrag_cts.append(cfrag_ct)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"代码块7运行时间:{elapsed_time}秒")

# 9
start_time = time.time()
cfrags = mergecfrag(cfrag_cts)
m = DecryptFrags(sk_b, pk_b, pk_a, cfrags)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"代码块9运行时间:{elapsed_time}秒")
print(m)
