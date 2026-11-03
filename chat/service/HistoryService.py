from chat.dao import HistoryDao
from common import ResponseUtil

def find_history_by_user_id(user_id):
    result = HistoryDao.find_history_by_user_id(user_id)
    history_list = []
    for item in result:
      history_list.append({
    'historyId': item['history_id'],
    'question': item['question'],
    'parentId': item['parent_id'],
    'answer': item['answer'],
    'createTime': item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
    })
    return ResponseUtil.response_json(200, "success", history_list)

def find_message_by_history_id(history_id):
    result = HistoryDao.find_messages_by_history_id(history_id)
    messages = []
    for item in result:
      if item.get('question'):
          messages.append({'role':'user','content':item['question']})
      if item.get('answer'):
          messages.append({'role':'assistant','content':item['answer']})

    return ResponseUtil.response_json(200, "success", messages)


def save_history(request):
    try :
        new_id= HistoryDao.insert_history(
            question=request.question,
            answer=request.answer,
            parent_id=request.parentId,
            user_id=request.userId,
        )
        return ResponseUtil.response_json(200, "success", new_id)
    except Exception as e:
        print(f"保存历史记录出错：{e}")
        return ResponseUtil.response_json(500, "error",None)

def search_history(user_id,keyword):
    result = HistoryDao.search_history_by_keyword(user_id,keyword)
    history_list = []
    for item in result:
     history_list.append({
    'historyId': item['history_id'],
    'question': item['question'],
    'answer': item['answer'],
    'parentId': item['parent_id'],
    'createTime': item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
    })
    return ResponseUtil.response_json(200, "success", history_list)

def delete_history_by_root_id(history_id):
   try:
       HistoryDao.delete_history_root_id(history_id)
       return ResponseUtil.response_json(200, "success", None)
   except Exception as e:
       print(f"删除历史记录出错：{e}")
       return ResponseUtil.response_json(200, "删除失败", None)
