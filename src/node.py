from fastapi import FastAPI, Request, HTTPException
import requests
from contextlib import asynccontextmanager
import socket
import asyncio
from pydantic import BaseModel
from tpre import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clear()


app = FastAPI(lifespan=lifespan)
server_address = "http://10.20.14.232:8000/server"
id = 0
ip = "10.16.21.163"
client_ip_src = ""  # 发送信息用户的ip
client_ip_des = ""  # 接收信息用户的ip
processed_message = ()  # 重加密后的数据

# class C(BaseModel):
#     Tuple: Tuple[capsule, int]
#     ip_src: str


# 向中心服务器发送自己的IP地址,并获取自己的id
def send_ip():
    url = server_address + "/get_node?ip=" + ip
    # ip = get_local_ip() # type: ignore
    global id
    id = requests.get(url)


# 用socket获取本机ip
def get_local_ip():
    # 创建一个套接字对象
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 连接到一个外部的服务器，这将自动绑定到本地IP地址
    s.connect(("8.8.8.8", 80))
    # 获取本地IP地址
    local_ip = s.getsockname()[0]
    s.close()
    global ip
    ip = local_ip


def init():
    # get_local_ip()
    global id
    send_ip()
    task = asyncio.create_task(send_heartbeat_internal())
    print("Finish init")


def clear():
    pass


# 接收用户发来的消息，经过处理之后，再将消息发送给其他用户


async def send_heartbeat_internal() -> None:
    timeout = 3
    global ip
    url = server_address + "/heartbeat?ip=" + ip
    while True:
        # print('successful send my_heart')
        try:
            folderol = requests.get(url)
        except:
            print("Central server error")
        
        # 删除超时的节点（假设你有一个异步的数据库操作函数）
        await asyncio.sleep(timeout)


@app.post("/user_src")  # 接收用户1发送的信息
async def receive_user_src_message(message: Request):
    global client_ip_src, client_ip_des
    # kfrag , capsule_ct ,client_ip_src , client_ip_des   = json_data[]  # 看梁俊勇
    """
    payload = {
            "source_ip": local_ip,
            "dest_ip": dest_ip,
            "capsule_ct": capsule_ct,
            "rk": rk_list[i],
        }
    """

    data = await message.json()
    source_ip = data.get("source_ip")
    dest_ip = data.get("dest_ip")
    capsule_ct = data.get("capsule_ct")
    rk = data.get("rk")

    processed_message = ReEncrypt(rk, capsule_ct)
    await send_user_des_message(source_ip, dest_ip, processed_message)
    return HTTPException(status_code=200, detail="message recieved")


async def send_user_des_message(source_ip: str, dest_ip: str, re_message):  # 发送消息给用户2
    data = {"Tuple": re_message, "ip": source_ip}  # 类型不匹配

    # 发送 HTTP POST 请求
    response = requests.post(
        "http://" + dest_ip + "/receive_messages?message", json=data
    )
    print(response)


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("node:app", host="0.0.0.0", port=8001, reload=True)
