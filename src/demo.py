from tpre import *

# 1
pk_a, sk_a = GenerateKeyPair()
m = b"hello world"

# 2
capsule_ct = Encrypt(pk_a, m)

# 3
pk_b, sk_b = GenerateKeyPair()

N = 5
T = 2

# 5
rekeys = GenerateReKey(sk_a, pk_b, N, T)

# 7
cfrag_cts = []

for rekey in rekeys:
    cfrag_ct = ReEncrypt(rekey, capsule_ct)
    cfrag_cts.append(cfrag_ct)

# 9
cfrags = mergecfrag(cfrag_cts)
m = DecryptFrags(sk_b, pk_b, pk_a, cfrags)

print(m)
