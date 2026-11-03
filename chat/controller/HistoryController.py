from chat.service import HistoryService
from chat.entity.HistoryRequest import HistoryRequest
from fastapi import APIRouter

history_router = APIRouter()

#获取用户对话列表
@history_router.get("/list")
def find_history_by_user_id(userId):
    return HistoryService.find_history_by_user_id(userId)

#加载对话信息
@history_router.get("/Messages")
def find_messages_by_history_id(historyId):
    return HistoryService.find_message_by_history_id(historyId)

#保存聊天记录
@history_router.post("/Save")
def save_history(request: HistoryRequest):
    return HistoryService.save_history(request)

#搜索聊天记录
@history_router.get("/Search")
def search_history(userId:int,keyword:str):
    return HistoryService.search_history(userId, keyword)

#删除对话
@history_router.delete("/Delete")
def delete_history(historyId:int):
    return HistoryService.delete_history_by_root_id(historyId)


