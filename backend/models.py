from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Link
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"

class User(Document):
    email: EmailStr
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"
        indexes = [
            "email",
            "role"
        ]

class Student(Document):
    student_id: str
    name: str
    department: str
    email: EmailStr
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "students"
        indexes = [
            "student_id",
            "department",
            "email"
        ]

class StudentCreate(BaseModel):
    student_id: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None

class StudentResponse(BaseModel):
    student_id: str
    name: str
    department: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class AnalyticsResponse(BaseModel):
    total_students: int
    students_by_department: Dict[str, int]
    recent_students: List[StudentResponse]
    active_students_last_7_days: int

class ActivityLog(Document):
    student: Link[Student]
    activity_type: str
    description: str
    timestamp: datetime = datetime.utcnow()

    class Settings:
        name = "activity_logs"
        indexes = [
            "student",
            "activity_type",
            "timestamp"
        ]

class ActivityLogCreate(BaseModel):
    student_id: str
    activity_type: str
    description: str

class ActivityLogResponse(BaseModel):
    student_id: str
    activity_type: str
    description: str
    timestamp: datetime

class Conversation(Document):
    session_id: str
    message: str
    response: str
    timestamp: datetime = datetime.utcnow()

    class Settings:
        name = "conversations"
        indexes = [
            "session_id",
            "timestamp"
        ]
    
    class Config:
        from_attributes = True

class EmailRequest(BaseModel):
    student_id: str
    message: str

class EmailResponse(BaseModel):
    success: bool
    message: str

class CampusInfo(BaseModel):
    cafeteria_timings: str = "Monday-Friday: 8:00 AM - 8:00 PM, Saturday-Sunday: 9:00 AM - 6:00 PM"
    library_hours: str = "Monday-Friday: 7:00 AM - 11:00 PM, Saturday-Sunday: 9:00 AM - 9:00 PM"
    event_schedule: List[str] = [
        "Tech Fest - March 15-17, 2024",
        "Sports Week - April 1-7, 2024", 
        "Cultural Night - May 10, 2024",
        "Graduation Ceremony - June 20, 2024"
    ]
