#include <Python.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// define TPRE Big Number
typedef uint64_t TPRE_BN[8]

    // GF(p)
    typedef TPRE_BN SM2_Fp;

// GF(n)
typedef TPRE_BN SM2_Fn;

// 定义一个结构体来表示雅各比坐标系的点
typedef struct
{
    TPRE_BN X;
    TPRE_BN Y;
    TPRE_BN Z;
} JACOBIAN_POINT;

// 定义一个结构体来表示点
typedef struct
{
    uint8_t x[32];
    uint8_t y[32];
} TPRE_POINT;

const TPRE_BN SM2_P = {
    0xffffffff,
    0xffffffff,
    0x00000000,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xfffffffe,
};

const TPRE_BN SM2_A = {
    0xfffffffc,
    0xffffffff,
    0x00000000,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xfffffffe,
};

const TPRE_BN SM2_B = {
    0x4d940e93,
    0xddbcbd41,
    0x15ab8f92,
    0xf39789f5,
    0xcf6509a7,
    0x4d5a9e4b,
    0x9d9f5e34,
    0x28e9fa9e,
};

// 生成元GX, GY
const SM2_JACOBIAN_POINT _SM2_G = {
    {
        0x334c74c7,
        0x715a4589,
        0xf2660be1,
        0x8fe30bbf,
        0x6a39c994,
        0x5f990446,
        0x1f198119,
        0x32c4ae2c,
    },
    {
        0x2139f0a0,
        0x02df32e5,
        0xc62a4740,
        0xd0a9877c,
        0x6b692153,
        0x59bdcee3,
        0xf4f6779c,
        0xbc3736a2,
    },
    {
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    },
};

const SM2_JACOBIAN_POINT *SM2_G = &_SM2_G;

const TPRE_BN SM2_N = {
    0x39d54123,
    0x53bbf409,
    0x21c6052b,
    0x7203df6b,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xfffffffe,
};

// u = (p - 1)/4, u + 1 = (p + 1)/4
const TPRE_BN SM2_U_PLUS_ONE = {
    0x00000000,
    0x40000000,
    0xc0000000,
    0xffffffff,
    0xffffffff,
    0xffffffff,
    0xbfffffff,
    0x3fffffff,
};

const TPRE_BN SM2_ONE = {1, 0, 0, 0, 0, 0, 0, 0};
const TPRE_BN SM2_TWO = {2, 0, 0, 0, 0, 0, 0, 0};
const TPRE_BN SM2_THREE = {3, 0, 0, 0, 0, 0, 0, 0};

#define GETU32(p)             \
    ((uint32_t)(p)[0] << 24 | \
     (uint32_t)(p)[1] << 16 | \
     (uint32_t)(p)[2] << 8 |  \
     (uint32_t)(p)[3])

// 点乘
static void multiply(TPRE_POINT r, const TPRE_POINT a, int64_t n)
{
    Point result;
    // ...实现乘法逻辑...
    return result;
}

// 点加
static void add(TPRE_POINT *R, TPRE_POINT *P, TPRE_POINT *Q)
{
    JACOBIAN_POINT P_;
    JACOBIAN_POINT Q_;

    jacobianPoint_from_bytes(&P_, (uint8_t *)P)
        jacobianPoint_from_bytes(&Q_, (uint8_t *)Q)
            jacobianPoint_add(&P_, &P_, &Q_);
    jacobianPoint_to_bytes(&P_, (uint8_t *)R);
}

// 求逆
static void inv()
{
}

// jacobianPoint点加
static void jacobianPoint_add(JACOBIAN_POINT *R, const JACOBIAN_POINT *P, const JACOBIAN_POINT *Q)
{
    const uint64_t *X1 = P->X;
    const uint64_t *Y1 = P->Y;
    const uint64_t *Z1 = P->Z;
    const uint64_t *x2 = Q->X;
    const uint64_t *y2 = Q->Y;
    SM2_BN T1;
    SM2_BN T2;
    SM2_BN T3;
    SM2_BN T4;
    SM2_BN X3;
    SM2_BN Y3;
    SM2_BN Z3;
    if (sm2_jacobian_point_is_at_infinity(Q))
    {
        sm2_jacobian_point_copy(R, P);
        return;
    }

    if (sm2_jacobian_point_is_at_infinity(P))
    {
        sm2_jacobian_point_copy(R, Q);
        return;
    }

    assert(sm2_bn_is_one(Q->Z));

    sm2_fp_sqr(T1, Z1);
    sm2_fp_mul(T2, T1, Z1);
    sm2_fp_mul(T1, T1, x2);
    sm2_fp_mul(T2, T2, y2);
    sm2_fp_sub(T1, T1, X1);
    sm2_fp_sub(T2, T2, Y1);
    if (sm2_bn_is_zero(T1))
    {
        if (sm2_bn_is_zero(T2))
        {
            SM2_JACOBIAN_POINT _Q, *Q = &_Q;
            sm2_jacobian_point_set_xy(Q, x2, y2);

            sm2_jacobian_point_dbl(R, Q);
            return;
        }
        else
        {
            sm2_jacobian_point_set_infinity(R);
            return;
        }
    }
    sm2_fp_mul(Z3, Z1, T1);
    sm2_fp_sqr(T3, T1);
    sm2_fp_mul(T4, T3, T1);
    sm2_fp_mul(T3, T3, X1);
    sm2_fp_dbl(T1, T3);
    sm2_fp_sqr(X3, T2);
    sm2_fp_sub(X3, X3, T1);
    sm2_fp_sub(X3, X3, T4);
    sm2_fp_sub(T3, T3, X3);
    sm2_fp_mul(T3, T3, T2);
    sm2_fp_mul(T4, T4, Y1);
    sm2_fp_sub(Y3, T3, T4);

    sm2_bn_copy(R->X, X3);
    sm2_bn_copy(R->Y, Y3);
    sm2_bn_copy(R->Z, Z3);
}

// bytes转jacobianPoint
static void jacobianPoint_from_bytes(JACOBIAN_POINT *P, const uint8_t in[64])
{
}

// jacobianPoint转bytes
static void jacobianPoint_to_bytes(JACOBIAN_POINT *P, const uint8_t in[64])
{
}

static void BN_from_bytes(TPRE_BN *r, const uint8_t in[32])
{
    int i;
    for (i = 7; i >= 0; i--)
    {
        r[i] = GETU32(in);
        in += sizeof(uint32_t);
    }
}

// 点乘的Python接口函数
static PyObject *py_multiply(PyObject *self, PyObject *args)
{
    return
}

// 点加的Python接口函数
static PyObject *py_add(PyObject *self, PyObject *args)
{
    return
}

// 求逆的Python接口函数
static PyObject *py_inv(PyObject *self, PyObject *args)
{
    return
}

// 模块方法定义
static PyMethodDef MyMethods[] = {
    {"multiply", py_multiply, METH_VARARGS, "Multiply a point on the sm2p256v1 curve"},
    {"add", py_add, METH_VARARGS, "Add a point on thesm2p256v1 curve"},
    {"inv", py_inv, METH_VARARGS, "Calculate an inv of a number"},
    {NULL, NULL, 0, NULL} // 哨兵
};

// 模块定义
static struct PyModuleDef tpreECC = {
    PyModuleDef_HEAD_INIT,
    "tpreECC",
    NULL, // 模块文档
    -1,
    MyMethods};

// 初始化模块
PyMODINIT_FUNC PyInit_tpre(void)
{
    return PyModule_Create(&tpreECC);
}
