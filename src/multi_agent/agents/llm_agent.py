from src.llm.base_llm import BaseLLM
from src.multi_agent.statetype.manager import ManagerState
from src.utils.logger import get_logger

logger = get_logger("llm_agent")



class LLMAgent:
    def __init__(self):
        pass

    def run(self,state: ManagerState):
        logger.info("进入 llm_agent")
        llm = BaseLLM().get_llm(state["llm_name"])
        
        if llm is None:
            logger.error(f"llm {state['llm_name']} 不存在")
            state["output"] = "llm_not_available"
            state["done"] = True
            return state

        prompts = [
            {"role": "system", "content": f"用户相关记忆:\n{state.get('memory_context', '')}"},
            {"role": "user", "content": state["user_input"]},
        ]
        response = llm.invoke(prompts)
        state["output"] = getattr(response, "content", response)
        state["done"] = True
        return state
