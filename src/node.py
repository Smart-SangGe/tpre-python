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


import requests

def send_heartbeat(url: str) -> bool:
    try:
        response = requests.get(url, timeout=5)  # 使用 GET 方法作为心跳请求
        response.raise_for_status()  # 检查响应是否为 200 OK

        # 可选：根据响应内容进行进一步验证
        # if response.json() != expected_response:
        #     return False

        return True
    except requests.RequestException:
        return False

# 使用方式
url = "https://your-service-url.com/heartbeat"
if send_heartbeat(url):
    print("Service is alive!")
else:
    print("Service might be down or unreachable.")


import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

async def receive_heartbeat_internal() -> int:
    while True:
        print('successful delete1')
        timeout = 10
        # 删除超时的节点（假设你有一个异步的数据库操作函数）
        await async_cursor_execute("DELETE FROM nodes WHERE last_heartbeat < ?", (time.time() - timeout,))
        await async_conn_commit()
        print('successful delete')
        await asyncio.sleep(timeout)

    return 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(receive_heartbeat_internal())
    yield
    task.cancel()  # 取消我们之前创建的任务
    await clean_env()  # 假设这是一个异步函数

# 其他FastAPI应用的代码...
