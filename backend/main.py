# backend/main.py
import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .db import db
from . import tools, utils, agent
from .auth import router as auth_router, get_current_user


# ------------------ Init App ------------------
load_dotenv()
app = FastAPI(title="Campus Admin Agent")

# Auth router
app.include_router(auth_router)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------ Root ------------------
@app.get("/")
async def root():
    return {"msg": "Campus Admin Agent API is running 🚀"}


# ------------------ Student CRUD ------------------
class StudentIn(BaseModel):
    name: str
    student_id: str
    department: str
    email: str


class StudentUpdateIn(BaseModel):
    field: str
    value: str


@app.post("/students")
async def create_student(payload: StudentIn, user=Depends(get_current_user)):
    try:
        doc = payload.dict()
        res = await tools.add_student(doc)
        return utils.doc_to_json(res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/students/{student_id}")
async def read_student(student_id: str, user=Depends(get_current_user)):
    doc = await tools.get_student(student_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return utils.doc_to_json(doc)


@app.put("/students/{student_id}")
async def put_student(student_id: str, payload: StudentUpdateIn, user=Depends(get_current_user)):
    res = await tools.update_student(student_id, payload.field, payload.value)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return utils.doc_to_json(res)


@app.delete("/students/{student_id}")
async def delete_student(student_id: str, user=Depends(get_current_user)):
    cnt = await tools.delete_student(student_id)
    return {"deleted": bool(cnt)}


@app.get("/students")
async def list_students(limit: int = 100, user=Depends(get_current_user)):
    docs = await tools.list_students(limit=limit)
    return [utils.doc_to_json(d) for d in docs]


# ------------------ Analytics ------------------
@app.get("/analytics")
async def analytics(user=Depends(get_current_user)):
    total = await tools.get_total_students()
    by_dept = await tools.get_students_by_department()
    recent = await tools.get_recent_onboarded_students(limit=5)
    active = await tools.get_active_students_last_7_days()
    return {
        "total_students": total,
        "by_department": by_dept,
        "recent_onboardings": [utils.doc_to_json(d) for d in recent],
        "active_last_7_days": active,
    }


# ------------------ Chat ------------------
class ChatMsg(BaseModel):
    session_id: str | None = None
    messages: list


@app.get("/threads")
async def list_threads(user=Depends(get_current_user)):
    user_id = user["_id"] if "_id" in user else user["username"]
    threads = await db.conversations.find({"user_id": user_id}).to_list(length=100)
    session_ids = list({t["session_id"] for t in threads if "session_id" in t})
    return {"threads": session_ids}


@app.post("/chat")
async def chat_endpoint(payload: ChatMsg, user=Depends(get_current_user)):
    user_id = user["_id"] if "_id" in user else user["username"]
    res = await agent.handle_agent_request(payload.session_id, payload.messages, user_id=user_id)
    if "error" in res and res["error"] == "Message blocked by guardrails":
        return {"error": "Message blocked by guardrails"}
    return res


# 🔥 Streaming chat
@app.post("/chat/stream")
async def chat_stream(payload: ChatMsg, user=Depends(get_current_user)):
    async def event_generator():
        res = await agent.handle_agent_request(payload.session_id, payload.messages, user_id=user["username"])
        if "assistant" in res:
            for token in res["assistant"].split():
                yield f"data: {token}\n\n"
        else:
            yield f"data: {json.dumps(res)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ------------------ WebSocket Chat ------------------
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_text = payload.get("content")
            if not user_text:
                await websocket.send_text(json.dumps({"error": "no content"}))
                continue

            # Save user message
            await db.conversations.update_one(
                {"session_id": session_id},
                {"$push": {"messages": {"role": "user", "content": user_text}}},
                upsert=True,
            )

            # Call the agent
            result = await agent.handle_agent_request(session_id, [{"role": "user", "content": user_text}])
            await websocket.send_text(json.dumps({"result": result}))
    except WebSocketDisconnect:
        print("Client disconnected")
