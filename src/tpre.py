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
        
def Setup(sec: int) -> Tuple[CurveFp, Tuple[int, int], 
                             Tuple[int, int], Callable,
                             Callable, Callable, Callable]:
    '''
    params:
    sec: an init safety param
    
    return:
<<<<<<< HEAD
    G: sm2 curve
    g: generator
    U: another generator
    use sm3 as hash function
    hash2: G^2 -> Zq 
    hash3: G^3 -> Zq
    hash4: G^3 * Zq -> Zq
    '''
    
    G = sm2p256v1
    
    g = (sm2p256v1.Gx, sm2p256v1.Gy)
    
    tmp_u = random.randint(0, sm2p256v1.P)
    U = multiply(g, tmp_u)
    
    def hash2(double_G: Tuple[Tuple[int, int], Tuple[int, int]]) -> int:
        sm3 = Sm3() #pylint: disable=e0602
        for i in double_G:
            for j in i:
                sm3.update(j.to_bytes())
        digest = sm3.digest()
        digest = int.from_bytes(digest,'big') % sm2p256v1.P
        return digest
    
    def hash3(triple_G: Tuple[Tuple[int, int], 
                              Tuple[int, int],
                              Tuple[int, int]]) -> int:
        sm3 = Sm3() #pylint: disable=e0602
        for i in triple_G:
            for j in i:
                sm3.update(j.to_bytes())
        digest = sm3.digest()
        digest = int.from_bytes(digest,'big') % sm2p256v1.P
        return digest
    
    def hash4(triple_G: Tuple[Tuple[int, int],
                              Tuple[int, int],
                              Tuple[int, int]],
                Zp: int) -> int:
        sm3 = Sm3() #pylint: disable=e0602
        for i in triple_G:
            for j in i:
                sm3.update(j.to_bytes())
        sm3.update(Zp.to_bytes())
        digest = sm3.digest()
        digest = int.from_bytes(digest,'big') % sm2p256v1.P
        return digest
    
    KDF = Sm3() #pylint: disable=e0602
    
    return G, g, U, hash2, hash3, hash4, KDF

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
    

def Enc(pk: Tuple[int, int], m: int) -> Tuple[Tuple[
    Tuple[int, int],Tuple[int, int], int], int]:
    enca = Encapsulate(pk)
    K = enca[0]
    capsule = enca[1]
    
    sm4_enc = Sm4Cbc(key, iv, DO_ENCRYPT) #pylint: disable=e0602
    plain_Data = m.to_bytes()
    enc_Data = sm4_enc.update(plain_Data)
    enc_Data += sm4_enc.finish()
    enc_message = (capsule, enc_Data)
    return enc_message