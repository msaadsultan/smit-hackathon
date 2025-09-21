from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import PydanticObjectId

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
        
    async def get_student(self, student_id: str) -> Optional[Student]:
        """Get a student by ID"""
        return await Student.find_one({"student_id": student_id})
        
    async def list_students(self, skip: int = 0, limit: int = 10) -> List[Student]:
        """List all students with pagination"""
        return await Student.find_all().skip(skip).limit(limit).to_list()
        
    async def update_student(self, student_id: str, student_data: StudentUpdate) -> Optional[Student]:
        """Update a student's information"""
        student = await self.get_student(student_id)
        if not student:
            return None
            
        # Update only provided fields
        update_data = student_data.dict(exclude_unset=True)
        if update_data:
            for key, value in update_data.items():
                setattr(student, key, value)
            student.updated_at = datetime.utcnow()
            await student.save()
        
        return student
        
    async def delete_student(self, student_id: str) -> bool:
        """Delete a student"""
        student = await self.get_student(student_id)
        if not student:
            return False
        await student.delete()
        return True
    
    async def add_student(self, student_data: StudentCreate) -> Student:
        """Add a new student to the database"""
        try:
            # Check if student already exists
            existing_student = await Student.find_one({"student_id": student_data.student_id})
            if existing_student:
                raise ValueError(f"Student with ID {student_data.student_id} already exists")
            
            # Create new student
            student = Student(
                student_id=student_data.student_id,
                name=student_data.name,
                department=student_data.department,
                email=student_data.email
            )
            await student.insert()
            
            # Log activity
            await ActivityLog(
                student_id=student.student_id,
                activity_type="student_added",
                description=f"Student {student.name} added to {student.department} department"
            ).insert()
            
            return student
        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            raise e
        """Get student information by ID"""
        try:
            student = self.db.query(Student).filter(Student.id == id).first()
            if not student:
                return {"success": False, "message": f"Student with ID {id} not found"}
            
            return {
                "success": True,
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "department": student.department,
                    "email": student.email,
                    "created_at": student.created_at.isoformat(),
                    "updated_at": student.updated_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            return {"success": False, "message": f"Error getting student: {str(e)}"}
    
    def update_student(self, id: str, field: str, new_value: str) -> Dict:
        """Update a specific field of a student"""
        try:
            student = self.db.query(Student).filter(Student.id == id).first()
            if not student:
                return {"success": False, "message": f"Student with ID {id} not found"}
            
            valid_fields = ["name", "department", "email"]
            if field not in valid_fields:
                return {"success": False, "message": f"Invalid field. Valid fields are: {', '.join(valid_fields)}"}
            
            # Check if email is being updated and if it already exists
            if field == "email":
                existing_email = self.db.query(Student).filter(Student.email == new_value, Student.id != id).first()
                if existing_email:
                    return {"success": False, "message": f"Email {new_value} is already in use"}
            
            setattr(student, field, new_value)
            student.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Log activity
            self._log_activity(id, "student_updated", f"Student {field} updated to {new_value}")
            
            return {
                "success": True,
                "message": f"Student {field} updated successfully",
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "department": student.department,
                    "email": student.email,
                    "updated_at": student.updated_at.isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating student: {str(e)}")
            return {"success": False, "message": f"Error updating student: {str(e)}"}
    
    def delete_student(self, id: str) -> Dict:
        """Delete a student from the database"""
        try:
            student = self.db.query(Student).filter(Student.id == id).first()
            if not student:
                return {"success": False, "message": f"Student with ID {id} not found"}
            
            student_name = student.name
            self.db.delete(student)
            self.db.commit()
            
            # Log activity
            self._log_activity(id, "student_deleted", f"Student {student_name} deleted")
            
            return {"success": True, "message": f"Student {student_name} deleted successfully"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting student: {str(e)}")
            return {"success": False, "message": f"Error deleting student: {str(e)}"}
    
    def list_students(self) -> Dict:
        """List all students"""
        try:
            students = self.db.query(Student).all()
            student_list = []
            for student in students:
                student_list.append({
                    "id": student.id,
                    "name": student.name,
                    "department": student.department,
                    "email": student.email,
                    "created_at": student.created_at.isoformat(),
                    "updated_at": student.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "count": len(student_list),
                "students": student_list
            }
        except Exception as e:
            logger.error(f"Error listing students: {str(e)}")
            return {"success": False, "message": f"Error listing students: {str(e)}"}
    
    def get_total_students(self) -> Dict:
        """Get total number of students"""
        try:
            count = self.db.query(Student).count()
            return {"success": True, "total_students": count}
        except Exception as e:
            logger.error(f"Error getting total students: {str(e)}")
            return {"success": False, "message": f"Error getting total students: {str(e)}"}
    
    def get_students_by_department(self) -> Dict:
        """Get student count by department"""
        try:
            result = self.db.query(
                Student.department,
                func.count(Student.id).label('count')
            ).group_by(Student.department).all()
            
            department_stats = {dept: count for dept, count in result}
            return {"success": True, "students_by_department": department_stats}
        except Exception as e:
            logger.error(f"Error getting students by department: {str(e)}")
            return {"success": False, "message": f"Error getting students by department: {str(e)}"}
    
    def get_recent_onboarded_students(self, limit: int = 5) -> Dict:
        """Get recently onboarded students"""
        try:
            students = self.db.query(Student).order_by(desc(Student.created_at)).limit(limit).all()
            recent_students = []
            for student in students:
                recent_students.append({
                    "id": student.id,
                    "name": student.name,
                    "department": student.department,
                    "email": student.email,
                    "created_at": student.created_at.isoformat()
                })
            
            return {"success": True, "recent_students": recent_students}
        except Exception as e:
            logger.error(f"Error getting recent students: {str(e)}")
            return {"success": False, "message": f"Error getting recent students: {str(e)}"}
    
    def get_active_students_last_7_days(self) -> Dict:
        """Get count of active students in the last 7 days (based on activity logs)"""
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            active_student_ids = self.db.query(ActivityLog.student_id).filter(
                ActivityLog.timestamp >= seven_days_ago
            ).distinct().all()
            
            count = len(active_student_ids)
            return {"success": True, "active_students_last_7_days": count}
        except Exception as e:
            logger.error(f"Error getting active students: {str(e)}")
            return {"success": False, "message": f"Error getting active students: {str(e)}"}
    
    def get_cafeteria_timings(self) -> Dict:
        """Get cafeteria timings"""
        return {"success": True, "cafeteria_timings": self.campus_info.cafeteria_timings}
    
    def get_library_hours(self) -> Dict:
        """Get library hours"""
        return {"success": True, "library_hours": self.campus_info.library_hours}
    
    def get_event_schedule(self) -> Dict:
        """Get event schedule"""
        return {"success": True, "event_schedule": self.campus_info.event_schedule}
    
    def send_email(self, student_id: str, message: str) -> Dict:
        """Mock email sending functionality"""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {"success": False, "message": f"Student with ID {student_id} not found"}
            
            # Mock email sending - in real implementation, integrate with email service
            logger.info(f"Mock email sent to {student.email}: {message}")
            
            # Log activity
            self._log_activity(student_id, "email_sent", f"Email sent: {message[:50]}...")
            
            return {
                "success": True,
                "message": f"Email sent successfully to {student.name} ({student.email})",
                "email_content": message
            }
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {"success": False, "message": f"Error sending email: {str(e)}"}
    
    def _log_activity(self, student_id: str, activity_type: str, description: str):
        """Log student activity"""
        try:
            activity = ActivityLog(
                student_id=student_id,
                activity_type=activity_type,
                description=description
            )
            self.db.add(activity)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            self.db.rollback()

# Tool function definitions for the AI agent
def get_campus_tools(db: Session) -> CampusTools:
    """Get campus tools instance"""
    return CampusTools(db)

# Define tool functions that the AI agent can call
TOOL_FUNCTIONS = {
    "add_student": "Add a new student with name, id, department, and email",
    "get_student": "Get student information by ID",
    "update_student": "Update a student's field (name, department, or email)",
    "delete_student": "Delete a student by ID",
    "list_students": "List all students in the database",
    "get_total_students": "Get the total number of students",
    "get_students_by_department": "Get student count grouped by department",
    "get_recent_onboarded_students": "Get recently onboarded students (default limit: 5)",
    "get_active_students_last_7_days": "Get count of active students in the last 7 days",
    "get_cafeteria_timings": "Get cafeteria operating hours",
    "get_library_hours": "Get library operating hours",
    "get_event_schedule": "Get upcoming campus events",
    "send_email": "Send an email to a student (mock implementation)"
}
