# Campus AI Admin Agent

A full-stack application that provides an AI-powered administrative interface for managing student interactions and campus activities. Built with FastAPI and Next.js, it enables educational institutions to manage student records, engage in real-time AI-assisted chat interactions, and track campus activities.

## Key Features

- 🤖 AI-powered chat interactions with students
- 📊 Real-time analytics dashboard
- 👥 Comprehensive student management system
- 🔒 Secure JWT authentication
- 📝 Activity logging and tracking
- 🔄 Real-time updates with Server-Sent Events (SSE)
- 📱 Responsive web interface

## Project Overview

### Backend (FastAPI + MongoDB)

- ✅ MongoDB database integration with Beanie ODM
- ✅ FastAPI server with async support
- ✅ JWT authentication system
- ✅ Student management endpoints (CRUD operations)
- ✅ Real-time chat with SSE streaming
- ✅ Activity logging system
- ✅ Error handling and logging
- ✅ Postman collection for API testing

### Frontend (Next.js)

- ✅ Authentication pages and middleware
- ✅ Dashboard layout with navigation
- ✅ Student management interface
- ✅ Real-time chat interface
- ✅ Analytics overview

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- MongoDB
- Poetry (Python package manager)
- npm (Node.js package manager)

## Quick Start Guide

### Step 1: Install Required Software

