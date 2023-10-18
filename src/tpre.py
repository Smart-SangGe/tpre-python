from gmssl import * #pylint: disable = e0401 
from typing import Tuple, Callable
import random

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
    Gy=0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
)

# 椭圆曲线
G = sm2p256v1

# 生成元
g = (sm2p256v1.Gx, sm2p256v1.Gy)

def multiply(a: Tuple[int, int], n: int) -> Tuple[int, int]:
    N = sm2p256v1.N
    A = sm2p256v1.A
    P = sm2p256v1.P 
    return fromJacobian(jacobianMultiply(toJacobian(a), n, N, A, P), P)

def add(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
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
 
def toJacobian(Xp_Yp: Tuple[int, int]) -> Tuple[int, int, int]:
    Xp, Yp = Xp_Yp
    return (Xp, Yp, 1)

def fromJacobian(Xp_Yp_Zp: Tuple[int, int, int], P: int) -> Tuple[int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    z = inv(Zp, P)
    return ((Xp * z ** 2) % P, (Yp * z ** 3) % P)
 
def jacobianDouble(Xp_Yp_Zp: Tuple[int, int, int], A: int, P: int) -> Tuple[int, int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    if not Yp:
        return (0, 0, 0)
    ysq = (Yp ** 2) % P
    S = (4 * Xp * ysq) % P
    M = (3 * Xp ** 2 + A * Zp ** 4) % P
    nx = (M ** 2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq ** 2) % P
    nz = (2 * Yp * Zp) % P
    return (nx, ny, nz)
 
def jacobianAdd(
    Xp_Yp_Zp: Tuple[int, int, int], 
    Xq_Yq_Zq: Tuple[int, int, int], 
    A: int, 
    P: int
) -> Tuple[int, int, int]:
    Xp, Yp, Zp = Xp_Yp_Zp
    Xq, Yq, Zq = Xq_Yq_Zq
    if not Yp:
        return (Xq, Yq, Zq)
    if not Yq:
        return (Xp, Yp, Zp)
    U1 = (Xp * Zq ** 2) % P
    U2 = (Xq * Zp ** 2) % P
    S1 = (Yp * Zq ** 3) % P
    S2 = (Yq * Zp ** 3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobianDouble((Xp, Yp, Zp), A, P)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R ** 2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * Zp * Zq) % P
    return (nx, ny, nz)
 
def jacobianMultiply(
    Xp_Yp_Zp: Tuple[int, int, int], 
    n: int, 
    N: int, 
    A: int, 
    P: int
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
        return jacobianAdd(jacobianDouble(jacobianMultiply((Xp, Yp, Zp), n // 2, N, A, P), A, P), (Xp, Yp, Zp), A, P)
    raise ValueError("jacobian Multiply error")

# 生成元    
U = multiply(g, random.randint(0, sm2p256v1.P))

# def Setup(sec: int) -> Tuple[CurveFp, Tuple[int, int], 
#                              Tuple[int, int]]:
#     '''
#     params:
#     sec: an init safety param
    
#     return:
#     G: sm2 curve
#     g: generator
#     U: another generator
#     '''
    
#     G = sm2p256v1
    
#     g = (sm2p256v1.Gx, sm2p256v1.Gy)
    
#     tmp_u = random.randint(0, sm2p256v1.P)
#     U = multiply(g, tmp_u)
    
#     return G, g, U

def hash2(double_G: Tuple[Tuple[int, int], Tuple[int, int]]) -> int:
    sm3 = Sm3() #pylint: disable=e0602
    for i in double_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest,'big') % sm2p256v1.P
    return digest

def hash3(triple_G: Tuple[Tuple[int, int], 
                            Tuple[int, int],
                            Tuple[int, int]]) -> int:
    sm3 = Sm3() #pylint: disable=e0602
    for i in triple_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, 'big') % sm2p256v1.P
    return digest

def hash4(triple_G: Tuple[Tuple[int, int],
                            Tuple[int, int],
                            Tuple[int, int]],
            Zp: int) -> int:
    sm3 = Sm3() #pylint: disable=e0602
    for i in triple_G:
        for j in i:
            sm3.update(j.to_bytes(32))
    sm3.update(Zp.to_bytes(32))
    digest = sm3.digest()
    digest = int.from_bytes(digest, 'big') % sm2p256v1.P
    return digest

def KDF(G: Tuple[int, int]) -> int:
    sm3 = Sm3() #pylint: disable=e0602
    for i in G:
        sm3.update(i.to_bytes(32))
    digest = sm3.digest(32)
    digest = digest
    digest = int.from_bytes(digest, 'big') % sm2p256v1.P
    return digest

def GenerateKeyPair(
    lamda_parma: int, 
    public_params: tuple
    ) -> Tuple[Tuple[int, int], int]:
    '''
    params: 
    lamda_param: an init safety param 
    public_params: curve params
    
    return:
    public_key, secret_key
    '''
    sm2 = Sm2Key() #pylint: disable=e0602
    sm2.generate_key()
    
    public_key_x = int.from_bytes(bytes(sm2.public_key.x),"big")
    public_key_y = int.from_bytes(bytes(sm2.public_key.y),"big")
    public_key = (public_key_x, public_key_y)
      
    
    secret_key = int.from_bytes(bytes(sm2.private_key),"big")
    
    return public_key, secret_key

# 生成A和B的公钥和私钥
pk_A, sk_A = GenerateKeyPair(0, ())
pk_B, sk_B = GenerateKeyPair(0, ())

def Encrypt(pk: Tuple[int, int], m: int) -> Tuple[Tuple[
    Tuple[int, int],Tuple[int, int], int], int]:
    enca = Encapsulate(pk)
    K = enca[0].to_bytes()
    capsule = enca[1]
    if len(K) != 16:
        raise ValueError("invalid key length")
    iv = b'tpretpretpretpre'
    sm4_enc = Sm4Cbc(K, iv, DO_ENCRYPT) #pylint: disable=e0602
    plain_Data = m.to_bytes(32)
    enc_Data = sm4_enc.update(plain_Data)
    enc_Data += sm4_enc.finish()
    enc_message = (capsule, enc_Data)
    return enc_message

def Decapsulate(ska:int,capsule:Tuple[Tuple[int,int],Tuple[int,int],int]) -> int:
    E,V,s = capsule
    EVa=multiply(add(E,V), ska)    # (E*V)^ska
    K = KDF(EVa)

    return K

def Decrypt(sk_A: int,C:Tuple[Tuple[
    Tuple[int, int],Tuple[int, int], int], int]) ->int:
    '''
    params:
    sk_A: secret key
    C: (capsule, enc_data) 
    '''
    capsule,enc_Data = C
    K = Decapsulate(sk_A,capsule)
    iv = b'tpretpretpretpre'
    sm4_dec = Sm4Cbc(K, iv, DO_DECRYPT) #pylint: disable= e0602
    dec_Data = sm4_dec.update(enc_Data)
    dec_Data += sm4_dec.finish()
    return dec_Data

# GenerateRekey
def H5(id: int, D: int) -> int:
    sm3 = Sm3() #pylint: disable=e0602
    sm3.update(id.to_bytes(32))
    sm3.update(D.to_bytes(32))
    hash = sm3.digest()
    hash = int.from_bytes(hash,'big') % G.P
    return hash

def H6(triple_G: Tuple[Tuple[int, int], 
                              Tuple[int, int],
                              Tuple[int, int]]) -> int:
        sm3 = Sm3() #pylint: disable=e0602
        for i in triple_G:
            for j in i:
                sm3.update(j.to_bytes(32))
        hash = sm3.digest()
        hash = int.from_bytes(hash,'big') % G.P
        return hash

def f(x: int, f_modulus: list, T: int) -> int:
    '''
    功能: 通过多项式插值来实现信息的分散和重构
    例如: 随机生成一个多项式f(x)=4x+5,质数P=11,其中f(0)=5,将多项式的系数分别分配给两个人,例如第一个人得到(1, 9),第二个人得到(2, 2).如果两个人都收集到了这两个点,那么可以使用拉格朗日插值法恢复原始的多项式,进而得到秘密信息"5"
    param:
    x, f_modulus(多项式系数列表), T(门限)
    return:
    res
    '''
    res = 0
    for i in range(T):
        res += f_modulus[i] * pow(x, i)
    res = res % sm2p256v1.P
    return res

def GenerateReKey(sk_A, pk_B, N: int, T: int) -> list:
    '''
    param: 
    skA, pkB, N(节点总数), T(阈值)
    return: 
    rki(0 <= i <= N-1)
    '''
    # 计算临时密钥对(x_A, X_A)
    x_A = random.randint(0, G.P - 1)
    X_A = multiply(g, x_A)                

    # d是Bob的密钥对与临时密钥对的非交互式Diffie-Hellman密钥交换的结果
    d = hash3((X_A, pk_B, multiply(pk_B, x_A)))   
    
    # 计算多项式系数, 确定代理节点的ID(一个点)
    f_modulus = []
    # 计算f0
    f0 = (sk_A * inv(d, G.P)) % G.P
    f_modulus.append(f0)
    # 计算fi(1 <= i <= T - 1)
    for i in range(1, T):
        f_modulus.append(random.randint(0, G.P - 1))

    # 计算D
    D = H6((X_A, pk_B, multiply(pk_B, sk_A)))

    # 计算KF
    KF = []
    for i in range(N):
        y = random.randint(0, G.P - 1)
        Y = multiply(g, y)
        s_x = H5(i, D)         # id需要设置
        r_k = f(s_x, f_modulus, T)
        U1 = multiply(U, r_k)   
        kFrag = (i, r_k, X_A, U1)
        KF.append(kFrag)

    return KF

def Encapsulate(pk_A: Tuple[int, int]) -> Tuple[int, Tuple[Tuple[int, int], Tuple[int, int], int]]:
    r = random.randint(0, G.P - 1)
    u = random.randint(0, G.P - 1)
    E = multiply(g, r)
    V = multiply(g, u)
    s = u + r * hash2((E, V))
    s = s % sm2p256v1.P
    pk_A_ru = multiply(pk_A, r + u)
    K = KDF(pk_A_ru)
    capsule = (E, V, s)
    return (K, capsule)

def Checkcapsule(capsule:Tuple[Tuple[int,int],Tuple[int,int],int]) -> bool:  # 验证胶囊的有效性
    E,V,s = capsule
    h2 = hash2((E,V))
    g = (sm2p256v1.Gx, sm2p256v1.Gy)
    result1 = multiply(g,s)
    temp = multiply(E,h2)   # 中间变量
    result2 =add(V,temp)   #  result2=V*E^H2(E,V)
    if result1 == result2:
        flag =True
    else:
        flag = False
        
    return flag 

def ReEncapsulate(kFrag:list,capsule:Tuple[Tuple[int,int],Tuple[int,int],int]) -> Tuple[Tuple[int,int],Tuple[int,int],int,Tuple[int,int]] :
    id,rk,Xa,U1 = kFrag
    E,V,s = capsule
    if not Checkcapsule(capsule):
        raise ValueError('Invalid capsule')
    flag = Checkcapsule(capsule)
    assert flag == True    # 断言，判断胶囊capsule的有效性
    E1 = multiply(E,rk)
    V1 = multiply(V,rk)
    cfrag = E1,V1,id,Xa
    return cfrag   #  cfrag=(E1,V1,id,Xa)   E1= E^rk  V1=V^rk 
    
    # 重加密函数
def ReEncrypt(kFrag:list,
              C:Tuple[Tuple[Tuple[int,int],Tuple[int,int],int],int])->Tuple[Tuple[Tuple[int,int],Tuple[int,int],int,Tuple[int,int]],int] :
    capsule,enc_Data = C

    cFrag = ReEncapsulate(kFrag,capsule)
    return (cFrag,enc_Data)    # 输出密文
# capsule, enc_Data = C


# N 是加密节点的数量，t是阈值
def mergecfrag(N:int,t:int)->tuple[Tuple[Tuple[int,int],Tuple[int,int]
                              ,int,Tuple[int,int]], ...]:
    cfrags = ()
    kfrags = GenerateReKey(sk_A,pk_B,N,t)
    result  = Encapsulate(pk_A)
    K,capsule = result  
    for kfrag in kfrags:
        cfrag = ReEncapsulate(kfrag,capsule)
        cfrags = cfrags + (cfrag,)
    
    return cfrags

    

def DecapsulateFrags(sk_B:int,pk_A:Tuple[int,int],cFrags:Tuple[Tuple[Tuple[int,int],Tuple[int,int],int,Tuple[int,int]]]
                  ,capsule:Tuple[Tuple[int,int],Tuple[int,int],int]) -> int:
    '''
    return:
    K: sm4 key
    '''
    Elist = []
    Vlist = []
    idlist = []
    X_Alist = []
    t = 0
    for cfrag in cFrags:   # Ei,Vi,id,Xa = cFrag
        Elist.append(cfrag[0])
        Vlist.append(cfrag[1])
        idlist.append(cfrag[2])
        X_Alist.append(cfrag[3])
        t = t+1        # 总共有t个片段，t为阈值
  
    pkab = multiply(pk_A,sk_B)     # pka^b
    D = H6((pk_A,pk_B,pkab))
    Sx = []
    for id in idlist:        #  从1到t
        sxi = H5(id,D)       #  id 节点的编号
        Sx.append(sxi)    
    bis= []    #  b ==> λ
    j = 1
    i = 1
    bi =1
    for i in range(t):
        for j in range(t):
            if j == i:
                j=j+1
            else:
                bi = bi * (Sx[j]//(Sx[j]-Sx[i]))    # 暂定整除
        bis.append(bi)

    E2=multiply(Elist[0],bis[0])             #  E^  便于计算
    V2=multiply(Vlist[0],bis[0])             #  V^
    for k in range(1,t):
        Ek = multiply(Elist[k],bis[k])     # EK/Vk 是个列表
        Vk = multiply(Vlist[k],bis[k])
        E2 = add(Ek,E2)   
        V2 = add(Vk,V2)
    X_Ab = multiply(Xalist[0],b)     # X_A^b   X_A 的值是随机生成的xa，通过椭圆曲线上的倍点运算生成的固定的值
    d = hash3((Xalist[0],pk_B,X_Ab))
    EV = add(E2,V2)    # E2 + V2
    EVd = multiply(EV,d)     # (E2 + V2)^d
    K = KDF(EVd)

    return K

#  M = IAEAM(K,enc_Data)

def DecryptFrags(sk_B:int,
                 pk_A:Tuple[int,int],
                 cFrags:Tuple[Tuple[Tuple[int,int],Tuple[int,int],int,Tuple[int,int]]],
                 C:Tuple[Tuple[Tuple[int,int],Tuple[int,int],int],int]
                 )->int:
    capsule,enc_Data = C   # 加密后的密文
    K = DecapsulateFrags(sk_B,pk_A,cFrags,capsule)
    
    iv = b'tpretpretpretpre'
    sm4_dec = Sm4Cbc(K, iv, DO_DECRYPT) #pylint: disable= e0602
    dec_Data = sm4_dec.update(enc_Data)
    dec_Data += sm4_dec.finish()
    return dec_Data