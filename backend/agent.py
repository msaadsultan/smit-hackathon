import openai
import json
import uuid
from typing import Dict, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .tools import CampusTools, TOOL_FUNCTIONS
from .db import Conversation, get_db

load_dotenv()

class CampusAgent:
    def __init__(self, db: Session):
        self.db = db
        self.tools = CampusTools(db)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_memory = {}
        
        # Define the function schemas for OpenAI
        self.function_schemas = [
            {
                "name": "add_student",
                "description": "Add a new student to the campus database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Student's full name"},
                        "id": {"type": "string", "description": "Student ID"},
                        "department": {"type": "string", "description": "Student's department"},
                        "email": {"type": "string", "description": "Student's email address"}
                    },
                    "required": ["name", "id", "department", "email"]
                }
            },
            {
                "name": "get_student",
                "description": "Get student information by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Student ID"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "update_student",
                "description": "Update a student's information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Student ID"},
                        "field": {"type": "string", "enum": ["name", "department", "email"], "description": "Field to update"},
                        "new_value": {"type": "string", "description": "New value for the field"}
                    },
                    "required": ["id", "field", "new_value"]
                }
            },
            {
                "name": "delete_student",
                "description": "Delete a student from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Student ID"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "list_students",
                "description": "List all students in the database",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_total_students",
                "description": "Get the total number of students",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_students_by_department",
                "description": "Get student count grouped by department",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_recent_onboarded_students",
                "description": "Get recently onboarded students",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of students to return", "default": 5}
                    }
                }
            },
            {
                "name": "get_active_students_last_7_days",
                "description": "Get count of active students in the last 7 days",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_cafeteria_timings",
                "description": "Get cafeteria operating hours",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_library_hours",
                "description": "Get library operating hours",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_event_schedule",
                "description": "Get upcoming campus events",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "send_email",
                "description": "Send an email to a student",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "string", "description": "Student ID"},
                        "message": {"type": "string", "description": "Email message content"}
                    },
                    "required": ["student_id", "message"]
                }
            }
        ]
    
    def _execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """Execute a function call with the given arguments"""
        try:
            if hasattr(self.tools, function_name):
                method = getattr(self.tools, function_name)
                result = method(**arguments)
                return result
            else:
                return {"success": False, "message": f"Function {function_name} not found"}
        except Exception as e:
            return {"success": False, "message": f"Error executing {function_name}: {str(e)}"}
    
    def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id not in self.conversation_memory:
            # Load from database
            conversations = self.db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.timestamp).limit(10).all()
            
            history = []
            for conv in conversations:
                history.append({"role": "user", "content": conv.message})
                history.append({"role": "assistant", "content": conv.response})
            
            self.conversation_memory[session_id] = history
        
        return self.conversation_memory[session_id]
    
    def _save_conversation(self, session_id: str, message: str, response: str):
        """Save conversation to database and memory"""
        try:
            conversation = Conversation(
                session_id=session_id,
                message=message,
                response=response
            )
            self.db.add(conversation)
            self.db.commit()
            
            # Update memory
            if session_id not in self.conversation_memory:
                self.conversation_memory[session_id] = []
            
            self.conversation_memory[session_id].append({"role": "user", "content": message})
            self.conversation_memory[session_id].append({"role": "assistant", "content": response})
            
            # Keep only last 20 messages in memory
            if len(self.conversation_memory[session_id]) > 20:
                self.conversation_memory[session_id] = self.conversation_memory[session_id][-20:]
                
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def chat(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Process a chat message and return response"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Get conversation history
            history = self._get_conversation_history(session_id)
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful Campus Admin Agent AI assistant. You can help with:
                    
1. Student Management: Add, update, delete, and retrieve student information
2. Campus Analytics: Provide statistics about students, departments, and activities
3. Campus Information: Share details about cafeteria timings, library hours, and events
4. Communication: Send emails to students (mock implementation)

You have access to various tools to interact with the campus database. Always be helpful, professional, and provide accurate information. When users ask for student operations, use the appropriate tools to perform the requested actions.

If you need to perform any database operations, use the available function calls. Always confirm successful operations and provide clear feedback to users."""
                }
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=self.function_schemas,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # Execute the function
                function_result = self._execute_function(function_name, function_args)
                
                # Add function call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": response_message.function_call.arguments
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Get final response from OpenAI
                final_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_message = final_response.choices[0].message.content
            else:
                final_message = response_message.content
            
            # Save conversation
            self._save_conversation(session_id, message, final_message)
            
            return {
                "response": final_message,
                "session_id": session_id,
                "success": True
            }
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            return {
                "response": error_message,
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
    
    async def chat_stream(self, message: str, session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Process a chat message and return streaming response"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Get conversation history
            history = self._get_conversation_history(session_id)
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful Campus Admin Agent AI assistant. You can help with:
                    
1. Student Management: Add, update, delete, and retrieve student information
2. Campus Analytics: Provide statistics about students, departments, and activities
3. Campus Information: Share details about cafeteria timings, library hours, and events
4. Communication: Send emails to students (mock implementation)

You have access to various tools to interact with the campus database. Always be helpful, professional, and provide accurate information. When users ask for student operations, use the appropriate tools to perform the requested actions."""
                }
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # First, check if we need to call functions
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=self.function_schemas,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # Execute the function
                function_result = self._execute_function(function_name, function_args)
                
                # Add function call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": response_message.function_call.arguments
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Stream the final response
                stream = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True
                )
                
                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content, 'session_id': session_id})}\n\n"
                
                # Save conversation
                self._save_conversation(session_id, message, full_response)
                
            else:
                # Stream the direct response
                stream = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True
                )
                
                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content, 'session_id': session_id})}\n\n"
                
                # Save conversation
                self._save_conversation(session_id, message, full_response)
            
            # Send end signal
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            yield f"data: {json.dumps({'content': error_message, 'error': True, 'session_id': session_id})}\n\n"
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

def get_agent(db: Session) -> CampusAgent:
    """Get campus agent instance"""
    return CampusAgent(db)
