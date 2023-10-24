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
server_address = "http://110.41.155.96:8000/server"
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


# 用环境变量获取本机ip
def get_local_ip():
    global ip
    ip = os.environ.get("HOST_IP", "IP not set")


def init():
    get_local_ip()
    send_ip()
    task = asyncio.create_task(send_heartbeat_internal())
    print("Finish init")


def clear():
    print("exit node")


# 接收用户发来的消息，经过处理之后，再将消息发送给其他用户


async def send_heartbeat_internal() -> None:
    timeout = 3
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
    capsule_ct: Tuple[capsule, int]
    rk: Any


@app.post("/user_src")  # 接收用户1发送的信息
async def user_src(message: Req):
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
    source_ip = message.source_ip
    dest_ip = message.dest_ip
    capsule, ct = message.capsule_ct
    capsule_ct = (capsule, ct.to_bytes(32))
    rk = message.rk

    a, b = ReEncrypt(rk, capsule_ct)
    processed_message = (a, int.from_bytes(b))
    await send_user_des_message(source_ip, dest_ip, processed_message)
    return HTTPException(status_code=200, detail="message recieved")


async def send_user_des_message(source_ip: str, dest_ip: str, re_message):  # 发送消息给用户2
    data = {"Tuple": re_message, "ip": source_ip}  # 类型不匹配

    # 发送 HTTP POST 请求
    response = requests.post(
        "http://" + dest_ip + "/receive_messages", json=data
    )
    print(response)


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("node:app", host="0.0.0.0", port=8001, reload=True)