1. Install MongoDB:
   - Go to [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Download MongoDB Community Edition
   - Run the installer and follow the wizard
   - At the end of installation, make sure "Run service as Network Service user" is checked

2. Install Node.js:
   - Go to [Node.js website](https://nodejs.org/)
   - Download the "LTS" version
   - Run the installer and accept all defaults

3. Install Python 3.9 or higher:
   - Go to [Python Downloads](https://www.python.org/downloads/)
   - Download Python 3.9 or newer
   - During installation, check "Add Python to PATH"

### Step 2: Download and Setup Project

1. Download this project:
   - Click the green "Code" button above
   - Select "Download ZIP"
   - Extract the ZIP file to your desired location

2. Open PowerShell and navigate to the project folder:
   ```powershell
   cd "path\to\campus-ai-agent"
   ```

### Step 3: Run the Software

1. First Terminal - Start Backend:
   ```powershell
   # Install Poetry
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   
   # Install backend dependencies
   poetry install
   
   # Start backend server
   poetry run uvicorn backend.main:app --reload --port 8000
   ```

2. Second Terminal - Start Frontend:
   ```powershell
   # Go to frontend folder
   cd frontend
   
   # Install frontend dependencies
   npm install
   
   # Start frontend server
   npm run dev
   ```

### Step 4: Access the Application

1. Open your web browser and go to:
   - Login page: `http://localhost:3000/login`
   - API documentation: `http://localhost:8000/docs`

2. Create your admin account:
   ```powershell
   # Run this in PowerShell
   poetry run python -c "from backend.auth.security import get_password_hash; print(get_password_hash('your_password_here'))"
   ```

3. Add these lines to your `.env` file:
   ```env
   ADMIN_EMAIL=your_email@example.com
   ADMIN_PASSWORD_HASH=<paste_the_hash_from_step_2>
   ```

4. Login credentials will be:
   - Email: The email you set in ADMIN_EMAIL
   - Password: The password you used in step 2

### Common Problems and Solutions

1. If "poetry" command not found:
   ```powershell
   # Add Poetry to your PATH
   $env:Path += ";$env:APPDATA\Python\Scripts"
   ```

2. If MongoDB service isn't running:
   ```powershell
   # Open PowerShell as Administrator and run:
   Start-Service MongoDB
   ```

3. If port 8000 is in use:
   ```powershell
   # Use a different port
   poetry run uvicorn backend.main:app --reload --port 8001
   ```
   Then update `NEXT_PUBLIC_API_URL` in frontend/.env.local to match

### Backend Setup

1. Clone the repository and install Python dependencies:
   ```bash
   git clone https://github.com/yourusername/campus-ai-agent.git
   cd campus-ai-agent
   poetry install
   ```

2. Create a `.env` file in the project root:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=campus_ai_agent
   OPENAI_API_KEY=your_openai_api_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Start the backend server:
   ```bash
   poetry run uvicorn backend.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   
   API Documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage Examples

### Student Management

1. Create a new student:

   ```bash
   curl -X POST http://localhost:8000/students \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "department": "Computer Science"
     }'
   ```

2. List all students:

   ```bash
   curl http://localhost:8000/students \
     -H "Authorization: Bearer $TOKEN"
   ```

### Real-time Chat

1. Start a chat session:

   ```bash
   curl http://localhost:8000/chat/stream \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "123",
       "message": "Hello, I need help with my course registration"
     }'
   ```

2. Retrieve chat history:

   ```bash
   curl http://localhost:8000/chat/123/messages \
     -H "Authorization: Bearer $TOKEN"
   ```

### User Authentication

1. Login to get JWT token:

   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -d "username=admin@example.com&password=your_password"
   ```

2. Use the token in subsequent requests:

   ```bash
   export TOKEN="your_jwt_token"
   ```

## Troubleshooting Guide

### Common Issues

1. MongoDB Connection Issues:
   - Ensure MongoDB service is running
   - Verify MongoDB connection URL in `.env`
   - Check MongoDB logs for errors:
     ```bash
     # Windows
     Get-Content 'C:\Program Files\MongoDB\Server\logs\mongod.log'
     ```

2. Backend Server Won't Start:
   - Verify Python virtual environment is activated
   - Check if required ports are available
   - Ensure all environment variables are set
   - Look for errors in the `logs/api.log` file

3. Frontend Development Server Issues:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: 
     ```bash
     rm -rf node_modules
     rm package-lock.json
     npm install
     ```
   - Verify API URL in `.env.local`

### Performance Optimization Tips

1. Database Indexes:
   - MongoDB indexes are automatically created by Beanie ODM
   - Check index usage: `db.collection.explain()`
   - Monitor query performance in MongoDB Compass

2. Frontend Optimization:
   - Use React Query for data caching
   - Implement pagination for large lists
   - Lazy load components and images
   - Enable Next.js static optimization

3. Production Deployment:
   - Use PM2 or systemd for process management
   - Set up NGINX as reverse proxy
   - Enable HTTPS with Let's Encrypt
   - Configure proper CORS settings

## Development Status

### ✅ Completed Features

1. Backend Features:
   - MongoDB database integration with Beanie ODM
   - FastAPI server with async support
   - JWT authentication system
   - Student management endpoints
   - Real-time chat with SSE streaming
   - Activity logging system
   - Error handling and logging
   - API documentation (Swagger/ReDoc)
   - Postman collection for testing

2. Frontend Features:
   - Next.js setup with TypeScript
   - Authentication system with JWT
   - Responsive dashboard layout
   - Student management interface
   - Real-time chat interface
   - Analytics overview page
   - Error handling and notifications

### 🔄 In Progress

- Additional test coverage
- Performance optimizations
- Documentation updates

### 📝 Planned Features

- Email notifications
- File upload support
- Batch student operations
- Advanced analytics
- Chat message templates

## Contributing

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Run tests before committing:
   ```bash
   # Backend tests
   poetry run pytest
   
   # Frontend tests
   cd frontend && npm test
   ```
4. Commit your changes:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
5. Push to the branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the amazing Python web framework
- Next.js team for the React framework
- MongoDB team for the database
- OpenAI for the AI capabilities

## Project Structure

```plaintext
campus-ai-agent/
├── backend/
│   ├── auth/           # Authentication handlers
│   ├── tests/          # Backend tests
│   ├── agent.py        # AI agent implementation
│   ├── db.py          # Database configuration
│   ├── main.py        # FastAPI application
│   ├── models.py      # Data models
│   └── tools_new.py   # Business logic
├── frontend/
│   ├── app/           # Next.js pages and components
│   ├── utils/         # Frontend utilities
│   └── public/        # Static assets
├── postman/           # API testing collection
└── logs/             # Application logs
```

## API Testing with Postman

### Setting Up Postman Tests

1. Import the collection:
   - Open Postman
   - Click "Import" and select `postman/Campus_AI_Admin.postman_collection.json`
   - Also import `postman/Campus_AI_Admin_Local.postman_environment.json`

2. Configure environment:
   - Select the "Campus_AI_Admin_Local" environment
   - Update the following variables:
     - `baseUrl`: `http://localhost:8000`
     - `jwt_token`: (This will be automatically set after login)

3. Running the tests:
   - Start with the "Auth/Login" request to get a valid JWT token
   - The token will be automatically set for subsequent requests
   - Run other requests in the collection to test different endpoints

### Available API Endpoints

#### Authentication

- POST /auth/login - Login with credentials
- POST /auth/refresh - Refresh JWT token

#### Students

- GET /students - List all students
- POST /students - Create a new student
- GET /students/{id} - Get student details
- PUT /students/{id} - Update student
- DELETE /students/{id} - Delete student

#### Chat

- GET /chat/{student_id}/messages - Get chat history
- POST /chat/{student_id}/stream - Start streaming chat

#### Analytics

- GET /analytics/students - Get student statistics
- GET /analytics/activity - Get activity logs

## Development Status

### ✅ Completed Features

1. Backend:
   - MongoDB database integration
   - FastAPI server with async support
   - JWT authentication system
   - Student management endpoints
   - Real-time chat with SSE
   - Activity logging
   - Error handling
   - API documentation
   - Postman collection

2. Frontend:
   - Next.js setup with TypeScript
   - Authentication system
   - Dashboard layout
   - Student management interface
   - Real-time chat interface
   - Analytics overview

### 🔄 In Progress

- Additional test coverage
- Performance optimizations
- Documentation updates

## Running Tests

### Backend Tests

```bash
# In the project root
poetry run pytest backend/tests/
```

### API Tests (Postman)

1. Start the backend server
2. Import the Postman collection and environment
3. Run the collection:
   - In Postman, click on the "..." menu next to the collection
   - Select "Run collection"
   - Click "Run Campus_AI_Admin"

## Common Issues and Troubleshooting

1. MongoDB Connection:
   - Ensure MongoDB is running locally
   - Check the MONGODB_URL in .env file
   - Verify database permissions

2. JWT Authentication:
   - Make sure JWT_SECRET_KEY is set in .env
   - Check token expiration time
   - Clear browser storage if needed

3. Frontend API Connection:
   - Verify NEXT_PUBLIC_API_URL in .env.local
   - Check CORS settings in backend
   - Ensure backend is running on correct port
=======
# campus-admin-ai-agent
>>>>>>> 85bf2cb5d6ddb3f5a5cc5f03ab0354c4d2c39749
=======
# campus-admin-ai-agent
>>>>>>> 85bf2cb5d6ddb3f5a5cc5f03ab0354c4d2c39749
