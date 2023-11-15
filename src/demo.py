from tpre import *
import time

# for T in range(2, 20, 2):
N = 10
T = N // 2
# print(f"当前门限值: N = {N}, T = {T}")

start_total_time = time.time()
# 1
start_time = time.time()
pk_a, sk_a = GenerateKeyPair()
# print("pk_a: ", pk_a)
# print("sk_a: ", sk_a)
end_time = time.time()
elapsed_time = end_time - start_time
# print(f"密钥生成运行时间:{elapsed_time}秒")

# 2
start_time = time.time()
m = b"hello world"
capsule_ct = Encrypt(pk_a, m)
capsule = capsule_ct[0]
print("check capsule: ", Checkcapsule(capsule))
capsule = (capsule[0], capsule[1], -1)
print("check capsule: ", Checkcapsule(capsule))
# print("capsule_ct: ", capsule_ct)
end_time = time.time()
elapsed_time = end_time - start_time
# print(f"加密算法运行时间:{elapsed_time}秒")

# 3
pk_b, sk_b = GenerateKeyPair()

# 5
start_time = time.time()
id_tuple = tuple(range(N))
rekeys = GenerateReKey(sk_a, pk_b, N, T, id_tuple)
# print("rekeys: ", rekeys)
end_time = time.time()
elapsed_time = end_time - start_time
# print(f"重加密密钥生成算法运行时间:{elapsed_time}秒")

# 7
start_time = time.time()
cfrag_cts = []

for rekey in rekeys:
    cfrag_ct = ReEncrypt(rekey, capsule_ct)
    # cfrag_ct = ReEncrypt(rekeys[0], capsule_ct)
    cfrag_cts.append(cfrag_ct)
# print("cfrag_cts: ", cfrag_cts)
end_time = time.time()
re_elapsed_time = (end_time - start_time) / len(rekeys)
# print(f"重加密算法运行时间:{re_elapsed_time}秒")

# 9
start_time = time.time()
cfrags = mergecfrag(cfrag_cts)
# print("cfrags: ", cfrags)
# m = DecryptFrags(sk_b, pk_b, pk_a, cfrags)
m = DecryptFrags(sk_a, pk_b, pk_a, cfrags)
# print("m = ", m)
end_time = time.time()
elapsed_time = end_time - start_time
end_total_time = time.time()
total_time = end_total_time - start_total_time - re_elapsed_time * len(rekeys)
# print(f"解密算法运行时间:{elapsed_time}秒")
# print("成功解密:", m)
# print(f"算法总运行时间:{total_time}秒")
# print()
