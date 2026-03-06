import asyncio
import os
import warnings
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Optional
from langchain.agents import create_agent
from src.llm.base_llm import BaseLLM
from src.multi_agent.statetype.manager import ManagerState
from src.multi_agent.mcp.client import MCPClientManager
from src.multi_agent.skills import SkillRegistry
from src.utils.logger import get_logger

logger = get_logger("tool_agent")

project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / ".env")


AMAP_KEY = os.environ.get("AMAP_KEY")

def _default_mcp_configs() -> dict[str, Any]:
    """
    默认同时加载：
    - 本地 stdio MCP
    - 可选的高德 MCP
    """
    configs: dict[str, Any] = {}
    
    project_root = Path(__file__).resolve().parents[3]
    local_server = project_root / "mcp-server" / "server.py"
    if local_server.exists():
        configs["local-sillymcp-stdio"] = {
            "transport": "stdio",
            "command": "python",
            "args": [str(local_server)],
        }

    if AMAP_KEY:
        configs["amap-maps-streamableHTTP"] = {
            "transport": "http",
            "url": f"https://mcp.amap.com/mcp?key={AMAP_KEY}"
        }
    return configs


def _tool_name(tool_obj: Any) -> Optional[str]:
    name = getattr(tool_obj, "name", None)
    if isinstance(name, str) and name:
        return name
    if isinstance(tool_obj, dict):
        n = tool_obj.get("name")
        if isinstance(n, str) and n:
            return n
    return None


class ToolAgent:
    def __init__(
        self,
        skills: SkillRegistry | None = None,
        enabled_skill_names: list[str] | None = None,
        mcp_configs: dict[str, Any] | None = None,
    ):
        skills_dir = Path(__file__).resolve().parents[1] / "skills"
        self.skills = (skills or SkillRegistry.load_from_dir(skills_dir)).filter(enabled_skill_names)
        self.mcp_configs = mcp_configs or _default_mcp_configs()
        self._cached_tools: list[Any] | None = None

    def get_tools(self) -> list[Any]:
        if self._cached_tools is not None:
            return self._cached_tools

        client = MCPClientManager(self.mcp_configs)
        loop = asyncio.new_event_loop()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                self._cached_tools = loop.run_until_complete(client.get_all_tools())
                return self._cached_tools
        finally:
            loop.close()


    def run(self,state: ManagerState) -> str:
        logger.info("进入 tool_agent")
        all_tools = self.get_tools()
        print("工具列表个数：", len(all_tools))

        selected_tool_names = self.skills.select_tool_names(state.get("user_input", ""))
        tools = [t for t in all_tools if (_tool_name(t) in selected_tool_names)] if selected_tool_names else all_tools
        if not tools:
            tools = all_tools

        llm = BaseLLM().get_llm(state["llm_name"])
        if llm is None:
            state["output"] = "llm_not_available"
            state["done"] = True
            return state
            
        skills_prompt = self.skills.format_for_system_prompt()
        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=(
                "你是一个助手。你可以调用工具来获取外部信息或执行动作。\n\n"
                "已注入的 skills（每个 skill 对应一组可调用工具与触发时机）：\n"
                f"{skills_prompt}\n\n"
                "规则：仅在需要外部信息/动作时才调用工具；优先选择与用户问题最匹配的 skill/工具。"
            ),
        )

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result = loop.run_until_complete(agent.ainvoke({
                    "messages": [
                        {"role": "system", "content": f"用户相关记忆:\n{state.get('memory_context', '')}"},
                        {"role": "user", "content": state["user_input"]}
                    ]
                }))
        finally:
            loop.close()
        
        tool_calls = []
        messages = result.get("messages") if isinstance(result, dict) else None
        if messages:
            for msg in messages:
                msg_tool_calls = getattr(msg, "tool_calls", None)
                if msg_tool_calls is None and isinstance(msg, dict):
                    msg_tool_calls = msg.get("tool_calls")
                if msg_tool_calls:
                    for call in msg_tool_calls:
                        name = getattr(call, "name", None)
                        if name is None and isinstance(call, dict):
                            name = call.get("name")
                        if name:
                            tool_calls.append(name)
                msg_role = getattr(msg, "role", None)
                if msg_role is None and isinstance(msg, dict):
                    msg_role = msg.get("role")
                if msg_role == "tool":
                    tool_name = getattr(msg, "name", None)
                    if tool_name is None and isinstance(msg, dict):
                        tool_name = msg.get("name") or msg.get("tool")
                    if tool_name:
                        tool_calls.append(tool_name)
        if tool_calls:
            seen = set()
            unique_calls = []
            for name in tool_calls:
                if name in seen:
                    continue
                seen.add(name)
                unique_calls.append(name)
            print("调用的工具：", ", ".join(unique_calls))

        if isinstance(result, dict) and result.get("messages"):
            state["output"] = result["messages"][-1].content
        else:
            state["output"] = result
        state["done"] = True
        return state





# if __name__ == "__main__":
#     # skills_dir = Path(__file__).resolve().parents[1] / "skills"
#     # skills = SkillRegistry.load_from_dir(skills_dir)

#     # print(skills_dir)
#     # print(skills.skills)
#     # tools = ToolAgent().get_tools()
#     # for tool in tools:
#     #     print(tool)
#     # all_tools = ToolAgent().get_tools()
#     # print("工具列表个数：", len(all_tools))

#     state = ManagerState(user_input="帮我查找柯南的介绍")
#     skills_dir = Path(__file__).resolve().parents[1] / "skills"
#     print(skills_dir)
#     skills = SkillRegistry.load_from_dir(skills_dir)
#     selected_tool_names = skills.select_tool_names(state.get("user_input", ""))
#     print("选择的工具名：", selected_tool_names)
