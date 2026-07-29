from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

router = APIRouter(prefix="")

connections_chat: list[WebSocket] = []


# 明天看一下 多个人同时请求、然后退出 是什么样的

# 注意请求方法是websocket
@router.websocket("/ws/{name}")
async def ws(websocket: WebSocket, name: str):
    await websocket.accept()
    connections_chat.append(websocket)
    await websocket.send_text(f"{name}，你已经进入聊天室，可以说话啦！")
    try:
        while True:
            # 接收信息
            data = await websocket.receive_text()
            for client in connections_chat:
                await client.send_text(f"{name}说：{data}")
    except WebSocketDisconnect:
        print(f'{websocket} 断开连接。')
        if websocket in connections_chat:
            connections_chat.remove(websocket)
        for client in connections_chat:
            await client.send_text("有人退出了聊天")
