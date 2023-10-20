from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Tuple, Callable

app = FastAPI()

@app.get("/server/get_node")
async def get_node(ip: str) -> int:
    '''
    中心服务器与节点交互, 节点发送ip, 中心服务器接收ip存入数据库并将ip转换为int作为节点id返回给节点
    params:
    ip: node ip
    return:
    id: ip按点分割成四部分, 每部分转二进制后拼接再转十进制作为节点id
    '''
    # ip存入数据库, id = hash(int(ip))

    ip_parts = ip.split(".")
    ip_int = 0
    for i in range(4):
        ip_int += int(ip_parts[i]) << (24 - (8 * i))
    return ip_int

@app.get("/server/delete_node")
async def delete_node(ip: str) -> None:
    # 按照节点ip遍历数据库, 删除该行数据

@app.post("/server/send_nodes_list")
async def send_nodes_list(count: int) -> JSONResponse:
    '''
    中心服务器与客户端交互, 客户端发送所需节点个数, 中心服务器从数据库中顺序取出节点封装成json格式返回给客户端
    params:
    count: 所需节点个数
    return:
    JSONResponse: {id: ip,...}
    '''
    nodes_list = {}
    for i in range(count):
        # 访问数据库取出节点数据
        node = (id, ip)
        nodes_list[node[0]] = node[1]
    json_result = jsonable_encoder(nodes_list)
    return JSONResponse(content=json_result)