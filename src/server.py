from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3
import asyncio
import time
import ipaddress


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clean_env()


app = FastAPI(lifespan=lifespan)


def init():
    asyncio.create_task(receive_heartbeat_internal())

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
    return nodes_list


def validate_ip(ip: str) -> bool:
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
    print("IP", ip, "对应的ID为", ip_int)

    # 获取当前时间
    current_time = int(time.time())
    print("当前时间: ", current_time)

    with sqlite3.connect("server.db") as db:
        # 插入数据
        db.execute(
            "INSERT INTO nodes (id, ip, last_heartbeat) VALUES (?, ?, ?)",
            (ip_int, ip, current_time),
        )
        db.commit()

    return ip_int


@app.get("/server/delete_node")
async def delete_node(ip: str) -> None:
    """
    param:  
    ip: 待删除节点的ip地址  
    return:  
    None  
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
        print(f"Node with IP {ip} deleted successfully.")
    else:
        print(f"Node with IP {ip} not found.")


# 接收节点心跳包
@app.get("/server/heartbeat")
async def receive_heartbeat(ip: str):
    if not validate_ip(ip):
        content = {"message": "invalid ip "}
        return JSONResponse(content, status_code=400)
    print("收到来自", ip, "的心跳包")
    with sqlite3.connect("server.db") as db:
        db.execute(
            "UPDATE nodes SET last_heartbeat = ? WHERE ip = ?", (time.time(), ip)
        )
    return {"status": "received"}


async def receive_heartbeat_internal():
    while 1:
        timeout = 70
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
        id, ip, last_heartbeat = row
        nodes_list.append(ip)

    print("收到来自客户端的节点列表请求...")
    print(nodes_list)
    return nodes_list


# @app.get("/server/clear_database")
def clear_database() -> None:
    with sqlite3.connect("server.db") as db:
        db.execute("DELETE FROM nodes")
        db.commit()


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
