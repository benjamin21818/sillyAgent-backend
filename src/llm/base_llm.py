import os

_LLM_CACHE = {}


class BaseLLM:

    def __init__(self):
        pass

    def get_llm(self, llm_name: str):
        if llm_name == "openai":
            from langchain_openai import ChatOpenAI

            if os.environ.get("OPENAI_API_KEY"):
                model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
                base_url = os.environ.get("OPENAI_BASE_URL", None)
                cache_key = ("openai", model, base_url)
                if cache_key in _LLM_CACHE:
                    return _LLM_CACHE[cache_key]
                llm = ChatOpenAI(
                    model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    base_url=base_url,
                )
                _LLM_CACHE[cache_key] = llm
                return llm
            else:
                print("没有找到OPENAI_API_KEY，请配置环境变量")
                return None

        elif llm_name == "deepseek":
            from langchain_deepseek import ChatDeepSeek

            if os.environ.get("DEEPSEEK_API_KEY"):
                model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
                cache_key = ("deepseek", model)
                if cache_key in _LLM_CACHE:
                    return _LLM_CACHE[cache_key]
                llm = ChatDeepSeek(
                    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                    api_key=os.environ.get("DEEPSEEK_API_KEY"),
                )
                _LLM_CACHE[cache_key] = llm
                return llm
            else:
                print("没有找到DEEPSEEK_API_KEY，请配置环境变量")
                return None

        else:
            raise ValueError(f"肥肠抱芡，暂不支持 {llm_name}！")
