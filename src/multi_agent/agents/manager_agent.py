import os
from pathlib import Path
from langgraph.graph import StateGraph, START,END
from .rag_agent import RAGAgent
from .tool_agent import ToolAgent
from .llm_agent import LLMAgent
from langgraph.config import get_stream_writer
from src.multi_agent.statetype.manager import ManagerState
from src.llm.base_llm import BaseLLM
from src.multi_agent.skills import SkillRegistry
import logging
project_root = Path(__file__).resolve().parents[3]
from src.utils.logger import get_logger

logger = get_logger("manager_agent")


class ManagerAgent:
    def __init__(self):
        pass


    def init_agents(self):
        skills_dir = Path(__file__).resolve().parents[1] / "skills"
        skills = SkillRegistry.load_from_dir(skills_dir)
        return {
            "rag_agent":RAGAgent(),
            "tool_agent":ToolAgent(skills=skills),
            "llm_agent":LLMAgent(),
        }


    def routing_func(self,state: ManagerState):
        if state["done"]:
            return END
        if state["routing_decision"] == "rag_node":
            return "rag_node"
        if state["routing_decision"] == "tool_node":
            return "tool_node"
        if state["routing_decision"] == "llm_node":
            return "llm_node"
        return "llm_node"



    def door(self,state: ManagerState):

        logger.info("进入 door")

        if state["done"]:
            return state


        system_prompt = f"""
                你是入口代理，需要根据用户输入选择后续执行节点，只能输出以下三者之一：
                tool_node、rag_node、llm_node。

                选择规则（强约束）：
                1) 只要需要访问外部信息、实时数据、第三方服务、地图/天气/搜索/时间/下载/打开/执行动作，就必须选择 tool_node。
                   典型问题：天气/降雨/下雪/温度/预报、地图导航/路线规划、网页搜索/最新消息、调用外部接口。
                2) 需要查询本地知识库/文档/内部资料，选择 rag_node。
                3) 其它仅靠大模型常识即可回答的问题，选择 llm_node。

                重要提示：
                - 如果问题包含“明天/今天/实时/最新/现在”等时态词，通常需要外部信息，优先 tool_node。
                - 只输出 tool_node、rag_node 或 llm_node，禁止输出解释。

                示例：
                - “明天北京会下雪吗？” -> tool_node
                - “给我北京到天津的驾车路线” -> tool_node
                - “查找、搜索名侦探柯南中关于XX的内容” -> tool_node
                - “我本地文档里有没介绍XX？” -> rag_node
                - “解释一下递归是什么？” -> llm_node

                用户的历史问题：{state.get('memory_context', '')}
                """

        prompts = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state["user_input"]},
        ]

        if not state["routing_decision"]:
            llm = BaseLLM().get_llm(state["llm_name"])
            if llm is None:
                state["done"] = True
                state["output"] = "llm_not_available"
                return state

            response = llm.invoke(prompts)
            text = getattr(response, "content", str(response))
            
            if not text:
                state["routing_decision"] = "llm_node"
            else:
                decision = text.strip()
                if decision not in {"rag_node", "tool_node", "llm_node"}:
                    decision = decision.lower()
                    if "rag_node" in decision or "rag" in decision or "知识库" in decision or "检索" in decision:
                        decision = "rag_node"
                    elif "tool_node" in decision or "tool" in decision or "工具" in decision or "插件" in decision:
                        decision = "tool_node"
                    elif "llm_node" in decision or "llm" in decision or "直接" in decision or "回答" in decision:
                        decision = "llm_node"
                    else:
                        decision = "llm_node"
                state["routing_decision"] = decision
        return state




    def init_graph(self):
        agents = self.init_agents()

        workflow = StateGraph(ManagerState)

        # add nodes
        workflow.add_node("door", self.door)
        workflow.add_node("rag_node", agents["rag_agent"].run)
        workflow.add_node("tool_node", agents["tool_agent"].run)
        workflow.add_node("llm_node", agents["llm_agent"].run)

        # add edges
        workflow.add_edge(START, "door")
        workflow.add_conditional_edges("door",self.routing_func,["rag_node","tool_node","llm_node", END])
        workflow.add_edge("rag_node", "door")
        workflow.add_edge("tool_node", "door")
        workflow.add_edge("llm_node", "door")

        graph = workflow.compile()

        return graph
