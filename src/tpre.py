from gmssl import *  # pylint: disable = e0401
from typing import Tuple, Callable
import random
import traceback

point = Tuple[int, int]
capsule = Tuple[point, point, int]


# 生成密钥对模块
class CurveFp:
    def __init__(self, A, B, P, N, Gx, Gy, name):
        self.A = A
        self.B = B
        self.P = P
        self.N = N
        self.Gx = Gx
        self.Gy = Gy
        self.name = name


sm2p256v1 = CurveFp(
    name="sm2p256v1",
    A=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC,
    B=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93,
    P=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF,
    N=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123,
    Gx=0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
    Gy=0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0,
)

point = Tuple[int, int]

# 生成元
g = (sm2p256v1.Gx, sm2p256v1.Gy)


def multiply(a: point, n: int) -> point:
    N = sm2p256v1.N
    A = sm2p256v1.A
    P = sm2p256v1.P
    return fromJacobian(jacobianMultiply(toJacobian(a), n, N, A, P), P)


def add(a: point, b: point) -> point:
    A = sm2p256v1.A
    P = sm2p256v1.P
    return fromJacobian(jacobianAdd(toJacobian(a), toJacobian(b), A, P), P)


def inv(a: int, n: int) -> int:
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n


def toJacobian(Xp_Yp: point) -> Tuple[int, int, int]:
    Xp, Yp = Xp_Yp
    return (Xp, Yp, 1)


def fromJacobian(Xp_Yp_Zp: Tuple[int, int, int], P: int) -> point:
    Xp, Yp, Zp = Xp_Yp_Zp
    z = inv(Zp, P)
    return ((Xp * z**2) % P, (Yp * z**3) % P)


