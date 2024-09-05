from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3
import asyncio
import time
import ipaddress
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init()
    yield
    clean_env()


app = FastAPI(lifespan=lifespan)


def init():
    asyncio.create_task(receive_heartbeat_internal())
    init_db()


def init_db():
    conn = sqlite3.connect("server.db")
    cursor = conn.cursor()
    # init table: id: int; ip: TEXT
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    last_heartbeat INTEGER
                )"""
    )


def clean_env():
    clear_database()


# -----------------------------------------------------------------------------------------------


@app.get("/")
async def home():
    return {"message": "Hello, World!"}


@app.get("/server/show_nodes")
async def show_nodes() -> list:
    nodes_list = []
    with sqlite3.connect("server.db") as db:
        # 查询数据
        cursor = db.execute("SELECT * FROM nodes")
        rows = cursor.fetchall()

    for row in rows:
        nodes_list.append(row)
    # TODO: use JSONResponse
    return nodes_list


def validate_ip(ip: str) -> bool:
    """
    Validate an IP address.

    This function checks if the provided string is a valid IP address.
    Both IPv4 and IPv6 are considered valid.

    Args:
        ip (str): The IP address to validate.

    Returns:
        bool: True if the IP address is valid, False otherwise.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


@app.get("/server/get_node")
async def get_node(ip: str) -> int:
    """
    中心服务器与节点交互, 节点发送ip, 中心服务器接收ip存入数据库并将ip转换为int作为节点id返回给节点
    params:
    ip: node ip
    return:
    id: ip按点分割成四部分, 每部分转二进制后拼接再转十进制作为节点id
    """
    if not validate_ip(ip):
        content = {"message": "invalid ip "}
        return JSONResponse(content, status_code=400)  # type: ignore

    ip_parts = ip.split(".")
    ip_int = 0
    for i in range(4):
        ip_int += int(ip_parts[i]) << (24 - (8 * i))

    # TODO: replace print with logger
    print("IP", ip, "对应的ID为", ip_int)

    # 获取当前时间
    current_time = int(time.time())
    # TODO: replace print with logger
    print("当前时间: ", current_time)

    with sqlite3.connect("server.db") as db:
        # 插入数据
        db.execute(
            "INSERT INTO nodes (id, ip, last_heartbeat) VALUES (?, ?, ?)",
            (ip_int, ip, current_time),
        )
        db.commit()

    # TODO: use JSONResponse
    return ip_int


# TODO: try to use @app.delete("/node")
@app.get("/server/delete_node")
async def delete_node(ip: str):
    """
    Delete a node by ip.

    Args:
        ip (str): The ip of the node to be deleted.

    """

    with sqlite3.connect("server.db") as db:
        # 查询要删除的节点
        cursor = db.execute("SELECT * FROM nodes WHERE ip=?", (ip,))
        row = cursor.fetchone()
    if row is not None:
        with sqlite3.connect("server.db") as db:
            # 执行删除操作
            db.execute("DELETE FROM nodes WHERE ip=?", (ip,))
            db.commit()

        # TODO: replace print with logger
        print(f"Node with IP {ip} deleted successfully.")
        return {"message", f"Node with IP {ip} deleted successfully."}
    else:
        print(f"Node with IP {ip} not found.")
        raise HTTPException(status_code=404, detail=f"Node with IP {ip} not found.")


# 接收节点心跳包
@app.get("/server/heartbeat")
async def receive_heartbeat(ip: str):
    """
    Receive a heartbeat from a node.

    Args:
        ip (str): The IP address of the node.

    Returns:
        JSONResponse: A message indicating the result of the operation.
    """
    if not validate_ip(ip):
        content = {"message": "invalid ip format"}
        return JSONResponse(content, status_code=400)
    print("收到来自", ip, "的心跳包")
    logger.info("收到来自", ip, "的心跳包")

    with sqlite3.connect("server.db") as db:
        db.execute(
            "UPDATE nodes SET last_heartbeat = ? WHERE ip = ?", (time.time(), ip)
        )
    content = {"status": "received"}
    return JSONResponse(content, status_code=200)


async def receive_heartbeat_internal():
    timeout = 70
    while 1:
        with sqlite3.connect("server.db") as db:
            # 删除超时的节点
            db.execute(
                "DELETE FROM nodes WHERE last_heartbeat < ?", (time.time() - timeout,)
            )
            db.commit()
        await asyncio.sleep(timeout)


@app.get("/server/send_nodes_list")
async def send_nodes_list(count: int) -> list:
    """
    中心服务器与客户端交互, 客户端发送所需节点个数, 中心服务器从数据库中顺序取出节点封装成list格式返回给客户端
    params:
    count: 所需节点个数
    return:
    nodes_list: list
    """
    nodes_list = []

    with sqlite3.connect("server.db") as db:
        # 查询数据库中的节点数据
        cursor = db.execute("SELECT * FROM nodes LIMIT ?", (count,))
        rows = cursor.fetchall()

    for row in rows:
        # id, ip, last_heartbeat = row
        _, ip, _ = row
        nodes_list.append(ip)

    print("收到来自客户端的节点列表请求...")
    print(nodes_list)
    # TODO: use JSONResponse
    return nodes_list


def clear_database() -> None:
    with sqlite3.connect("server.db") as db:
        db.execute("DELETE FROM nodes")
        db.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
