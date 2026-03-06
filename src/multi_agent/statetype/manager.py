from typing import TypedDict


class ManagerState(TypedDict):
    user_id: str
    user_input: str
    output: str
    memory_context: str
    llm_name: str
    routing_decision: str
    done: bool
