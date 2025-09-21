# backend/agent.py
import os
import json
import logging
import asyncio
import openai
from dotenv import load_dotenv
from backend import tools, utils
from backend.db import db

load_dotenv()
LOGGER = logging.getLogger("agent")
LOGGER.setLevel(logging.INFO)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
openai.api_key = OPENAI_API_KEY

# ------------------ Define Functions ------------------
FUNCTIONS = [
    {
        "name": "add_student",
        "description": "Add a new student",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "student_id": {"type": "string"},
                "department": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["name", "student_id", "department", "email"]
        }
    },
    {
        "name": "get_student",
        "description": "Retrieve a student by student_id",
        "parameters": {
            "type": "object",
            "properties": {"student_id": {"type": "string"}},
            "required": ["student_id"]
        }
    },
    {
        "name": "update_student",
        "description": "Update a student field",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "field": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["student_id", "field", "value"]
        }
    },
    {
        "name": "delete_student",
        "description": "Delete a student by student_id",
        "parameters": {
            "type": "object",
            "properties": {"student_id": {"type": "string"}},
            "required": ["student_id"]
        }
    },
    {
        "name": "get_total_students",
        "description": "Get total number of students",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
]

FUNCTION_MAP = {
    "add_student": tools.add_student,
    "get_student": tools.get_student,
    "update_student": tools.update_student,
    "delete_student": tools.delete_student,
    "get_total_students": tools.get_total_students,
}

# ------------------ OpenAI Call ------------------
async def call_openai_with_functions(messages):
    return openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        functions=FUNCTIONS,
        function_call="auto"
    )

# ------------------ Guardrails ------------------
from backend.utils import is_safe_message

# ------------------ Handle Agent ------------------
async def handle_agent_request(session_id: str | None, messages: list, user_id=None):
    # ✅ Guardrails check
    if not is_safe_message(messages[-1]["content"]):
        return {"error": "Message blocked by guardrails"}

    chat_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    # Load previous memory
    if session_id:
        conv = await db.conversations.find_one({"session_id": session_id})
        if conv and "messages" in conv:
            for m in conv["messages"]:
                chat_messages.insert(0, {"role": m["role"], "content": m["content"]})

    resp = await asyncio.get_event_loop().run_in_executor(None, lambda: call_openai_with_functions(chat_messages))
    if asyncio.iscoroutine(resp):
        resp = await resp

    msg = resp["choices"][0]["message"]

    if msg.get("function_call"):
        fname = msg["function_call"]["name"]
        args_text = msg["function_call"].get("arguments", "{}")
        args = json.loads(args_text)
        fn = FUNCTION_MAP.get(fname)
        if not fn:
            return {"error": f"Unknown function: {fname}"}
        result = await fn(**args)
        if session_id:
            await db.conversations.update_one(
                {"session_id": session_id},
                {"$push": {"messages": {"role": "assistant", "content": f"Called {fname} -> {str(result)}"}}},
                upsert=True
            )
        return {"tool": fname, "result": result}
    else:
        content = msg.get("content")
        if session_id:
            await db.conversations.update_one(
                {"session_id": session_id},
                {"$push": {"messages": {"role": "assistant", "content": content}}},
                upsert=True
            )
        return {"assistant": content}
