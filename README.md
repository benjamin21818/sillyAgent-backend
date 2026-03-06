# sillyAgent-backend

sillyAgent-backend 是一个基于 Python 的多智能体（Multi-Agent）后端服务，旨在提供智能对话、工具调用和知识检索能力。项目利用 `LangGraph` 构建智能体工作流，结合 `FastAPI` 提供高性能的 Web 服务接口。

## ✨ 核心特性

*   **多智能体架构**：
    *   **Manager Agent**: 智能路由中心，根据用户意图将任务分发给最合适的子智能体（Tool, RAG, 或 LLM）。
    *   **Tool Agent**: 专注于执行外部工具调用，目前集成了丰富的高德地图（AMap）技能（路线规划、天气、POI搜索等）和网络搜索能力。
    *   **RAG Agent**: 检索增强生成，基于本地知识库提供准确的问答服务。
    *   **LLM Agent**: 处理通用对话和常识性问题。
*   **先进的记忆系统**：
    *   集成 `Mem0`，支持基于向量（PostgreSQL/pgvector）和图谱（Neo4j）的混合记忆存储。
    *   本地 SQLite 历史记录管理。
*   **现代化技术栈**：
    *   基于 `FastAPI` 和 `Uvicorn` 的异步 Web 服务。
    *   使用 `uv` 进行高效的依赖管理。
    *   集成 `DeepSeek` 等大语言模型。

## 🛠️ 前置要求

*   **Python**: >= 3.12
*   **PostgreSQL**: 需要安装 `pgvector` 插件。
*   **Neo4j**: 用于图谱记忆存储。
*   **HuggingFace 模型**: 需要下载 `bge-large-zh-v1.5` 到 `src/models/` 目录（或配置为在线加载）。

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository_url>
cd sillyAgent-backend
```

### 2. 环境配置与依赖安装

推荐使用 `uv` 进行依赖管理，也可以使用 `pip`。

**使用 uv (推荐):**

```bash
# 安装 uv (如果尚未安装)
pip install uv

# 同步依赖
uv sync
```

**使用 pip:**

```bash
pip install -e .
```

### 3. 配置文件 (.env)

在项目根目录下创建 `.env` 文件，并参考以下配置填写：

```ini
# LLM Configuration (DeepSeek)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Embedding Configuration
# 默认使用本地模型: src/models/bge-large-zh-v1.5
EMBEDDING_DIMS=1024

# Vector Store (PostgreSQL with pgvector)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_db_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_COLLECTION_NAME=your_collection_name

# Graph Store (Neo4j)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 4. 启动服务

使用 `run_server.py` 启动后端服务：

```bash
python run_server.py
```

或者自定义参数启动：

```bash
python run_server.py --host 0.0.0.0 --port 8000 --reload
```

启动成功后，访问 API 文档：
*   Swagger UI: `http://127.0.0.1:8000/docs`
*   ReDoc: `http://127.0.0.1:8000/redoc`

## 📂 项目结构

```
sillyAgent-backend/
├── src/
│   ├── backend/          # FastAPI 应用及 API 路由
│   ├── llm/              # LLM 基础封装
│   ├── multi_agent/      # 多智能体核心逻辑
│   │   ├── agents/       # 各类智能体实现 (Manager, Tool, RAG, LLM)
│   │   ├── skills/       # 工具/技能定义 (高德地图, Web搜索等)
│   │   └── statetype/    # LangGraph 状态定义
│   ├── utils/            # 通用工具函数
│   └── models/           # 本地模型存放目录 (如 bge-large-zh-v1.5)
├── config.py             # 项目配置加载
├── run_server.py         # 服务启动脚本
├── pyproject.toml        # 项目依赖配置
└── uv.lock               # 依赖锁定文件
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！
