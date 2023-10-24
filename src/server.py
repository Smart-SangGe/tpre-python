from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3
import asyncio
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield
    clean_env()


app = FastAPI(lifespan=lifespan)

# 连接到数据库（如果数据库不存在，则会自动创建）
conn = sqlite3.connect("server.db")
# 创建游标对象，用于执行SQL语句
cursor = conn.cursor()
# 创建表: id: int; ip: TEXT
cursor.execute(
    """CREATE TABLE IF NOT EXISTS nodes (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   ip TEXT NOT NULL,
                   last_heartbeat INTEGER
               )"""
)


def init():
    asyncio.create_task(receive_heartbeat_internal())


def clean_env():
    clear_database()
    # 关闭游标和连接
    cursor.close()
    conn.close()


@app.get("/server/show_nodes")
async def show_nodes() -> list:
    nodes_list = []
    # 查询数据
    cursor.execute("SELECT * FROM nodes")
    rows = cursor.fetchall()
    for row in rows:
        nodes_list.append(row)
    return nodes_list


@app.get("/server/get_node")
async def get_node(ip: str) -> int:
    """
    中心服务器与节点交互, 节点发送ip, 中心服务器接收ip存入数据库并将ip转换为int作为节点id返回给节点
    params:
    ip: node ip
    return:
    id: ip按点分割成四部分, 每部分转二进制后拼接再转十进制作为节点id
    """
    ip_parts = ip.split(".")
    ip_int = 0
    for i in range(4):
        ip_int += int(ip_parts[i]) << (24 - (8 * i))

    # 获取当前时间
    current_time = int(time.time())

    # 插入数据
    cursor.execute(
        "INSERT INTO nodes (id, ip, last_heartbeat) VALUES (?, ?, ?)",
        (ip_int, ip, current_time),
    )
    conn.commit()

    return ip_int


@app.get("/server/delete_node")
async def delete_node(ip: str) -> None:
    """
    param:
    ip: 待删除节点的ip地址
    return:
    None
    """
    # 查询要删除的节点
    cursor.execute("SELECT * FROM nodes WHERE ip=?", (ip,))
    row = cursor.fetchone()
    if row is not None:
        # 执行删除操作
        cursor.execute("DELETE FROM nodes WHERE ip=?", (ip,))
        conn.commit()
        print(f"Node with IP {ip} deleted successfully.")
    else:
        print(f"Node with IP {ip} not found.")


# 接收节点心跳包
@app.get("/server/heartbeat")
async def receive_heartbeat(ip: str):
    cursor.execute(
        "UPDATE nodes SET last_heartbeat = ? WHERE ip = ?", (time.time(), ip)
    )
    return {"status": "received"}


async def receive_heartbeat_internal():
    while 1:
        timeout = 7
        # 删除超时的节点
        cursor.execute("DELETE FROM nodes WHERE last_heartbeat < ?", (time.time() - timeout,))
        conn.commit()
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

    # 查询数据库中的节点数据
    cursor.execute("SELECT * FROM nodes LIMIT ?", (count,))
    rows = cursor.fetchall()
    for row in rows:
        id, ip, last_heartbeat = row
        nodes_list.append(ip)

    return nodes_list


# @app.get("/server/clear_database")
def clear_database() -> None:
    cursor.execute("DELETE FROM nodes")
    conn.commit()


if __name__ == "__main__":
    import uvicorn  # pylint: disable=e0401

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
