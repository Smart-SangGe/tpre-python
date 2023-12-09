from setuptools import setup, Extension

# 定义您的扩展
ext = Extension(
    "tpreECC",
    sources=["tpreECC.c"],
)

setup(
    name="tpreECC",
    version="1.0",
    description="basic ECC written in C",
    ext_modules=[ext],
)
