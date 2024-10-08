import asyncio
import json
import logging
import os
import socket
import threading
import time
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from eth_logger import call_eth_logger
from tpre import ReEncrypt, capsule


@asynccontextmanager
async def lifespan(_: FastAPI):
    init()
    yield
    clear()


message_list = []

app = FastAPI(lifespan=lifespan)
server_address = os.environ.get("server_address")
id = 0
ip = ""
client_ip_src = ""  # 发送信息用户的ip
client_ip_des = ""  # 接收信息用户的ip
processed_message = ()  # 重加密后的数据

logger = logging.getLogger("uvicorn")


# class C(BaseModel):
#     Tuple: Tuple[capsule, int]
#     ip_src: str


# 向中心服务器发送自己的IP地址,并获取自己的id
def send_ip():
    url = server_address + "/get_node?ip=" + ip  # type: ignore
    # ip = get_local_ip() # type: ignore
    global id
    id = requests.get(url, timeout=3)
    logger.info(f"中心服务器返回节点ID为: {id}")
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
        except IndexError:
            raise ValueError("Unable to get IP")


def init():
    get_local_ip()
    send_ip()
    asyncio.create_task(send_heartbeat_internal())
    print("Finish init")


def clear():
    print("exit node")


# 接收用户发来的消息，经过处理之后，再将消息发送给其他用户


async def send_heartbeat_internal() -> None:
    timeout = 30
    global ip
    url = server_address + "/heartbeat?ip=" + ip  # type: ignore
    while True:
        # print('successful send my_heart')
        try:
            requests.get(url, timeout=3)
        except requests.exceptions.RequestException:
            logger.error("Central server error")
            print("Central server error")

        # 删除超时的节点
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
    logger.info(f"node: {message}")
    print("node: ", message)
    source_ip = message.source_ip
    dest_ip = message.dest_ip
    capsule = message.capsule
    ct = message.ct

    payload = {
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "capsule": capsule,
        "ct": ct,
        "rk": message.rk,
    }
    # 将消息详情记录到区块链
    global message_list
    message_list.append(payload)

    byte_length = (ct.bit_length() + 7) // 8
    capsule_ct = (capsule, ct.to_bytes(byte_length))

    rk = message.rk
    logger.info(f"Computed capsule_ct: {capsule_ct}")
    print(f"Computed capsule_ct: {capsule_ct}")

    a, b = ReEncrypt(rk, capsule_ct)  # type: ignore
    processed_message = (a, int.from_bytes(b))

    logger.info(f"Re-encrypted message: {processed_message}")
    print(f"Re-encrypted message: {processed_message}")

    await send_user_des_message(source_ip, dest_ip, processed_message)

    logger.info("Message sent to destination user.")
    print("Message sent to destination user.")
    return HTTPException(status_code=200, detail="message recieved")


async def send_user_des_message(
    source_ip: str, dest_ip: str, re_message
):  # 发送消息给用户2
    data = {"Tuple": re_message, "ip": source_ip}  # 类型不匹配

    # 发送 HTTP POST 请求
    response = requests.post(
        "http://" + dest_ip + ":8002" + "/receive_messages", json=data
    )

    logger.info(f"send stauts: {response.text}")
    print("send stauts:", response.text)


def log_message():
    while True:
        global message_list
        payload = json.dumps(message_list)
        message_list = []
        call_eth_logger(wallet_address, wallet_pk, payload)
        time.sleep(2)


wallet_address = (
    "0xe02666Cb63b3645E7B03C9082a24c4c1D7C9EFf6"  # 修改成要使用的钱包地址/私钥
)
wallet_pk = "ae66ae3711a69079efd3d3e9b55f599ce7514eb29dfe4f9551404d3f361438c6"


if __name__ == "__main__":
    import uvicorn

    threading.Thread(target=log_message).start()

    uvicorn.run("node:app", host="0.0.0.0", port=8001, reload=True, log_level="debug")
