# 法律知识问答系统（law-qa-system）

基于 **RAG（检索增强生成）** 的法律智能问答系统。用户提问后，系统从本地法律知识库中检索相关法条，经重排序后交由大模型生成准确、有依据的回答，并提供流式聊天界面与用户登录、历史记录功能。

## 核心功能

- **法律知识库问答**：基于 ChromaDB 向量库存储法律条文，检索 top-10 相关片段
- **Rerank 重排序**：调用阿里云百炼 `qwen3-rerank` 对检索结果二次排序，取 top-3 高相关法条
- **流式输出（SSE）**：问答过程逐字流式返回，前端实时渲染
- **多轮对话**：支持携带最近 6 条对话历史，结合上下文追问
- **用户登录与会话历史**：MySQL 存储用户与问答历史记录
- **Web 聊天界面**：Vue + Element UI 前端页面，支持流式聊天与历史加载

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 后端框架 | Python + FastAPI + Uvicorn |
| LLM 应用框架 | LangChain（LCEL 链式编排） |
| 向量数据库 | ChromaDB（本地持久化，cosine 相似度） |
| 大模型 | 阿里云百炼 `qwen3.7-plus`（OpenAI 兼容接口） |
| 重排序 | 阿里云百炼 `qwen3-rerank` |
| 向量化 | 阿里云百炼 DashScope Embedding |
| 数据库 | MySQL（pymysql，库名 `feifan_ai`） |
| 前端 | Vue 2 + Element UI + Axios + marked（CDN 静态资源） |
| 对话协议 | SSE（Server-Sent Events）流式输出 |

## 目录结构

```
├── main.py                 # FastAPI 入口（端口 8000）
├── ai/
│   └── models/             # 大模型加载（LoadALYModel）
├── chat/
│   ├── controller/         # 路由（ChatController / HistoryController）
│   ├── service/            # RAG 问答与历史服务
│   ├── dao/                # 历史记录数据访问
│   ├── entity/             # 请求实体
│   └── util/               # ChromaDB 工具、知识库构建、Embedding 封装
├── users/
│   ├── controller/         # 用户登录注册路由
│   ├── service/            # 用户服务
│   ├── dao/                # 用户数据访问
│   └── entity/             # 用户实体
├── common/                 # MySQL 连接、统一响应封装
├── static/                 # 前端静态资源（axios / element-ui / vue / marked）
├── templates/              # 登录页 login.html、聊天页 chat_stream.html
├── datasets/               # 法律数据集（不入库，git 已忽略）
├── models/                 # 本地模型权重（不入库，git 已忽略）
├── chromadb_data/          # 向量库持久化目录（不入库，git 已忽略）
└── output/                 # 报告等输出文档（不入库，git 已忽略）
```

## 快速启动

### 1. 安装依赖

```bash
pip install fastapi uvicorn langchain langchain-openai langchain-core langchain-chroma chromadb pymysql pandas requests jinja2
```

### 2. 配置环境变量

```bash
# 阿里云百炼 API Key（用于大模型 / Embedding / Rerank）
set DASHSCOPE_API_KEY=sk-xxxx

# MySQL root 密码（连接本地库 feifan_ai）
set BASE_PASSWORD=your_password
```

> 建议将上述配置写入 `.env` 或系统环境变量，避免明文泄露。

### 3. 准备向量知识库

首次运行需先构建法律知识库（读取 `datasets/法律数据集.csv` 向量化写入 ChromaDB）：

```bash
python chat/util/BuildLawBase.py
```

### 4. 启动服务

```bash
python main.py
```

访问 `http://localhost:8000/login` 登录后即可使用聊天界面。

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/login` | 登录页面 |
| GET | `/chat/goChatStream` | 流式聊天页面 |
| GET | `/chat/chatStream?question=...&history=...` | 流式问答（SSE） |
| GET | `/chat/chatNoStream?question=...&history=...` | 非流式问答 |
| GET | `/history/...` | 对话历史查询 |
| POST | `/users/...` | 用户注册 / 登录 |

## 注意事项

- 模型、向量库、数据集均不随仓库提交，部署时需按上述步骤自行准备
- 回答严格基于检索到的法律条文，不编造法条；涉及具体维权请咨询专业律师
