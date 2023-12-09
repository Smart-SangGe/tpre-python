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

// 将Python中的multiply函数转换为C
static Point multiply(Point a, int64_t n)
{
    Point result;
    // ...实现乘法逻辑...
    return result;
}

// Python接口函数
static PyObject *py_multiply(PyObject *self, PyObject *args)
{
    Point a;
    int64_t n;

    // 从Python参数解析值到C变量
    if (!PyArg_ParseTuple(args, "(ll)l", &a.x, &a.y, &n))
    {
        return NULL;
    }

    Point result = multiply(a, n);

    // 将C结构体的结果转换回Python对象
    return Py_BuildValue("(ll)", result.x, result.y);
}

// 模块方法定义
static PyMethodDef MyMethods[] = {
    {"multiply", py_multiply, METH_VARARGS, "Multiply a point on the curve by a scalar"},
    {NULL, NULL, 0, NULL} // 哨兵
};

// 模块定义
static struct PyModuleDef tpre = {
    PyModuleDef_HEAD_INIT,
    "tpre",
    NULL, // 模块文档
    -1,
    MyMethods};

// 初始化模块
PyMODINIT_FUNC PyInit_tpre(void)
{
    return PyModule_Create(&tpre);
}
