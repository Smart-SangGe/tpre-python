from fastapi import FastAPI, Request, HTTPException
import requests
from contextlib import asynccontextmanager
import socket
import asyncio
from pydantic import BaseModel
from tpre import *
import os
from typing import Any, Tuple
import base64


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clear()


app = FastAPI(lifespan=lifespan)
server_address = "http://60.204.236.38:8000/server"
id = 0
ip = ""
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
    id = requests.get(url, timeout=3)
    print("中心服务器返回节点ID为: ", id)


# 用环境变量获取本机ip
def get_local_ip():
    global ip
    ip = os.environ.get("HOST_IP")
    if not ip:  # 如果环境变量中没有IP
        try:
            # 从网卡获取IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # 通过连接Google DNS获取IP
            ip = str(s.getsockname()[0])
            s.close()
        except:
            raise ValueError("Unable to get IP")
            


def init():
    get_local_ip()
    send_ip()
    task = asyncio.create_task(send_heartbeat_internal())
    print("Finish init")


def clear():
    print("exit node")


# 接收用户发来的消息，经过处理之后，再将消息发送给其他用户


async def send_heartbeat_internal() -> None:
    timeout = 30
    global ip
    url = server_address + "/heartbeat?ip=" + ip
    while True:
        # print('successful send my_heart')
        try:
            folderol = requests.get(url, timeout=3)
        except:
            print("Central server error")

        # 删除超时的节点（假设你有一个异步的数据库操作函数）
        await asyncio.sleep(timeout)


class Req(BaseModel):
    source_ip: str
    dest_ip: str
    capsule: capsule
    ct: int
    rk: list


@app.post("/user_src")  # 接收用户1发送的信息
async def user_src(message: Req):
    global client_ip_src, client_ip_des
    print(
        f"Function 'user_src' called with: source_ip={message.source_ip}, dest_ip={message.dest_ip}, capsule={message.capsule}, ct={message.ct}, rk={message.rk}"
    )
    # kfrag , capsule_ct ,client_ip_src , client_ip_des   = json_data[]
    """
    payload = {
            "source_ip": local_ip,
            "dest_ip": dest_ip,
            "capsule_ct": capsule_ct,
            "rk": rk_list[i],
        }
    """
    print("node: ", message)
    source_ip = message.source_ip
    dest_ip = message.dest_ip
    capsule = message.capsule
    ct = message.ct
    # here has a problem. If ct longer than 32 bytes,
    # here will raise an error then exit.
    # So node will goes down.
    # def int_to_bytes(ct):
    #     byte_length = (ct.bit_length() + 7) // 8
    #     return ct.to_bytes(byte_length, byteorder='big')
    # capsule_ct = (capsule, int_to_bytes(ct))
    capsule_ct = (capsule, ct.to_bytes(32)) 
    rk = message.rk
    print(f"Computed capsule_ct: {capsule_ct}")
    a, b = ReEncrypt(rk, capsule_ct)
    processed_message = (a, int.from_bytes(b))
    print(f"Re-encrypted message: {processed_message}")
    await send_user_des_message(source_ip, dest_ip, processed_message)
    print("Message sent to destination user.")
    return HTTPException(status_code=200, detail="message recieved")


async def send_user_des_message(source_ip: str, dest_ip: str, re_message):  # 发送消息给用户2
    data = {"Tuple": re_message, "ip": source_ip}  # 类型不匹配

    # 发送 HTTP POST 请求
    response = requests.post(
        "http://" + dest_ip + ":8002" + "/receive_messages", json=data
    )
    print("send stauts:", response.text)


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("node:app", host="0.0.0.0", port=8001, reload=True, log_level="debug")
