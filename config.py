import os
from pathlib import Path
from dotenv import load_dotenv
from mem0 import Memory

project_root = Path(__file__).resolve().parent
load_dotenv(project_root / ".env")
memory_dir = project_root / ".mem0"
memory_dir.mkdir(parents=True, exist_ok=True)


def get_config():
    return {
        "llm": {
            "provider": "deepseek",
            "config": {
                "model": "deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
            },
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                # "model": os.getenv("EMBEDDING_MODEL") or "text-embedding-3-small",
                # "embedding_dims": int(os.getenv("EMBEDDING_DIMS") or "1536"),
                # "api_key": os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY"),
                # "openai_base_url": os.getenv("EMBEDDING_API_BASE_URL"),
                "model": str(project_root / "src" / "models" / "bge-large-zh-v1.5"),
                "embedding_dims": int(os.getenv("EMBEDDING_DIMS") or "1024"),
            },
        },
        "vector_store": {
            "provider": "pgvector",
            "config": {
                "host": os.getenv("POSTGRES_HOST"),
                "port": int(os.getenv("POSTGRES_PORT")),
                "dbname": os.getenv("POSTGRES_DB"),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASSWORD"),
                "collection_name": os.getenv("POSTGRES_COLLECTION_NAME"),
                "embedding_model_dims": int(os.getenv("EMBEDDING_DIMS")),
            },
        },
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": os.getenv("NEO4J_URI"),
                "username": os.getenv("NEO4J_USERNAME"),
                "password": os.getenv("NEO4J_PASSWORD"),
            },
        },
        "history_db_path": str(memory_dir / "history.db"),
    }


_memory_instance = None


def get_memory():
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = Memory.from_config(get_config())
    return _memory_instance
