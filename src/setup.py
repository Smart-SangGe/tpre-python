from setuptools import setup, Extension

# 定义您的扩展
ext = Extension("tpre", sources=["tpre.c"])

setup(
    name="tpre",
    version="1.0",
    description="tpre written in C",
    ext_modules=[ext],
)
