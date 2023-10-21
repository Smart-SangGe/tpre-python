from fastapi import FastAPI
import requests
from contextlib import asynccontextmanager
import socket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    init()
    yield
    # Clean up the ML models and release the resources
    clear()

app = FastAPI(lifespan=lifespan)
server_address ="http://中心服务器IP地址:端口号/ip" 
id = 0

# 向中心服务器发送自己的IP地址,并获取自己的id
def send_ip(ip: str):
    url = server_address
    # ip = get_local_ip # type: ignore
    data = {"ip": ip}
    response = requests.post(url, data=data)
    data = response.json()
    id = data['id']
    return id

# 用socket获取本机ip
def get_local_ip():
    # 创建一个套接字对象
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 连接到一个外部的服务器，这将自动绑定到本地IP地址
    s.connect(("8.8.8.8", 80))
    # 获取本地IP地址
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip
  

id  = int
def init():
    ip = get_local_ip()
    global id
    id = send_ip(ip)

def clear():

    pass

@app.post("/heartbeat/")
async def receive_heartbeat():
    return {"status": "received"}








# 接收用户发来的消息，经过处理之后，再将消息发送给其他用户
@app.post("/send_message")
async def send_message(message: str):
    # 处理消息
    processed_message = message.upper()
    # 发送消息给其他用户
    url = "http://其他用户IP地址:端口号/receive_message"
    data = {"message": processed_message}
    response = requests.post(url, data=data)
    return response.json()
