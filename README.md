# tpre-python

本项目是全国密码学竞赛设计项目，该项目是使用python实现tpre算法

## 项目原理  

使用国密算法实现分布式代理重加密tpre

## 项目结构

.  
├── basedockerfile (用于构建base镜像)  
├── dockerfile (用于构建应用镜像)  
├── doc (开发文档)  
├── include (gmssl 的头文件)  
├── lib (gmssl 的共享库)  
├── LICENSE  
├── README_en.md  
├── README.md  
├── requirements.txt  
└── src (程序源码)  

## 环境依赖

### 直接在实体机安装（未测试）

系统要求：

- Linux
- Windows (需要自行安装gmssl的共享库)

该项目依赖以下软件：  
python 3.11
gmssl
gmssl-python

### Docker 版本安装

```bash
apt update && apt install mosh -y 
chmod +x install_docker.sh
./install_docker.sh
```

### 开发环境docker版本信息

docker 版本:  

- 版本:           24.0.5  
- API 版本:       1.43  
- Go 版本:        go1.20.6  

## 安装步骤

### 安装前的准备

本项目依赖gmssl，所以请提前安装好。访问 [GmSSL](https://github.com/guanzhi/GmSSL) 可以看到如何安装。

然后安装必要的python库

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Docker 安装

### 使用准备好的base镜像，然后自己部署应用

```bash
docker build . -f basedockerfile -t git.mamahaha.work/sangge/tpre:base
(或者 docker pull git.mamahaha.work/sangge/tpre:base)  
docker build . -t your_image_name
```

### 使用完整版的docker镜像

```bash
docker pull git.mamahaha.work/sangge/tpre:latest
```

## 使用说明

详细说明查看开发文档 [docs](doc/README_app_en.md)

## 参考文献  

[TPRE Algorithm Blog Post](https://www.cnblogs.com/pam-sh/p/17364656.html#tprelib%E7%AE%97%E6%B3%95)  
[Gmssl-python library](https://github.com/GmSSL/GmSSL-Python)

## 许可证

GNU GENERAL PUBLIC LICENSE v3
