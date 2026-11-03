import os
import sys

# 将项目根目录加入sys.path
sys.path.insert(0, os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
))

os.environ['HF_HUB_OFFLINE'] = '1'

import pandas as pd
from langchain_chroma import Chroma
from langchain_core.documents import Document
from chat.util.DashScopeEmbeddings import DashScopeEmbeddings
from chromadb import PersistentClient

# 硬编码配置，修改此处可以切换数据集
path_base = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
dataset_path = os.path.join(path_base, "datasets")
csv_file = "法律数据集.csv"  # <=修改此处可以修改数据集
embedding_model_path = os.path.join(path_base, "models", "embedding_model")
chromadb_data_path = os.path.join(path_base, "chromadb_data", "law_knowledge_base")
chromadb_data_name = 'law_knowledge_base'


def build_base():
    # 读取CSV，向量化，存入ChromaDB
    csv_path = os.path.join(dataset_path, csv_file)
    print(f"读取数据集：{csv_path}")

    df = pd.read_csv(csv_path)
    data = df.values.tolist()
    documents = [Document(page_content=str(item[0]))
                 for item in data if str(item[0]).strip()]
    print(f"有效文档数：{len(documents)}")

    embedding_model = DashScopeEmbeddings(
        api_key=os.getenv("DASHSCOPE_API_KEY"),

    )

    Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=chromadb_data_path,
        collection_name=chromadb_data_name,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print("知识库构建完成")


def check_and_build():
    """检查向量库是否为空"""
    client = PersistentClient(path=chromadb_data_path)
    try:
        collection = client.get_collection(chromadb_data_name)
        count = collection.count()
        if count == 0:
            print(f"集合 '{chromadb_data_name}' 为空，开始构建...")
            build_base()
        else:
            print(f"集合 '{chromadb_data_name}' 已有 {count} 条数据，跳过构建")
    except Exception:
        print(f"集合 '{chromadb_data_name}' 不存在，开始构建...")
        build_base()


if __name__ == '__main__':
    check_and_build()