from fastapi import FastAPI, Request
import uvicorn
from chat.controller.ChatController import chat_router
from users.controller.UsersController import api_router
from chat.controller.HistoryController import history_router
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 挂载静态文件
app.mount("/static", app=StaticFiles(directory="static"), name="static")
# 挂载用户模块路由
app.include_router(router=api_router, prefix="/users", tags=["users"])
# 挂载聊天模块路由
app.include_router(router=chat_router, prefix="/chat", tags=["chat"])

app.include_router(router=history_router, prefix="/history", tags=["history"])


# 登录页面路由
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=False)