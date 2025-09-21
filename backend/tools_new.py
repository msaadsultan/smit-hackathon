from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient

from .models import (
    Student, ActivityLog, User,
    StudentCreate, StudentUpdate, StudentResponse,
    ActivityLogCreate, ActivityLogResponse
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampusTools:
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
    
    async def add_student(self, student_data: StudentCreate) -> Student:
        """Add a new student to the database"""
        try:
            # Check if student already exists
            existing_student = await Student.find_one({
                "student_id": student_data.student_id
            })
            if existing_student:
                raise ValueError(f"Student with ID {student_data.student_id} already exists")
            
            # Check if email already exists
            existing_email = await Student.find_one({
                "email": student_data.email
            })
            if existing_email:
                raise ValueError(f"Student with email {student_data.email} already exists")
            
            # Create new student
            student = Student(
                student_id=student_data.student_id,
                name=student_data.name,
                department=student_data.department,
                email=student_data.email
            )
            await student.insert()
            
            # Log activity
            await self.log_activity(
                student_data.student_id,
                "student_added",
                f"Student {student_data.name} added to {student_data.department} department"
            )
            
            return student
            
        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            raise
    
    async def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        try:
            student = await Student.find_one({"student_id": student_id})
            if not student:
                raise ValueError(f"Student with ID {student_id} not found")
            return student
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            raise
    
    async def list_students(self) -> List[Student]:
        """List all students"""
        try:
            return await Student.find_all().to_list()
        except Exception as e:
            logger.error(f"Error listing students: {str(e)}")
            raise
    
    async def update_student(self, student_id: str, update_data: StudentUpdate) -> Optional[Student]:
        """Update student information"""
        try:
            student = await self.get_student(student_id)
            if not student:
                raise ValueError(f"Student with ID {student_id} not found")
            
            update_dict = update_data.dict(exclude_unset=True)
            
            # Check if email is being updated and if it already exists
            if "email" in update_dict:
                existing_email = await Student.find_one({
                    "email": update_dict["email"],
                    "student_id": {"$ne": student_id}
                })
                if existing_email:
                    raise ValueError(f"Email {update_dict['email']} is already in use")
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                await student.set({**update_dict})
                
                # Log activity
                await self.log_activity(
                    student_id,
                    "student_updated",
                    f"Student information updated: {', '.join(update_dict.keys())}"
                )
            
            return student
            
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            raise
    
    async def delete_student(self, student_id: str) -> bool:
        """Delete a student"""
        try:
            student = await self.get_student(student_id)
            if not student:
                return False
            
            await student.delete()
            
            # Log activity
            await self.log_activity(
                student_id,
                "student_deleted",
                f"Student {student.name} deleted"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            raise
    
    async def log_activity(self, student_id: str, activity_type: str, description: str):
        """Log student activity"""
        try:
            student = await self.get_student(student_id)
            if not student:
                raise ValueError(f"Student with ID {student_id} not found")
            
            activity = ActivityLog(
                student=student,
                activity_type=activity_type,
                description=description
            )
            await activity.insert()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            raise
    
    async def get_total_students(self) -> int:
        """Get total number of students"""
        try:
            return await Student.count()
        except Exception as e:
            logger.error(f"Error getting total students: {str(e)}")
            raise
    
    async def get_students_by_department(self) -> Dict[str, int]:
        """Get student count grouped by department"""
        try:
            pipeline = [
                {"$group": {"_id": "$department", "count": {"$sum": 1}}}
            ]
            result = await Student.aggregate(pipeline).to_list(None)
            return {item["_id"]: item["count"] for item in result}
        except Exception as e:
            logger.error(f"Error getting students by department: {str(e)}")
            raise
    
    async def get_recent_onboarded_students(self, limit: int = 5) -> List[Student]:
        """Get recently added students"""
        try:
            return await Student.find_all().sort("-created_at").limit(limit).to_list()
        except Exception as e:
            logger.error(f"Error getting recent students: {str(e)}")
            raise
    
    async def get_active_students_last_7_days(self) -> int:
        """Get count of students with activity in last 7 days"""
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            pipeline = [
                {"$match": {"timestamp": {"$gte": seven_days_ago}}},
                {"$group": {"_id": "$student", "count": {"$sum": 1}}},
                {"$count": "total"}
            ]
            result = await ActivityLog.aggregate(pipeline).to_list(None)
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Error getting active students: {str(e)}")
            raise
    
    def get_cafeteria_timings(self) -> Dict:
        """Get cafeteria operating hours"""
        return {
            "weekdays": "7:30 AM - 8:00 PM",
            "weekends": "8:00 AM - 6:00 PM"
        }
    
    def get_library_hours(self) -> Dict:
        """Get library operating hours"""
        return {
            "weekdays": "8:00 AM - 10:00 PM",
            "weekends": "9:00 AM - 6:00 PM"
        }
    
    def get_event_schedule(self) -> List[Dict]:
        """Get upcoming campus events"""
        return [
            {
                "name": "Tech Symposium 2025",
                "date": "2025-10-15",
                "location": "Main Auditorium"
            },
            {
                "name": "Career Fair",
                "date": "2025-10-20",
                "location": "Student Center"
            }
        ]
    
    async def send_email(self, student_id: str, message: str) -> bool:
        """Mock email sending functionality"""
        try:
            student = await self.get_student(student_id)
            if not student:
                return False
            
            # Log the email activity
            await self.log_activity(
                student_id,
                "email_sent",
                f"Email sent to {student.email}: {message[:50]}..."
            )
            
            logger.info(f"Mock email sent to {student.email}: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise

async def get_campus_tools(client: AsyncIOMotorClient) -> CampusTools:
    """Get campus tools instance"""
    return CampusTools(client)