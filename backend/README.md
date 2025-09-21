<<<<<<< HEAD
# campus-admin-ai-agent
=======
import os

# Make sure the "readme" folder exists
os.makedirs("readme", exist_ok=True)

# Content for README.md
readme_content = """# Campus Admin Agent 🏫🤖

## Current Progress (Completed)

1. **Backend Setup**
   - FastAPI application created (`backend/main.py`)
   - Environment variables managed with `.env`  
   - CORS middleware enabled (frontend can connect)

2. **Authentication (JWT)**
   - User **Sign Up** (`/auth/signup`) with password hashing (bcrypt)  
   - User **Login** (`/auth/login`) returns JWT access token  
   - Protected routes use `Depends(get_current_user)`  

3. **Database (MongoDB)**
   - Connection handled in `backend/db.py`  
   - Users stored in `users` collection  
   - Students stored in `students` collection  
   - Conversations stored in `conversations` collection  

4. **Student Management (CRUD)**
   - Add new student (`POST /students`)  
   - Read student by ID (`GET /students/{id}`)  
   - Update student (`PUT /students/{id}`)  
   - Delete student (`DELETE /students/{id}`)  
   - List all students (`GET /students`)  

5. **Analytics**
   - Total student count  
   - Students grouped by department  
   - Recently onboarded students  
   - Active students in last 7 days  

6. **Chat System**
   - `/chat` endpoint (with JWT protection)  
   - WebSocket chat (`/ws/chat/{session_id}`)  
   - Guardrails filter (blocks unsafe messages)  

7. **PDF Upload + RAG (Basic)**
   - Upload PDF text into MongoDB  
   - Basic retrieval for Q/A  

8. **Testing**
   - Postman collections used to test signup, login, CRUD, chat  
   - Root endpoint (`/`) returns health message:  
     ```json
     {"msg": "Campus Admin Agent API is running 🚀"}
     ```

---

## 🔜 Pending (Tomorrow’s Tasks)

- **Frontend (Next.js)**  
  - Login / Signup pages  
  - Dashboard for Student CRUD + Analytics  
  - Chat interface (API + WebSocket)  
  - PDF upload UI  

- **RAG Enhancement**  
  - Chunk PDFs, generate embeddings (OpenAI)  
  - Store vectors in FAISS / Mongo Atlas Vector Search  
  - Use top-k retrieval during chat  

- **Polish**
  - Better error handling  
  - Secure secret keys in `.env`  
  - Docker setup (optional)  

---

## How to Run (Backend)

```bash
# Activate venv
poetry shell

# Start server
poetry run uvicorn backend.main:app --reload --port 8000
>>>>>>> c9c9ee8 (campus-admin-ai-agent)
