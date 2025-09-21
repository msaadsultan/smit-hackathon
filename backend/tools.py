# backend/tools.py
from datetime import datetime, timedelta
from pymongo import ReturnDocument
import random
import logging
from .db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Student Management ------------------
async def add_student(student_doc: dict):
    student_doc["created_at"] = datetime.utcnow()
    existing = await db.students.find_one({"student_id": student_doc["student_id"]})
    if existing:
        raise ValueError("student_id already exists")
    res = await db.students.insert_one(student_doc)
    return await db.students.find_one({"_id": res.inserted_id})

async def get_student(student_id: str):
    return await db.students.find_one({"student_id": student_id})

async def update_student(student_id: str, field: str, value):
    update = {"$set": {field: value}}
    updated = await db.students.find_one_and_update(
        {"student_id": student_id}, update, return_document=ReturnDocument.AFTER
    )
    return updated

async def delete_student(student_id: str):
    res = await db.students.delete_one({"student_id": student_id})
    return res.deleted_count

async def list_students(limit: int = 100):
    cur = db.students.find().sort("created_at", -1).limit(limit)
    return [doc async for doc in cur]

# ------------------ Analytics ------------------
async def get_total_students():
    return await db.students.count_documents({})

async def get_students_by_department():
    pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return [doc async for doc in db.students.aggregate(pipeline)]

async def get_recent_onboarded_students(limit=5):
    cur = db.students.find().sort("created_at", -1).limit(limit)
    return [doc async for doc in cur]

async def log_activity(student_id: str, activity_type: str = "login"):
    doc = {
        "student_id": student_id,
        "activity_type": activity_type,
        "timestamp": datetime.utcnow()
    }
    await db.activity_logs.insert_one(doc)
    return doc

async def get_active_students_last_7_days():
    dt = datetime.utcnow() - timedelta(days=7)
    pipeline = [
        {"$match": {"timestamp": {"$gte": dt}}},
        {"$group": {"_id": "$student_id", "last_activity": {"$max": "$timestamp"}, "count": {"$sum": 1}}},
        {"$sort": {"last_activity": -1}}
    ]
    return [doc async for doc in db.activity_logs.aggregate(pipeline)]

# ------------------ FAQ (optional) ------------------
async def get_cafeteria_timings():
    return {"cafeteria": "Mon-Fri 8:00-20:00, Sat 9:00-16:00"}

async def get_library_hours():
    return {"library": "Mon-Sun 07:00-23:00"}

async def get_event_schedule():
    events = [
        {"title": "Orientation", "date": "2025-10-01", "time": "10:00"}
    ]
    return events

# ------------------ Notifications ------------------
async def send_email(student_id: str, message: str):
    student = await get_student(student_id)
    if not student:
        raise ValueError("student not found")
    email_log = {
        "student_id": student_id,
        "to": student["email"],
        "message": message,
        "timestamp": datetime.utcnow()
    }
    await db.email_logs.insert_one(email_log)
    logger.info("Mock email sent: %s", email_log)
    return email_log
