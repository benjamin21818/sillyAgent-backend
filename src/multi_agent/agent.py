import sys
import os
import warnings
from dotenv import load_dotenv
import importlib.util
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
project_root_str = str(project_root)
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)
if project_root_str not in sys.path:
    sys.path.append(project_root_str)

warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv(os.path.join(project_root, ".env"))

import asyncio
from src.multi_agent.agents.manager_agent import ManagerAgent

def load_local_config():
    module_name = "sillyagent_local_config"
    if module_name in sys.modules:
        return sys.modules[module_name]
    config_path = Path(project_root) / "config.py"
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

config_module = load_local_config()
get_config = config_module.get_config
get_memory = config_module.get_memory
_cached_graph = None


def get_graph():
    global _cached_graph
    if _cached_graph is None:
        _cached_graph = ManagerAgent().init_graph()
    return _cached_graph



async def run_agent(user_id,query,llm_name):

    memory = get_memory()
    relevant_memories = memory.search(query, user_id=user_id, limit=30)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    
    graph = get_graph()
    result = await graph.ainvoke({
        "user_id": user_id,
        "user_input": query,
        "llm_name": llm_name,
        "output": "",
        "memory_context": memories_str,
        "routing_decision": "",
        "done": False,
    })

    messages = [{"role": "user", "content": query}, {"role": "assistant", "content": result["output"]}]
    try:
        memory.add(messages, user_id=user_id)
    except Exception:
        memory.enable_graph = False
        memory.graph = None
        memory.add(messages, user_id=user_id, infer=False)

    print(result["output"])
    return result["output"]




