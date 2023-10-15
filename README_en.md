# tpre-python

This project is designed for the National Cryptography Competition and is implemented in Python to execute the TPRE algorithm.

## Project Principle

The project uses the Chinese national standard cryptography algorithm to implement distributed proxy re-encryption (TPRE).

## Project Structure
.  
├── basedockerfile (being used to build base iamge)  
├── dockerfile (being used to build application)  
├── include (gmssl header)  
├── lib (gmssl shared object)  
├── LICENSE  
├── README_en.md  
├── README.md  
├── requirements.txt  
└── src (application source code)  

## Environment Dependencies

System requirements:  
- Linux
- Windows(may need to complie and install gmssl yourself)

The project relies on the following software:  
- Python 3.11
- gmssl
- gmssl-python

## Installation Steps

### Pre-installation
This project depends on gmssl, so you need to compile it from source first.  
Visit [GmSSL](https://github.com/guanzhi/GmSSL) to learn how to install.  

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```


## Docker Installation
my docker version:
- Version:           24.0.5
- API version:       1.43
- Go version:        go1.20.6

### Use base image and build yourself
```bash
docker pull git.mamahaha.work/sangge/tpre:base  
docker build . -t your_image_name
docker run your_image_name
```

### Use pre-build image
```bash
docker pull git.mamahaha.work/sangge/tpre:latest
docker run git.mamahaha.work/sangge/tpre:latest
```

## Usage Instructions


## References  
[TPRE Algorithm Blog Post](https://www.cnblogs.com/pam-sh/p/17364656.html#tprelib%E7%AE%97%E6%B3%95)  
[Gmssl-python library](https://github.com/GmSSL/GmSSL-Python)


## License
GNU GENERAL PUBLIC LICENSE v3
