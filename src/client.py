<<<<<<< HEAD
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

    print("Starting function: init_config")

    global server_address
    config = configparser.ConfigParser()
    print("Attempting to read client.ini...")
    config.read("client.ini")

    if "settings" in config and "server_address" in config["settings"]:
        server_address = config["settings"]["server_address"]
        print(f"Config loaded successfully. Server address: {server_address}")
    else:
        print("Error: 'settings' section or 'server_address' key not found in client.ini")

    print("Function init_config executed successfully!")



# execute on exit
def clean_env():
    global message, node_response
    message = b""
    node_response = False
    with sqlite3.connect("client.db") as db:
        db.execute("DELETE FROM node")
        db.execute("DELETE FROM message")
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

    print("Starting function: receive_messages")

    if not message.Tuple or not message.ip:
        print("Invalid input data")
        raise HTTPException(status_code=400, detail="Invalid input data")

    C_capsule, C_ct = message.Tuple
    ip = message.ip
    print(f"Received message: Capsule = {C_capsule}, C_ct = {C_ct}, IP = {ip}")

    # Serialization
    print("Serializing the capsule...")
    bin_C_capsule = pickle.dumps(C_capsule)
    print("Serialization successful")

    # insert record into database
    with sqlite3.connect("client.db") as db:
        try:
            print("Attempting to insert data into 'message' table...")
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
            print("Data insertion successful")
            
            check_merge(C_ct, ip)
            print("check_merge executed successfully")
            
            return HTTPException(status_code=200, detail="Message received")
        except Exception as e:
            print(f"Error occurred: {e}")
            db.rollback()
            return HTTPException(status_code=400, detail="Database error")

    print("Function receive_messages executed successfully!")



# check record count
def check_merge(ct: int, ip: str):
    print("Starting function: check_merge")
    
    global sk, pk, node_response, message

    with sqlite3.connect("client.db") as db:
        # Check if the combination of ct_column and ip_column appears more than once.
        print("Fetching data from 'message' table...")
        cursor = db.execute(
            """
        SELECT capsule, ct 
        FROM message  
        WHERE ct = ? AND senderip = ?
        """,
            (str(ct), ip),
        )
        cfrag_cts = cursor.fetchall()
        print(f"Number of records fetched from 'message' table: {len(cfrag_cts)}")

        # get _sender_pk
        print("Fetching sender's public key...")
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
            print(f"Successfully fetched sender's public key: {pk_sender}")
        except:
            pk_sender, T = 0, -1
            print("Failed to fetch sender's public key")

    T = 2
    if len(cfrag_cts) >= T:
        # Deserialization
        temp_cfrag_cts = []
        for i in cfrag_cts:
            capsule = pickle.loads(i[0])
            temp_cfrag_cts.append((capsule, int(i[1]).to_bytes(32)))
        print("Deserialization completed")

        cfrags = mergecfrag(temp_cfrag_cts)

        print("Attempting decryption...")
        print("sk:", type(sk))
        print("pk:", type(pk))
        print("pk_sender:", type(pk_sender))
        print("cfrags:", type(cfrags))
        message = DecryptFrags(sk, pk, pk_sender, cfrags)

        print(f"Decryption successful, message: {message}")
        node_response = True
        print(f"Node response set to: {node_response}")
    else:
        print("Insufficient number of cfrag_cts, skipping decryption")

    print("Function check_merge executed successfully!")



