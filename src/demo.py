from tpre import *

# 1
pk_a, sk_a = GenerateKeyPair(1, ())
m = b'hello world'
m = int.from_bytes(m)

# 2
capsule_ct = Encrypt(pk_a, m)

# 3
pk_b, sk_b = GenerateKeyPair(1, ())

N = 20
T = 10

# 5
rekeys =  GenerateReKey(sk_a, pk_b, N, T)

# 7
cfrag_cts = []

for rekey in rekeys:
    cfrag_ct = ReEncrypt(rekey, capsule_ct)
    cfrag_cts.append(cfrag_ct)
    
# 9
cfrags = mergecfrag(cfrag_cts)
m = DecryptFrags(sk_b, pk_b, pk_a, cfrags)


