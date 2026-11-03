import os

from langchain_chroma import Chroma
from  chat.util.DashScopeEmbeddings import DashScopeEmbeddings

# 路径计算
path_base = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
# 路径验证
# print(path_base)

# 向量化模型的本地路径
embedding_model_path = os.path.abspath(
    os.path.join(path_base, "models", "embedding_model")
)
# 路径验证
# print(embedding_model_path)

# ChromaDB持久化存储路径
chromadb_data_path = os.path.abspath(
    os.path.join(path_base, "chromadb_data", "law_knowledge_base")
)
# 路径验证
# print(chromadb_data_path)

# ChromaDB集合名称
chromadb_data_name = 'law_knowledge_base'

def get_knowledge_conn():
    """连接向量数据库，返回可检索的Chroma对象"""
    embedding_model = DashScopeEmbeddings(
        api_key=os.getenv("DASHSCOPE_API_KEY"),

    )
    return Chroma(
        persist_directory=chromadb_data_path,
        collection_name=chromadb_data_name,
        embedding_function=embedding_model,
    )