import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.multi_agent.agent import run_agent


router = APIRouter(
    tags=["agent"],
    prefix="/agent",
)


@router.get("/")
def read_root():
    return {"Hello": "World agent"}


@router.websocket("/ws")
async def agent_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                payload = {"query": message}
            user_id = payload.get("user_id") or "default"
            query = payload.get("query") or payload.get("input") or ""
            llm_name = payload.get("llm_name") or "deepseek"
            if not query:
                await websocket.send_text(json.dumps({"error": "empty_query"}))
                continue
            result = await run_agent(user_id, query, llm_name)
            await websocket.send_text(json.dumps({"output": result}))
    except WebSocketDisconnect:
        return