def jacobianDouble(
    Xp_Yp_Zp: Tuple[int, int, int], A: int, P: int
) -> Tuple[int, int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    if not Yp:
        return (0, 0, 0)
    ysq = (Yp**2) % P
    S = (4 * Xp * ysq) % P
    M = (3 * Xp**2 + A * Zp**4) % P
    nx = (M**2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq**2) % P
    nz = (2 * Yp * Zp) % P
    return (nx, ny, nz)


def jacobianAdd(
    Xp_Yp_Zp: Tuple[int, int, int], Xq_Yq_Zq: Tuple[int, int, int], A: int, P: int
) -> Tuple[int, int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    Xq, Yq, Zq = Xq_Yq_Zq
    if not Yp:
        return (Xq, Yq, Zq)
    if not Yq:
        return (Xp, Yp, Zp)
    U1 = (Xp * Zq**2) % P
    U2 = (Xq * Zp**2) % P
    S1 = (Yp * Zq**3) % P
    S2 = (Yq * Zp**3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobianDouble((Xp, Yp, Zp), A, P)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R**2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * Zp * Zq) % P
    return (nx, ny, nz)


def jacobianMultiply(
    Xp_Yp_Zp: Tuple[int, int, int], n: int, N: int, A: int, P: int
) -> Tuple[int, int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    if Yp == 0 or n == 0:
        return (0, 0, 1)
    if n == 1:
        return (Xp, Yp, Zp)
    if n < 0 or n >= N:
        return jacobianMultiply((Xp, Yp, Zp), n % N, N, A, P)
    if (n % 2) == 0:
        return jacobianDouble(jacobianMultiply((Xp, Yp, Zp), n // 2, N, A, P), A, P)
    if (n % 2) == 1:
        return jacobianAdd(
            jacobianDouble(jacobianMultiply((Xp, Yp, Zp), n // 2, N, A, P), A, P),
            (Xp, Yp, Zp),
            A,
            P,
        )
    raise ValueError("jacobian Multiply error")


# 生成元
U = multiply(g, random.randint(0, sm2p256v1.N - 1))


def hash2(double_G: Tuple[point, point]) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    for i in double_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, "big") % sm2p256v1.N
    return digest


def hash3(triple_G: Tuple[point, point, point]) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    for i in triple_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, "big") % sm2p256v1.N
    return digest


def hash4(triple_G: Tuple[point, point, point], Zp: int) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    for i in triple_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    sm3.update(Zp.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, "big") % sm2p256v1.N
    return digest


def KDF(G: point) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    for i in G:
        sm3.update(i.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, "big") % sm2p256v1.N
    mask_128bit = (1 << 128) - 1
    digest = digest & mask_128bit
    return digest


def GenerateKeyPair() -> Tuple[point, int]:
    """
    return:
    public_key, secret_key
    """
    sm2 = Sm2Key()  # pylint: disable=e0602
    sm2.generate_key()

    public_key_x = int.from_bytes(bytes(sm2.public_key.x), "big")
    public_key_y = int.from_bytes(bytes(sm2.public_key.y), "big")
    public_key = (public_key_x, public_key_y)

    secret_key = int.from_bytes(bytes(sm2.private_key), "big")

    return public_key, secret_key


def Encrypt(pk: point, m: bytes) -> Tuple[capsule, bytes]:
    enca = Encapsulate(pk)
    K = enca[0].to_bytes(16)
    capsule = enca[1]
    if len(K) != 16:
        raise ValueError("invalid key length")
    iv = b"tpretpretpretpre"
    sm4_enc = Sm4Cbc(K, iv, DO_ENCRYPT)  # pylint: disable=e0602
    enc_Data = sm4_enc.update(m)
    enc_Data += sm4_enc.finish()
    enc_message = (capsule, enc_Data)
    return enc_message


def Decapsulate(ska: int, capsule: capsule) -> int:
    E, V, s = capsule
    EVa = multiply(add(E, V), ska)  # (E*V)^ska
    K = KDF(EVa)

    return K


def Decrypt(sk_A: int, C: Tuple[capsule, bytes]) -> bytes:
    """
    params:
    sk_A: secret key
    C: (capsule, enc_data)
    """
    capsule, enc_Data = C
    K = Decapsulate(sk_A, capsule)
    iv = b"tpretpretpretpre"
    sm4_dec = Sm4Cbc(K, iv, DO_DECRYPT)  # pylint: disable= e0602
    dec_Data = sm4_dec.update(enc_Data)
    dec_Data += sm4_dec.finish()
    return dec_Data


# GenerateRekey
def hash5(id: int, D: int) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    sm3.update(id.to_bytes(32))
    sm3.update(D.to_bytes(32))
    hash = sm3.digest()
    hash = int.from_bytes(hash, "big") % sm2p256v1.N
    return hash


def hash6(triple_G: Tuple[point, point, point]) -> int:
    sm3 = Sm3()  # pylint: disable=e0602
    for i in triple_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    hash = sm3.digest()
    hash = int.from_bytes(hash, "big") % sm2p256v1.N
    return hash


def f(x: int, f_modulus: list, T: int) -> int:
    """
    功能: 通过多项式插值来实现信息的分散和重构
    例如: 随机生成一个多项式f(x)=4x+5,质数P=11,其中f(0)=5,将多项式的系数分别分配给两个人,例如第一个人得到(1, 9),第二个人得到(2, 2).如果两个人都收集到了这两个点,那么可以使用拉格朗日插值法恢复原始的多项式,进而得到秘密信息"5"
    param:
    x, f_modulus(多项式系数列表), T(门限)
    return:
    res
    """
    res = 0
    for i in range(T):
        res += f_modulus[i] * pow(x, i)
    res = res % sm2p256v1.N
    return res


def GenerateReKey(sk_A: int, pk_B: point, N: int, T: int, id_tuple: Tuple[int,...]) -> list:
    """
    param:
    skA, pkB, N(节点总数), T(阈值)
    return:
    rki(0 <= i <= N-1)
    """
    # 计算临时密钥对(x_A, X_A)
    x_A = random.randint(0, sm2p256v1.N - 1)
    X_A = multiply(g, x_A)

    pk_A = multiply(g, sk_A)

    # d是Bob的密钥对与临时密钥对的非交互式Diffie-Hellman密钥交换的结果
    d = hash3((X_A, pk_B, multiply(pk_B, x_A)))

    # 计算多项式系数
    f_modulus = []
    # 计算f0
    # f0 = (sk_A * inv(d, G.P)) % G.P
    f0 = (sk_A * inv(d, sm2p256v1.N)) % sm2p256v1.N
    f_modulus.append(f0)
    # 计算fi(1 <= i <= T - 1)
    for i in range(1, T):
        f_modulus.append(random.randint(0, sm2p256v1.N - 1))

    # 计算D
    D = hash6((pk_A, pk_B, multiply(pk_B, sk_A)))
    # 计算KF
    KF = []
    for i in range(N):
        y = random.randint(0, sm2p256v1.N - 1)
        Y = multiply(g, y)
        s_x = hash5(id_tuple[i], D)  # id需要设置
        r_k = f(s_x, f_modulus, T)
        U1 = multiply(U, r_k)
        kFrag = (id_tuple[i], r_k, X_A, U1)
        KF.append(kFrag)

    return KF


def Encapsulate(pk_A: point) -> Tuple[int, capsule]:
    r = random.randint(0, sm2p256v1.N - 1)
    u = random.randint(0, sm2p256v1.N - 1)
    E = multiply(g, r)
    V = multiply(g, u)
    s = (u + r * hash2((E, V))) % sm2p256v1.N
    pk_A_ru = multiply(pk_A, r + u)
    K = KDF(pk_A_ru)
    capsule = (E, V, s)
    return (K, capsule)


def Checkcapsule(capsule: capsule) -> bool:  # 验证胶囊的有效性
    E, V, s = capsule
    h2 = hash2((E, V))
    g = (sm2p256v1.Gx, sm2p256v1.Gy)
    result1 = multiply(g, s)
    temp = multiply(E, h2)  # 中间变量
    result2 = add(V, temp)  #  result2=V*E^H2(E,V)
    if result1 == result2:
        flag = True
    else:
        flag = False

    return flag


def ReEncapsulate(kFrag: tuple, capsule: capsule) -> Tuple[point, point, int, point]:
    id, rk, Xa, U1 = kFrag
    E, V, s = capsule
    if not Checkcapsule(capsule):
        raise ValueError("Invalid capsule")
    E1 = multiply(E, rk)
    V1 = multiply(V, rk)
    cfrag = E1, V1, id, Xa
    return cfrag  #  cfrag=(E1,V1,id,Xa)   E1= E^rk  V1=V^rk

    # 重加密函数


def ReEncrypt(
    kFrag: tuple, C: Tuple[capsule, bytes]
) -> Tuple[Tuple[point, point, int, point], bytes]:
    capsule, enc_Data = C

    cFrag = ReEncapsulate(kFrag, capsule)
    return (cFrag, enc_Data)  # 输出密文


# capsule, enc_Data = C


# 将加密节点加密后产生的t个（capsule,ct）合并在一起,产生cfrags = {{capsule1,capsule2,...},ct}
def mergecfrag(cfrag_cts: list) -> list:
    ct_list = []
    cfrags_list = []
    cfrags = []
    for cfrag_ct in cfrag_cts:
        cfrags_list.append(cfrag_ct[0])
        ct_list.append(cfrag_ct[1])
    cfrags.append(cfrags_list)
    cfrags.append(ct_list[0])
    return cfrags


def DecapsulateFrags(sk_B: int, pk_B: point, pk_A: point, cFrags: list) -> int:
    """
    return:
    K: sm4 key
    """

    Elist = []
    Vlist = []
    idlist = []
    X_Alist = []
    for cfrag in cFrags:  # Ei,Vi,id,Xa = cFrag
        Elist.append(cfrag[0])
        Vlist.append(cfrag[1])
        idlist.append(cfrag[2])
        X_Alist.append(cfrag[3])

    pkab = multiply(pk_A, sk_B)  # pka^b
    D = hash6((pk_A, pk_B, pkab))
    Sx = []
    for id in idlist:  #  从1到t
        sxi = hash5(id, D)  #  id 节点的编号
        Sx.append(sxi)
    bis = []  #  b ==> λ
    bi = 1
    for i in range(len(cFrags)):
        bi = 1
        for j in range(len(cFrags)):
            if j != i:
                Sxj_sub_Sxi = (Sx[j] - Sx[i]) % sm2p256v1.N
                Sxj_sub_Sxi_inv = inv(Sxj_sub_Sxi, sm2p256v1.N)
                bi = (bi * Sx[j] * Sxj_sub_Sxi_inv) % sm2p256v1.N
        bis.append(bi)

    E2 = multiply(Elist[0], bis[0])  #  E^  便于计算
    V2 = multiply(Vlist[0], bis[0])  #  V^
    for k in range(1, len(cFrags)):
        Ek = multiply(Elist[k], bis[k])  # EK/Vk 是个列表
        Vk = multiply(Vlist[k], bis[k])
        E2 = add(Ek, E2)
        V2 = add(Vk, V2)
    X_Ab = multiply(X_Alist[0], sk_B)  # X_A^b   X_A 的值是随机生成的xa,通过椭圆曲线上的倍点运算生成的固定的值
    d = hash3((X_Alist[0], pk_B, X_Ab))
    EV = add(E2, V2)  # E2 + V2
    EVd = multiply(EV, d)  # (E2 + V2)^d
    K = KDF(EVd)

    return K


#  M = IAEAM(K,enc_Data)


# cfrags = {{capsule1,capsule2,...},ct} ,ct->en_Data
def DecryptFrags(sk_B: int, pk_B: point, pk_A: point, cfrags: list) -> bytes:
    capsules, enc_Data = cfrags  # 加密后的密文
    K = DecapsulateFrags(sk_B, pk_B, pk_A, capsules)
    K = K.to_bytes(16)
    iv = b"tpretpretpretpre"
    sm4_dec = Sm4Cbc(K, iv, DO_DECRYPT)  # pylint: disable= e0602
    try:
        dec_Data = sm4_dec.update(enc_Data)
        dec_Data += sm4_dec.finish()
    except Exception as e:
        print(e)
        print("key error")
        dec_Data = b""
    return dec_Data
