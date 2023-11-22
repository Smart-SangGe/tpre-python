from fastapi import FastAPI, HTTPException
import requests
import os
from typing import Tuple
from tpre import *
import sqlite3
from contextlib import asynccontextmanager
from pydantic import BaseModel
import socket
import random
import time
import base64
import json
import pickle
from fastapi.responses import JSONResponse
import asyncio

# 测试文本
test_msessgaes = {
    "name": b"proxy re-encryption",
    "environment": b"distributed environment"
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clean_env()


app = FastAPI(lifespan=lifespan)


def init():
    global pk, sk, server_address
    init_db()
    pk, sk = GenerateKeyPair()

    # load config from config file
    init_config()
    get_node_list(2, server_address)  # type: ignore


def init_db():
    with sqlite3.connect("client.db") as db:
        # message table
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY,
                capsule BLOB,
                ct TEXT,
                senderip TEXT
            );
        """
        )

        # node ip table
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS node (
                id INTEGER PRIMARY KEY,
                nodeip TEXT
            );
        """
        )

        # sender info table
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS senderinfo (
                id INTEGER PRIMARY KEY,
                ip TEXT,
                pkx TEXT,
                pky TEXT,
                threshold INTEGER
            )
            """
        )
        db.commit()
        print("Init Database Successful")


# load config from config file
def init_config():
    import configparser

    global server_address
    config = configparser.ConfigParser()
    config.read("client.ini")

    server_address = config["settings"]["server_address"]


# execute on exit
def clean_env():
    global message, node_response
    message = b""
    node_response = False
    with sqlite3.connect("client.db") as db:
        db.execute("DELETE FROM node")
        db.execute("DELETE FROM message")
        db.execute("DELETE FROM senderinfo")
        db.commit()
    print("Exit app")


# main page
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


class C(BaseModel):
    Tuple: Tuple[Tuple[Tuple[int, int], Tuple[int, int], int, Tuple[int, int]], int]
    ip: str


# receive messages from nodes
@app.post("/receive_messages")
async def receive_messages(message: C):
    """
    receive capsule and ip from nodes
    params:
    Tuple: capsule and ct
    ip: sender ip
    return:
    status_code
    """
    print(f"Received message: {message}")

    if not message.Tuple or not message.ip:
        print("Invalid input data received.")
        raise HTTPException(status_code=400, detail="Invalid input data")

    C_capsule, C_ct = message.Tuple
    ip = message.ip

    # Serialization
    bin_C_capsule = pickle.dumps(C_capsule)

    # insert record into database
    with sqlite3.connect("client.db") as db:
        try:
            db.execute(
                """
                INSERT INTO message 
                (capsule, ct, senderip) 
                VALUES 
                (?, ?, ?)
                """,
                (bin_C_capsule, str(C_ct), ip),
            )
            db.commit()
            print("Data inserted successfully into database.")
            check_merge(C_ct, ip)
            return HTTPException(status_code=200, detail="Message received")
        except Exception as e:
            print(f"Error occurred: {e}")
            db.rollback()
            return HTTPException(status_code=400, detail="Database error")


# check record count
def check_merge(ct: int, ip: str):
    global sk, pk, node_response, message
    """
    CREATE TABLE IF NOT EXISTS senderinfo (
        id INTEGER PRIMARY KEY,
        ip TEXT,
        pkx TEXT,
        pky TEXT,
        threshold INTEGER
    )
    """
    with sqlite3.connect("client.db") as db:
        # Check if the combination of ct_column and ip_column appears more than once.
        cursor = db.execute(
            """
        SELECT capsule, ct 
        FROM message  
        WHERE ct = ? AND senderip = ?
        """,
            (str(ct), ip),
        )
        # [(capsule, ct), ...]
        cfrag_cts = cursor.fetchall()

        # get _sender_pk
        cursor = db.execute(
            """
        SELECT pkx, pky
        FROM senderinfo
        WHERE ip = ?
        """,
            (ip,),
        )
        result = cursor.fetchall()
        try:
            pkx, pky = result[0]  # result[0] = (pkx, pky)
            pk_sender = (int(pkx), int(pky))
        except:
            pk_sender, T = 0, -1

    T = 2
    if len(cfrag_cts) >= T:
        # Deserialization
        temp_cfrag_cts = []
        for i in cfrag_cts:
            capsule = pickle.loads(i[0])
            temp_cfrag_cts.append((capsule, int(i[1]).to_bytes(32)))

        cfrags = mergecfrag(temp_cfrag_cts)

        print("sk:", type(sk))
        print("pk:", type(pk))
        print("pk_sender:", type(pk_sender))
        print("cfrags:", type(cfrags))
        message = DecryptFrags(sk, pk, pk_sender, cfrags)  # type: ignore

        print("merge success", message)
        node_response = True

        print("merge:", node_response)


# send message to node
async def send_messages(
    node_ips: tuple[str, ...], message: bytes, dest_ip: str, pk_B: point, shreshold: int
):
    global pk, sk
    id_list = []

    # calculate id of nodes
    for node_ip in node_ips:
        node_ip = node_ip[0]
        ip_parts = node_ip.split(".")
        id = 0
        for i in range(4):
            id += int(ip_parts[i]) << (24 - (8 * i))
        id_list.append(id)
    print(f"Calculated IDs: {id_list}")
    # generate rk
    rk_list = GenerateReKey(sk, pk_B, len(node_ips), shreshold, tuple(id_list))  # type: ignore
    print(f"Generated ReKey list: {rk_list}")
    capsule, ct = Encrypt(pk, message)  # type: ignore
    # capsule_ct = (capsule, int.from_bytes(ct))
    print(f"Encrypted message to capsule={capsule}, ct={ct}")

    for i in range(len(node_ips)):
        url = "http://" + node_ips[i][0] + ":8001" + "/user_src"
        payload = {
            "source_ip": local_ip,
            "dest_ip": dest_ip,
            "capsule": capsule,
            "ct": int.from_bytes(ct),
            "rk": rk_list[i],
        }
        print(f"Sending payload to {url}: {json.dumps(payload)}")
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print(f"send to {node_ips[i]} successful")
        else:
            print(
                f"Failed to send to {node_ips[i]}. Response code: {response.status_code}, Response text: {response.text}"
            )
    return 0


class IP_Message(BaseModel):
    dest_ip: str
    message_name: str
    source_ip: str
    pk: Tuple[int, int]


class Request_Message(BaseModel):
    dest_ip: str
    message_name: str


# request message from others
@app.post("/request_message")
async def request_message(i_m: Request_Message):
    global message, node_response, pk
    print(
        f"Function 'request_message' called with: dest_ip={i_m.dest_ip}, message_name={i_m.message_name}"
    )
    dest_ip = i_m.dest_ip
    # dest_ip = dest_ip.split(":")[0]
    message_name = i_m.message_name
    source_ip = get_own_ip()
    dest_port = "8002"
    url = "http://" + dest_ip + ":" + dest_port + "/receive_request"
    payload = {
        "dest_ip": dest_ip,
        "message_name": message_name,
        "source_ip": source_ip,
        "pk": pk,
    }
    print(f"Sending request to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload, timeout=1)
        print(f"Response received from {url}: {response.text}")
        # print("menxian and pk", response.text)

    except requests.Timeout:
        print("Timeout error: can't post to the destination.")
        # print("can't post")
        # content = {"message": "post timeout", "error": str(e)}
        # return JSONResponse(content, status_code=400)

    # wait 3s to receive message from nodes
    for _ in range(10):
        print(f"Waiting for node_response... Current value: {node_response}")
        # print("wait:", node_response)
        if node_response:
            data = message
            print(f"Node response received with message: {data}")
            # reset message and node_response
            message = b""
            node_response = False

            # return message to frontend
            return {"message": str(data)}
        await asyncio.sleep(0.2)
    print("Timeout while waiting for node_response.")
    content = {"message": "receive timeout"}
    return JSONResponse(content, status_code=400)


# receive request from others
@app.post("/receive_request")
async def receive_request(i_m: IP_Message):
    global pk
    print(
        f"Function 'receive_request' called with: dest_ip={i_m.dest_ip}, source_ip={i_m.source_ip}, pk={i_m.pk}"
    )
    source_ip = get_own_ip()
    print(f"Own IP: {source_ip}")
    if source_ip != i_m.dest_ip:
        print("Mismatch in destination IP.")
        return HTTPException(status_code=400, detail="Wrong ip")
    dest_ip = i_m.source_ip
    # threshold = random.randrange(1, 2)
    threshold = 2
    own_public_key = pk
    pk_B = i_m.pk
    print(f"Using own public key: {own_public_key} and received public key: {pk_B}")

    with sqlite3.connect("client.db") as db:
        cursor = db.execute(
            """
                   SELECT nodeip
                   FROM node
                   LIMIT ?
                   """,
            (threshold,),
        )
        node_ips = cursor.fetchall()
    print(f"Selected node IPs from database: {node_ips}")

    # message name
    # message_name = i_m.message_name
    # message = xxxxx

    # 根据message name到测试文本查找对应值
    message = test_msessgaes[i_m.message_name]

    # message = b"hello world" + random.randbytes(8)
    print(f"Generated message: {message}")

    # send message to nodes
    await send_messages(tuple(node_ips), message, dest_ip, pk_B, threshold)
    response = {"threshold": threshold, "public_key": own_public_key}
    print(f"Sending response: {response}")
    return response


def get_own_ip() -> str:
    ip = os.environ.get("HOST_IP")
    if not ip:  # 如果环境变量中没有IP
        try:
            # 从网卡获取IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # 通过连接Google DNS获取IP
            ip = s.getsockname()[0]
            s.close()
        except:
            raise ValueError("Unable to get IP")
    return str(ip)


# get node list from central server
def get_node_list(count: int, server_addr: str):
    url = "http://" + server_addr + "/server/send_nodes_list?count=" + str(count)
    response = requests.get(url, timeout=3)
    # Checking the response
    if response.status_code == 200:
        print("Success get node list")
        node_ip = response.text
        node_ip = eval(node_ip)
        print(node_ip)
        # insert node ip to database
        with sqlite3.connect("client.db") as db:
            db.executemany(
                """
                INSERT INTO node 
                (nodeip) 
                VALUES (?)
                """,
                [(ip,) for ip in node_ip],
            )
            db.commit()
        print("Success add node ip")
    else:
        print("Failed:", response.status_code, response.text)


# send pk to others
@app.get("/get_pk")
async def get_pk():
    global pk, sk
    print(sk)
    return {"pkx": str(pk[0]), "pky": str(pk[1])}


class pk_model(BaseModel):
    pkx: str
    pky: str
    ip: str


# recieve pk from frontend
@app.post("/recieve_pk")
async def recieve_pk(pk: pk_model):
    pkx = pk.pkx
    pky = pk.pky
    dest_ip = pk.ip
    try:
        threshold = 2
        with sqlite3.connect("client.db") as db:
            db.execute(
                """
        INSERT INTO senderinfo
        (ip, pkx, pky, threshold)
        VALUES
        (?, ?, ?, ?)
        """,
                (str(dest_ip), pkx, pky, threshold),
            )
    except Exception as e:
        # raise error
        print("Database error")
        content = {"message": "Database Error", "error": str(e)}
        return JSONResponse(content, status_code=400)
    return {"message": "save pk in database"}


pk = (0, 0)
sk = 0
server_address = str
node_response = False
message = bytes
local_ip = get_own_ip()

if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("client:app", host="0.0.0.0", port=8002, reload=True, log_level="debug")
