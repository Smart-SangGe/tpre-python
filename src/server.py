from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
import asyncio
import time
import ipaddress
import logging
import os
import queue

app = FastAPI()

origins = [
    "http://localhost:3000",
]

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 配置日志文件路径

log_dir = os.path.expanduser("~/tpre-python-logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "server_logs.log")

# 全局日志配置
logging.basicConfig(
    level=logging.INFO,  # 设置全局日志级别
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),  # 输出到日志文件
        logging.StreamHandler(),  # 输出到控制台
    ],
)

# 获取日志记录器
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init()
    yield
    clean_env()


# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义 frontend 的绝对路径
frontend_dir = os.path.join(current_dir, "..", "frontend","build")

app = FastAPI(lifespan=lifespan)
app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


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
    logger.info("节点信息已成功获取")
    return nodes_list


@app.get("/nodes", response_class=HTMLResponse)
async def get_nodes_page():
    with open("frontend/public/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


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
async def get_node(ip: str) -> JSONResponse:
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

    logger.info(f"IP {ip} 对应的ID为 {ip_int}")

    # 获取当前时间
    current_time = int(time.time())
    logger.info(f"当前时间: {current_time}")

    with sqlite3.connect("server.db") as db:
        # 插入数据
        db.execute(
            "INSERT INTO nodes (id, ip, last_heartbeat) VALUES (?, ?, ?)",
            (ip_int, ip, current_time),
        )
        db.commit()

    # 使用 JSONResponse 返回节点ID和当前时间
    logger.info(f"节点 {ip} 已成功添加到数据库")
    content = {"id": ip_int, "current_time": current_time}
    return JSONResponse(content, status_code=200)


# TODO: try to use @app.delete("/node")
@app.get("/server/delete_node")
async def delete_node(ip: str):
    """
    Delete a node by ip.

    Args:
        ip (str): The ip of the node to be deleted.

    """
    if not validate_ip(ip):
        logger.warning(f"收到无效 IP 格式的删除请求: {ip}")
        raise HTTPException(status_code=400, detail="Invalid IP format")

    with sqlite3.connect("server.db") as db:
        # 查询要删除的节点
        cursor = db.execute("SELECT * FROM nodes WHERE ip=?", (ip,))
        row = cursor.fetchone()
    if row is not None:
        with sqlite3.connect("server.db") as db:
            # 执行删除操作
            db.execute("DELETE FROM nodes WHERE ip=?", (ip,))
            db.commit()

        logger.info(f"节点 {ip} 已成功删除")
        return {"message": f"Node with IP {ip} deleted successfully."}
    else:
        logger.warning(f"节点 {ip} 未找到")
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
        logger.warning(f"收到无效 IP 格式的心跳包: {ip}")
        return JSONResponse(content, status_code=400)
    logger.info(f"收到来自 {ip} 的心跳包")

    with sqlite3.connect("server.db") as db:
        db.execute(
            "UPDATE nodes SET last_heartbeat = ? WHERE ip = ?", (time.time(), ip)
        )
    logger.info(f"成功更新节点 {ip} 的心跳时间")
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

    logger.info(f"已成功发送 {count} 个节点信息")
    return nodes_list


def clear_database() -> None:
    with sqlite3.connect("server.db") as db:
        db.execute("DELETE FROM nodes")
        db.commit()
    logger.info("数据库已清空")


# WebSocket连接池
connected_clients = []
log_queue = queue.Queue()  # 用于存储日志的队列


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)  # 添加 WebSocket 客户端
    try:
        # 发送历史日志
        while not log_queue.empty():
            log_message = log_queue.get()
            await websocket.send_json({"type": "log", "message": log_message})

        # 实时日志发送
        while True:
            await asyncio.sleep(5)  # 保证 WebSocket 持续连接
    except Exception as e:
        print(f"WebSocket connection closed with error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        await websocket.close()


class WebSocketLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        log_message = f"{timestamp} - {log_entry}"
        log_queue.put(log_message)  # 将日志消息放入队列
        for client in connected_clients:
            if client.application_state == WebSocketState.CONNECTED:
                # 改为异步线程安全地发送日志
                asyncio.run_coroutine_threadsafe(
                    self.safe_send_log(client, log_message), asyncio.get_event_loop()
                )

    async def safe_send_log(self, client, log_message):
        try:
            await client.send_json({"type": "log", "message": log_message})
        except RuntimeError as e:
            print(f"Error while sending log to {client.application_state}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if client in connected_clients:
                connected_clients.remove(client)


# 捕获 FastAPI 和 Uvicorn 的日志
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)

# 捕获 FastAPI 的日志
fastapi_logger = logging.getLogger("fastapi")
fastapi_logger.setLevel(logging.INFO)

# 将日志输出到 WebSocket
uvicorn_logger.addHandler(WebSocketLogHandler())
fastapi_logger.addHandler(WebSocketLogHandler())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