# send message to node
async def send_messages(
    node_ips: tuple[str, ...], message: bytes, dest_ip: str, pk_B: point, shreshold: int
):
    print("Starting function: send_messages")
    
    global pk, sk
    id_list = []

    # calculate id of nodes
    print("Calculating ID of nodes...")
    for node_ip in node_ips:
        node_ip = node_ip[0]
        ip_parts = node_ip.split(".")
        id = 0
        for i in range(4):
            id += int(ip_parts[i]) << (24 - (8 * i))
        id_list.append(id)
    print(f"Calculated IDs: {id_list}")

    # generate rk
    print("Generating rekey...")
    rk_list = GenerateReKey(sk, pk_B, len(node_ips), shreshold, tuple(id_list))  # type: ignore
    print(f"Generated ReKey: {rk_list}")

    capsule, ct = Encrypt(pk, message)  # type: ignore
    # capsule_ct = (capsule, int.from_bytes(ct))

    for i in range(len(node_ips)):
        url = "http://" + node_ips[i][0] + ":8001" + "/user_src"
        payload = {
            "source_ip": local_ip,
            "dest_ip": dest_ip,
            "capsule": capsule,
            "ct": int.from_bytes(ct),
            "rk": rk_list[i],
        }
        print(f"Sending payload to {url}:")
        print(json.dumps(payload))
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print(f"send to {node_ips[i]} successful")
        else:
            print(f"send to {node_ips[i]} failed with status code {response.status_code}")

    print("Function send_messages executed successfully!")
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
    print("Starting function: request_message")
    
    global message, node_response, pk
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

    print(f"Requesting message from: {url}")
    try:
        response = requests.post(url, json=payload, timeout=1)
        print(f"Response received from {url}: {response.text}")

    except requests.Timeout as e:
        print(f"Request to {url} timed out!")
        print("can't post")

    # wait 2s to receive message from nodes
    for _ in range(10):
        print(f"Waiting for response... (iteration {_ + 1})")
        print("Current node_response:", node_response)
        if node_response:
            data = message
            
            # reset message and node_response
            print("Resetting message and node_response...")
            message = b""
            node_response = False

            # return message to frontend
            print("Returning message to frontend:", str(data))
            return {"message": str(data)}
        await asyncio.sleep(0.2)

    print("Timeout occurred while waiting for response.")
    content = {"message": "receive timeout"}
    return JSONResponse(content, status_code=400)



# request message from others
@app.post("/request_message")
async def request_message(i_m: Request_Message):
    print("Starting function: request_message")
    
    global message, node_response, pk
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

    print(f"Requesting message from: {url}")
    try:
        response = requests.post(url, json=payload, timeout=1)
        print(f"Response received from {url}: {response.text}")

    except requests.Timeout as e:
        print(f"Request to {url} timed out!")
        print("can't post")

    # wait 2s to receive message from nodes
    for _ in range(10):
        print(f"Waiting for response... (iteration {_ + 1})")
        print("Current node_response:", node_response)
        if node_response:
            data = message
            
            # reset message and node_response
            print("Resetting message and node_response...")
            message = b""
            node_response = False

            # return message to frontend
            print("Returning message to frontend:", str(data))
            return {"message": str(data)}
        await asyncio.sleep(0.2)

    print("Timeout occurred while waiting for response.")
    content = {"message": "receive timeout"}
    return JSONResponse(content, status_code=400)



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

@app.post("/recieve_pk")
async def recieve_pk(pk: pk_model):
    print("Starting function: recieve_pk")
    
    pkx = pk.pkx
    pky = pk.pky
    dest_ip = pk.ip
    
    print(f"Received pkx: {pkx}, pky: {pky}, IP: {dest_ip}")

    try:
        threshold = 2
        print("Connecting to client.db...")
        with sqlite3.connect("client.db") as db:
            print("Connected to client.db, inserting data...")
            db.execute(
                """
        INSERT INTO senderinfo
        (ip, pkx, pky, threshold)
        VALUES
        (?, ?, ?, ?)
        """,
                (str(dest_ip), pkx, pky, threshold),
            )
            print("Data inserted successfully!")
    except Exception as e:
        # raise error
        print("Database error:", str(e))
        content = {"message": "Database Error", "error": str(e)}
        return JSONResponse(content, status_code=400)

    print("Function recieve_pk executed successfully!")
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
=======
>>>>>>> parent of 7b6e456 (feat: init client)
