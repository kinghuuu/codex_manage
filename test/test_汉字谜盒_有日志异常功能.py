import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel
import logging

# 日志配置
# %(asctime)s: 时间  %(levelname)s: 日志级别  %(filename)s: 文件名  %(lineno)d: 行号  %(message)s: 日志信息
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# 创建FastAPI实例
app = FastAPI(title="汉字谜盒")


sessions_dir = Path(__file__).parent / "sessions_dir"  # 获取当前文件所在目录下的 sessions_dir 路径

if not sessions_dir.exists():
    sessions_dir.mkdir(exist_ok=True)  # exist_ok=True 表示如果目录已存在也不会报错


# 生成会话的标识
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 数据模型
class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any  # 表示任意类型


# 新建会话
# BaseModel： 是Pydantic库提供的父类（FastAPI 深度集成了 Pydantic），用于定义FastAPI数据模型和数据验证规则。
@app.post("/api/sessions")
def create_session() -> ApiResponse:
    logging.info("创建会话")
    session_id = generate_session_id()
    session_data = {
        "current_session": session_id,
        "messages": []
    }
    with open(f"sessions_dir/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    return ApiResponse(code=200, message="创建会话成功", data=session_id)


# 数据模型
class ChatRequest(BaseModel):
    session_id: str
    message: str


# 系统提示词
SYSTEM_PROMPT = """
    你是一个专门玩猜字谜的AI小助手，只进行字谜互动，不闲聊无关内容，全程纯文本交互。
    请严格遵守以下规则：
    一、出题规则
        开场先友好打招呼，并随机出一道常见、简单、适合大众的字谜，不生僻、不低俗、不使用网络烂梗。
        题目格式：“谜面”（打一字）。
        每次出题必须完全随机，禁止重复使用相同题目；你需要在对话上下文中主动记录已使用过的谜语，确保同一会话内绝对不重复。
        避免使用高频重复的经典老谜语，尽量选择多样化的中等常见谜语。
    
    二、【判题规则（最重要！）】
        判题时，只看用户输入中的核心汉字，忽略无关内容：
        比如用户输入“江字”“江”“jiang”，都视为答案是「江」；
        用户输入“是江吗？”“应该是江”，也视为答案是「江」。
        核心字与正确答案完全一致 → 判为正确，回复：“太棒了！答对了！就是‘XX’字！要不要再来一题？”
        核心字与正确答案不一致 → 判为错误，回复：“不对哦，再想想~ 给你个小提示：[简短线索，不泄露答案]”
        用户说“不知道”“公布答案”：先揭晓谜底和解释，再问“要不要再来一题？”
    
    三、互动流程
        用户答对：夸奖 + 确认正确 + 询问“要不要再来一题？”
        用户答错：告知不对 + 简单提示 + 鼓励继续猜
        用户说“提示一下”：给出简短线索，不公布答案
        用户说“公布答案”或“不知道”：揭晓谜底并解释 + 询问“要不要再来一题？”
        用户说“换一题”“再来一题”：立即更换新字谜
    
    四、其他要求
        语气轻松有趣、简洁明快，不啰嗦。
        全程只围绕字谜，不回答其他问题、不聊无关话题。
        不使用多余表情符号，保持简洁。
        若用户答案与正确答案仅差一字或笔画，请仔细核对是否正确。
        
    请严格按以上规则回复，优先保证谜语的随机性和多样性。
"""


# 根据session_id获取文件名
def get_session_file_name(session_id: str) -> str:
    return f"sessions_dir/{session_id}.json"


# 创建与AI大模型交互的客户端对象（DEEPSEEK_API_KEY环境变量的名称，值就是Deepseek的API_KEY）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# 与AI交互
@app.post("/api/chat")
def chat(request: ChatRequest) -> ApiResponse:
    # 1.加载JSON文件中的会话数据
    session_path = get_session_file_name(request.session_id)
    with open(session_path, "r", encoding="utf-8") as f:
        session_data = json.load(f)

    # 2.构建AI大模型交互的消息数据
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for message in session_data["messages"]:
        messages.append(message)
    messages.append({"role": "user", "content": request.message})

    # 3.调用AI大模型 Deepseek
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False,
        temperature=0.7
    )

    # 4.获取响应的数据
    content = response.choices[0].message.content

    # 5.更新消息列表中的消息
    messages.pop(0)  # 删除系统提示词
    messages.append({"role": "assistant", "content": content})
    session_data["messages"] = messages

    # 6.保存会话信息到JSON文件中
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    # 7.返回数据
    return ApiResponse(code=200, message="请求成功!", data=content)


# 获取会话列表
@app.get("/api/sessions")
def get_sessions() -> ApiResponse:
    session_files = [file for file in os.listdir("sessions_dir") if file.endswith(".json")]

    session_ids = [file.split(".")[0] for file in session_files]
    session_ids.sort(reverse=True)

    return ApiResponse(code=200, message="获取会话列表成功", data=session_ids)


# 获取指定的会话信息
@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> ApiResponse:
    session_file_name = get_session_file_name(session_id)
    with open(session_file_name, "r", encoding="utf-8") as f:
        session_data = json.load(f)

    return ApiResponse(code=200, message="获取会话信息成功", data=session_data)


# 删除指定的会话
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str) -> ApiResponse:
    logging.info(f"删除会话：{session_id}")
    session_file_name = get_session_file_name(session_id)
    os.remove(session_file_name)
    return ApiResponse(code=200, message="删除会话成功", data=None)


# 统一异常信息处理
@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    logging.error(f"处理异常：{request.method} {request.url}，异常信息： {exc}")
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误", "data": None})


# 启动服务
# host设置成 0.0.0.0 允许同一个局域网下的其他人也能访问这个服务，方便团队协作
# 如果把代码放到云服务器上，必须用 0.0.0.0，外网用户才能访问到这个服务。
# 而 127.0.0.1 只能本机访问
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
