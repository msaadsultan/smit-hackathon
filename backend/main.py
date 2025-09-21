from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from sse_starlette.sse import EventSourceResponse
from typing import List, Optional
import asyncio
import json
import time
from contextlib import asynccontextmanager

from .errors import BaseAppException
from .logging_config import api_logger, setup_logger
from .db import get_db
from .models import (
    StudentCreate, StudentUpdate, StudentResponse, 
    ChatMessage, ChatResponse, AnalyticsResponse,
    EmailRequest, EmailResponse, ActivityLogCreate
)
from .tools_new import get_campus_tools, CampusTools
from .agent import ChatAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    api_logger.info("Starting up Campus AI Admin application")
    yield
    # Shutdown
    api_logger.info("Shutting down Campus AI Admin application")

app = FastAPI(
    title="Campus AI Admin",
    description="""
    AI-powered campus administration system with features including:
    
    * Student Management (CRUD operations)
    * Real-time AI chat assistance
    * Campus analytics and statistics
    * Authentication and authorization
    * Activity logging
    
    For authentication, include the JWT token in the Authorization header:
    `Authorization: Bearer <token>`
    """,
    version="1.0.0",
    contact={
        "name": "Campus AI Admin Team",
        "email": "support@campusai.example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operations for user authentication and authorization"
        },
        {
            "name": "students",
            "description": "Student management operations"
        },
        {
            "name": "analytics",
            "description": "Campus analytics and statistics"
        },
        {
            "name": "chat",
            "description": "AI chat functionality"
        },
        {
            "name": "campus",
            "description": "General campus information"
        }
    ],
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    api_logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    return response

# Exception handlers
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    api_logger.error(
        f"Application error: {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": exc.error_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    api_logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

# Dependency to get campus tools
def get_tools(db: AsyncIOMotorClient = Depends(get_db)) -> CampusTools:
    return get_campus_tools(db)

# Include authentication routes
from .auth.routes import router as auth_router
from .auth.security import check_role, get_current_active_user
from .auth.models import UserRole

app.include_router(auth_router)

# Student Management Endpoints
@app.post(
    "/students/",
    response_model=StudentResponse,
    tags=["students"],
    summary="Create a new student",
    description="Create a new student in the system. Requires STAFF or ADMIN role.",
    responses={
        200: {
            "description": "Student successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ST001",
                        "name": "John Doe",
                        "department": "Computer Science",
                        "email": "john@example.com"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated"
        },
        403: {
            "description": "Not authorized - requires STAFF or ADMIN role"
        }
    }
)
def create_student(
    student: StudentCreate,
    tools: CampusTools = Depends(get_tools),
    current_user = Depends(check_role(UserRole.STAFF))
):
    """
    Create a new student with the following information:
    
    - **id**: Unique student ID
    - **name**: Full name
    - **department**: Department name
    - **email**: Valid email address
    """
    return tools.add_student(student)

@app.get(
    "/students/{student_id}",
    response_model=StudentResponse,
    tags=["students"],
    summary="Get a specific student",
    description="Retrieve detailed information about a student by their ID.",
    responses={
        200: {
            "description": "Student details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ST001",
                        "name": "John Doe",
                        "department": "Computer Science",
                        "email": "john@example.com",
                        "created_at": "2025-09-22T10:00:00Z",
                        "updated_at": "2025-09-22T10:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Student not found"
        },
        401: {
            "description": "Not authenticated"
        }
    }
)
def get_student(
    student_id: str,
    tools: CampusTools = Depends(get_tools),
    current_user = Depends(get_current_active_user)
):
    """
    Retrieve a student by their ID. Authentication required but no specific role needed.
    
    - **student_id**: The unique identifier of the student
    """
    student = tools.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get(
    "/students/",
    response_model=List[StudentResponse],
    tags=["students"],
    summary="List all students",
    description="Retrieve a list of all students in the system.",
    responses={
        200: {
            "description": "List of students retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "ST001",
                            "name": "John Doe",
                            "department": "Computer Science",
                            "email": "john@example.com"
                        },
                        {
                            "id": "ST002",
                            "name": "Jane Smith",
                            "department": "Physics",
                            "email": "jane@example.com"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Not authenticated"
        }
    }
)
def list_students(
    tools: CampusTools = Depends(get_tools),
    current_user = Depends(get_current_active_user)
):
    """
    Retrieve a list of all students. Authentication required but no specific role needed.
    Returns an array of student objects containing basic information.
    """
    return tools.list_students()

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str, 
    student_update: StudentUpdate, 
    tools: CampusTools = Depends(get_tools),
    current_user = Depends(check_role(UserRole.STAFF))
):
    student = tools.update_student(student_id, student_update)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.delete("/students/{student_id}")
def delete_student(
    student_id: str,
    tools: CampusTools = Depends(get_tools),
    current_user = Depends(check_role(UserRole.ADMIN))
):
    success = tools.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

# Analytics Endpoints
@app.get("/analytics/", response_model=AnalyticsResponse)
def get_analytics(tools: CampusTools = Depends(get_tools)):
    return {
        "total_students": tools.get_total_students(),
        "students_by_department": tools.get_students_by_department(),
        "recent_students": tools.get_recent_onboarded_students(),
        "active_students_last_7_days": tools.get_active_students_last_7_days()
    }

# Campus Information Endpoints
@app.get("/campus/cafeteria")
def get_cafeteria_info(tools: CampusTools = Depends(get_tools)):
    return {"timings": tools.get_cafeteria_timings()}

@app.get("/campus/library")
def get_library_info(tools: CampusTools = Depends(get_tools)):
    return {"hours": tools.get_library_hours()}

@app.get("/campus/events")
def get_events(tools: CampusTools = Depends(get_tools)):
    return {"schedule": tools.get_event_schedule()}

# Chat Endpoints
@app.post("/chat/", response_model=ChatResponse, tags=["chat"])
async def chat(
    message: ChatMessage,
    agent: ChatAgent = Depends(ChatAgent),
    db = Depends(get_db)
):
    """
    Regular chat endpoint for synchronous responses.
    Returns a complete response in a single API call.
    """
    response = await agent.get_response(message.message, message.session_id)
    return response

@app.get("/chat/stream", tags=["chat"])
async def stream_chat(
    request: Request,
    message: str,
    session_id: Optional[str] = None,
    agent: ChatAgent = Depends(ChatAgent),
    db = Depends(get_db)
):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    Yields response tokens in real-time as they are generated.
    """
    async def event_generator():
        try:
            async for response in agent.stream_response(message, session_id):
                if await request.is_disconnected():
                    break
                    
                # Format the SSE data
                if isinstance(response, dict):
                    # Final message with session info
                    yield {
                        "event": "done",
                        "data": json.dumps(response)
                    }
                else:
                    # Streaming token
                    yield {
                        "event": "message",
                        "data": json.dumps({"content": response})
                    }
                    
                # Add a retry interval
                yield {
                    "retry": 15000  # 15 seconds
                }
                
        except Exception as e:
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )

# Email Endpoints
@app.post("/email/", response_model=EmailResponse)
def send_email(email_request: EmailRequest, tools: CampusTools = Depends(get_tools)):
    success = tools.send_email(email_request.student_id, email_request.message)
    return {
        "success": success,
        "message": "Email sent successfully" if success else "Failed to send email"
    }

# Activity Logging
@app.post("/activity/", response_model=None)
def log_activity(activity: ActivityLogCreate, tools: CampusTools = Depends(get_tools)):
    tools.log_activity(activity)
    return {"message": "Activity logged successfully"}