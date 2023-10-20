from fastapi import FastAPI, HTTPException
import requests
import os
from typing import Tuple
from tpre import *
import sqlite3
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clean_env()


app = FastAPI(lifespan=lifespan)

pk = point
sk = int


def init():
    global pk, sk
    init_db()
    pk, sk = GenerateKeyPair()
    get_node_list(6)


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


# execute on exit
def clean_env():
    print("Exit app")


# main page
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


# receive messages from node
@app.post("/receive_messages")
async def receive_messages(C: Tuple[capsule, int], ip: str):
    """
    receive capsule and ip from nodes
    params:
    C: capsule and ct
    ip: sender ip
    return:

    """
    if not C or not ip:
        raise HTTPException(status_code=400, detail="Invalid input data")

    capsule, ct = C
    if not Checkcapsule(capsule):
        raise HTTPException(status_code=400, detail="Invalid capsule")

    # insert record into database
    with sqlite3.connect("message.db") as db:
        try:
            db.execute(
                "INSERT INTO message (capsule_column, ct_column, ip_column) VALUES (?, ?, ?)",
                (capsule, ct, ip),
            )
            db.commit()
            await check_merge(db, ct, ip)
            return HTTPException(status_code=200, detail="Message received")
        except Exception as e:
            print(f"Error occurred: {e}")
            db.rollback()
            return HTTPException(status_code=400, detail="Database error")


# check record count
async def check_merge(db, ct: int, ip: str):
    global sk, pk
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

    # get N
    cursor = db.execute(
        """
    SELECT publickey, threshold 
    FROM senderinfo
    WHERE senderip = ?
    """,
        (ip),
    )
    result = cursor.fetchall()
    pk_sender, T = result[0]
    if len(cfrag_cts) >= T:
        cfrags = mergecfrag(cfrag_cts)
        m = DecryptFrags(sk, pk, pk_sender, cfrags)  # type: ignore


# send message to node
@app.post("/send_message")
async def send_message(ip: tuple[str, ...]):
    return 0


# request message from others
@app.post("/request_message")
async def request_message(ip):
    return 0

# get node list from central server
def get_node_list(count: int):
    server_addr = ""
    url = "http://" + server_addr + "/server/send_nodes_list"
    payload = {"count": count}
    response = requests.post(url, json=payload)
    # Checking the response
    if response.status_code == 200:
        print("Success get node list")
        node_ip = response.text
        # insert node ip to database
        with sqlite3.connect("client.db") as db:
            db.executemany(
                """
                INSERT INTO node 
                nodeip 
                VALUE (?)
                """,
                node_ip,
            )
            db.commit()
        print("Success add node ip")
    else:
        print("Failed:", response.status_code, response.text)


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("client:app", host="0.0.0.0", port=8000)
