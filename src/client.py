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
                capsule TEXT,
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
                publickey TEXT,
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
    with sqlite3.connect("client.db") as db:
        db.execute("DELETE FROM node")
        db.commit()
    print("Exit app")


# main page
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


class C(BaseModel):
    Tuple: Tuple[capsule, int]
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
    C_tuple = message.Tuple

    ip = message.ip
    if not C_tuple or not ip:
        raise HTTPException(status_code=400, detail="Invalid input data")

    C_capsule = C_tuple[0]
    C_ct = C_tuple[1]

    if not Checkcapsule(C_capsule):
        raise HTTPException(status_code=400, detail="Invalid capsule")

    # insert record into database
    with sqlite3.connect("message.db") as db:
        try:
            db.execute(
                """
                INSERT INTO message 
                (capsule_column, ct_column, ip_column) 
                VALUES 
                (?, ?, ?)
                """,
                (C_capsule, C_ct, ip),
            )
            db.commit()
            await check_merge(C_ct, ip)
            return HTTPException(status_code=200, detail="Message received")
        except Exception as e:
            print(f"Error occurred: {e}")
            db.rollback()
            return HTTPException(status_code=400, detail="Database error")


# check record count
async def check_merge(ct: int, ip: str):
    global sk, pk, node_response, message
    with sqlite3.connect("client.db") as db:
        # Check if the combination of ct_column and ip_column appears more than once.
        cursor = db.execute(
            """
        SELECT capsule, ct 
        FROM message  
        WHERE ct = ? AND senderip = ?
        """,
            (ct, ip),
        )
        # [(capsule, ct), ...]
        cfrag_cts = cursor.fetchall()

        # get T
        cursor = db.execute(
            """
        SELECT publickey, threshold 
        FROM senderinfo
        WHERE senderip = ?
        """,
            (ip),
        )
        result = cursor.fetchall()
        pk_sender, T = result[0]  # result[0] = (pk, threshold)

    if len(cfrag_cts) >= T:
        cfrags = mergecfrag(cfrag_cts)
        message = DecryptFrags(sk, pk, pk_sender, cfrags)  # type: ignore
        node_response = True


# send message to node
async def send_messages(
    node_ips: tuple[str, ...], message: bytes, dest_ip: str, pk_B: point, shreshold: int
):
    global pk, sk
    id_list = []
    print(node_ips)
    # calculate id of nodes
    for node_ip in node_ips:
        node_ip = node_ip[0]
        ip_parts = node_ip.split(".")
        id = 0
        for i in range(4):
            id += int(ip_parts[i]) << (24 - (8 * i))
        id_list.append(id)

    # generate rk
    rk_list = GenerateReKey(sk, pk_B, len(node_ips), shreshold, tuple(id_list))  # type: ignore

    capsule_ct = Encrypt(pk, message)  # type: ignore

    for i in range(len(node_ips)):
        url = "http://" + node_ips[i][0] + ":8001" + "/user_src?message"

        payload = {
            "source_ip": local_ip,
            "dest_ip": dest_ip,
            "capsule_ct": capsule_ct,
            "rk": rk_list[i],
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"send to {node_ips[i]} successful")
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
    dest_ip = i_m.dest_ip
    # dest_ip = dest_ip.split(":")[0]
    message_name = i_m.message_name
    source_ip = get_own_ip()
    dest_port = "8002"
    url = "http://" + dest_ip + ":" + dest_port + "/recieve_request?i_m"
    payload = {
        "dest_ip": dest_ip,
        "message_name": message_name,
        "source_ip": source_ip,
        "pk": pk,
    }
    try:
        response = requests.post(url, json=payload, timeout=3)
        print(response.text)

    except:
        print("can't post")
        return {"message": "can't post"}
    if response.status_code == 200:
        data = response.json()
        public_key = int(data["public_key"])
        threshold = int(data["threshold"])
        with sqlite3.connect("client.db") as db:
            db.execute(
                """
        INSERT INTO senderinfo
        (public_key, threshold)
        VALUES
        (?, ?)
        """,
                (public_key, threshold),
            )

    try:
        if response.status_code == 200:
            data = response.json()
            public_key = int(data["public_key"])
            threshold = int(data["threshold"])
            print(data)
            with sqlite3.connect("client.db") as db:
                db.execute(
                    """
            INSERT INTO senderinfo
            (public_key, threshold)
            VALUES
            (?, ?)
            """,
                    (public_key, threshold),
                )
    except:
        print("Database error")
        return {"message": "Database Error"}

    # wait 10s to recieve message from nodes
    for _ in range(3):
        if node_response:
            data = message

            # reset message and node_response
            message = b""
            node_response = False

            # return message to frontend
            return {"message": data}
        time.sleep(1)
    return {"message": "recieve timeout"}


# recieve request from others
@app.post("/recieve_request")
async def recieve_request(i_m: IP_Message):
    global pk
    source_ip = get_own_ip()
    if source_ip != i_m.dest_ip:
        return HTTPException(status_code=400, detail="Wrong ip")
    dest_ip = i_m.source_ip
    # threshold = random.randrange(1, 2)
    threshold = 2
    own_public_key = pk
    pk_B = i_m.pk

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

    # message name
    message = b"hello world" + random.randbytes(8)

    # send message to nodes
    await send_messages(tuple(node_ips), message, dest_ip, pk_B, threshold)
    response = {"threshold": threshold, "public_key": own_public_key}
    return response


def get_own_ip() -> str:
    ip = os.environ.get("HOST_IP", "IP not set")
    return ip


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


pk = point
sk = int
server_address = str
node_response = False
message = bytes
local_ip = get_own_ip()

if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("client:app", host="0.0.0.0", port=8002, reload=True)
