import os
import requests
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda

from chat.controller.HistoryController import history_router
from chat.util import ChromaUtil
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ai.models import LoadALYModel
from common import ResponseUtil

# 路径设置（仅用于其他功能，当前未使用，可保留）
path_base = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
reranker_model_path = os.path.abspath(os.path.join(path_base, "models", "bge-reranker-large_v1"))

RAG_PROMPT_TEMPLATE = """你是一个专业的中国法律知识库智能问答助手。

请根据以下检索到的法律条文内容，准确、专业地回答用户的法律问题。

要求：
1. 只基于【法律条文】中提供的信息作答，不得编造法条
2. 如果条文不足以完全回答，明确指出"根据现有资料"可回答的范围
3. 回答应包含具体法律依据（法律名称、条款序号），引述需准确
4. 用清晰、易懂的语言解释，避免过于学术化
5. 涉及维权指引时，建议咨询专业律师

【法律条文】
{context}

【用户问题】
{question}

【你的回答】"""

def chat_no_stream(question,history_messages=None):
    chrome_db = ChromaUtil.get_knowledge_conn()
    retriever = chrome_db.as_retriever(search_kwargs={"k": 10})
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    #拼上历史对话
    if history_messages:
        history_text = ""
        for msg in history_messages[-6:]:
            role_label = "用户" if msg["role"] == "user" else "AI助手"
            history_text += f"{role_label}: {msg['content']}\n"
        context = f"【历史对话记录】\n{history_text}\n【法律参考资料】\n{context}"

    prompt = PromptTemplate(template=RAG_PROMPT_TEMPLATE, input_variables=["context", "question"])
    llm = LoadALYModel.load_model()
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context, "question": question})
    if response:
        return ResponseUtil.response_json(200, "success", response)
    return ResponseUtil.response_json(500, "fail", "没有应答")

def chat_stream(question,history_message=None):
    #构建对话历史文本
    history_text=""
    if history_message and len(history_message) > 0:
        recent =history_message[-6:]
        for msg in recent:
            role_label = "用户" if msg["role"] =="user" else "AI助手"
            history_text += f"{role_label}: {msg['content']}\n"

    chrome_db = ChromaUtil.get_knowledge_conn()
    retriever = chrome_db.as_retriever(search_kwargs={"k": 10})
    llm = LoadALYModel.load_model()
    prompt = PromptTemplate(template=RAG_PROMPT_TEMPLATE, input_variables=["context", "question"])

    try:
        # ---------- 使用百炼 Rerank API ----------
        def rerank(inputs):
            docs = inputs["context"]
            question_text = inputs["question"]
            if not docs:
                return {"context": "", "question": question_text}

            # 准备请求体（注意：不要加多余逗号）
            documents_list = [doc.page_content for doc in docs]
            requests_body = {
                "model": "qwen3-rerank",
                "input": {
                    "query": question_text,
                    "documents": documents_list,
                },
                "parameters": {
                    "top_n": 3,
                    "return_documents": False,
                }
            }

            print(f">>>开始重排序({len(docs)}篇 => top 3)...")
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise Exception("环境变量 DASHSCOPE_API_KEY 未设置")

            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=requests_body,
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f"Rerank API 请求失败，状态码 {response.status_code}：{response.text}")

            result = response.json()
            if "code" in result and result.get("code"):
                raise Exception(f"Rerank API 业务错误：{result.get('message', result)}")

            rerank_results = result["output"]["results"]  # 已按分数降序，且只有 top_n 条

            # 将分数写入 metadata
            for item in rerank_results:
                idx = item["index"]
                score = item["relevance_score"]
                docs[idx].metadata["relevance_score"] = round(float(score), 4)

            # 取 top-3（API 已保证顺序，直接取全部结果即可）
            final_docs = [docs[item["index"]] for item in rerank_results]

            # 打印重排序结果
            print("重排序完成：")
            for i, doc in enumerate(final_docs, 1):
                score = doc.metadata.get("relevance_score", "N/A")
                preview = doc.page_content[:80]
                suffix = "..." if len(doc.page_content) > 80 else ""
                print(f"[{i}] 相关度={score} | {preview}{suffix}")
                print("-" * 60)

            context_str = "\n\n".join(
                f"[来源{i}] {doc.page_content}" for i, doc in enumerate(final_docs, 1)
            )

            if history_text:
                context_str = (
                    f"【对话历史】\n{history_text}\n"
                    f"【法律参考资料】\n{context_str}"

                )

            return {"context": context_str, "question": question_text}

        # 构建含 Reranker 的 LCEL 链
        QA_chain = (
            RunnableParallel({
                "context": retriever,
                "question": RunnablePassthrough()
            })
            | RunnableLambda(rerank)
            | prompt
            | llm
            | StrOutputParser()
        )
        print("RAG链已就绪（含百炼 Reranker）")

    except Exception as e:
        print(f"Reranker 加载失败（{e}），降级为纯检索模式")

        # 降级方案：不使用 Reranker，直接取 top-5
        def format_docs(inputs):
            docs = inputs["context"]
            question_text = inputs["question"]
            if not docs:
                return {"context": "", "question": question_text}
            top_docs = docs[:5]
            context_str = "\n\n".join(
                f"[来源{i}] {doc.page_content}" for i, doc in enumerate(top_docs, 1)
            )

            #拼历史到法条前
            if history_text:
                context_str=(
                    f"【一下是你和用户之前的对话历史记录，请基于此历史理解用户的追问语境】\n"
                    f"{history_text}\n"
                    f"【以下是本次检索到的法律参考资料】\n"
                    f"{context_str}"
                )

            return {"context": context_str, "question": question_text}



        QA_chain = (
            RunnableParallel({
                "context": retriever,
                "question": RunnablePassthrough()
            })
            | RunnableLambda(format_docs)
            | prompt
            | llm
            | StrOutputParser()
        )
        print("RAG链已就绪（纯检索模式）")

    # 流式输出
    for chunk in QA_chain.stream(question):
        yield chunk