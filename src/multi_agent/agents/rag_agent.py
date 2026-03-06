from src.multi_agent.statetype.manager import ManagerState
from src.utils.logger import get_logger

logger = get_logger("rag_agent")


class RAGAgent:
    def __init__(self):
        pass
    
    def run(self,state: ManagerState) -> str:
        logger.info("进入 rag_agent")
        memory_context = state.get("memory_context", "")
        if memory_context:
            state["output"] = f"进入到了RAG agent\n参考记忆:\n{memory_context}"
        else:
            state["output"] = "进入到了RAG agent"
        state["done"] = True
        return state
