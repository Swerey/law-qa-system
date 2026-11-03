from fastapi import APIRouter, Request
from tempfile import template
from chat.service import ChatService
from starlette.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import json

chat_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@chat_router.get("/chatNoStream")
def chat_no_stream(question: str,history:str=None):
    history_message =None
    if history:
        try:
            history_message = json.loads(history)
        except json.JSONDecodeError:
            pass #解析失败就忽略，降级为无历史模式
    return ChatService.chat_no_stream(question,history_message)


@chat_router.get("/chatStream")
def chat_stream(question: str,history:str=None):
    history_message =None
    if history:
        try:
            history_message = json.loads(history)
        except json.JSONDecodeError:
            pass #

    def generator():
        for chunk in ChatService.chat_stream(question,history_message):
            # 尝试获取 content 属性，若不存在则直接转为字符串
            content = getattr(chunk, 'content', str(chunk))
            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'content': '[DONE]'}, ensure_ascii=False)}\n\n"
    return StreamingResponse(
        content=generator(),  # 传入生成器对象
        media_type="text/event-stream",  # 默认使用html
    )


# 页面路由
@chat_router.get("/goChatStream", response_class=HTMLResponse)
def go_chat_stream(request: Request):
    # 访问流式聊天界面
    return templates.TemplateResponse(request, "chat_stream.html")