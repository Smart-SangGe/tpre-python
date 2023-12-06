#ifndef tpre_SM2_H
#define tpre_SM2_H

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