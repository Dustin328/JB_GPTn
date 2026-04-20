# JailbrokeGPT Setup Guide

## Prerequisites

1. **MySQL Database** - Make sure MySQL server is installed and running
2. **Python 3.9+** - For backend
3. **Node.js 18+** - For frontend
4. **Git** - For version control

## Step 1: Database Setup

### Install MySQL
- Windows: Download from https://dev.mysql.com/downloads/mysql/
- Or install XAMPP/WAMP which includes MySQL

### Create Database
```sql
CREATE DATABASE jailbrokegpt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Create MySQL User (Optional but recommended)
```sql
CREATE USER 'jailbrokegpt_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON jailbrokegpt.* TO 'jailbrokegpt_user'@'localhost';
FLUSH PRIVILEGES;
```

## Step 2: Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create and activate virtual environment
```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Or activate (Windows Git Bash)
source venv/Scripts/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

**Note**: Installing `llama-cpp-python` may take 5-10 minutes as it compiles C++ code.

### 4. Configure environment variables

Copy `.env.example` to `.env` and update with your settings:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Model Configuration
MODEL_REPO=bartowski/dolphin-2.9.4-llama3.1-8b-GGUF
MODEL_FILE=dolphin-2.9.4-llama3.1-8b-Q4_K_S.gguf
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.9

# Flask Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root  # or jailbrokegpt_user
DB_PASSWORD=your_mysql_password
DB_NAME=jailbrokegpt

# Security - CHANGE THIS!
SECRET_KEY=generate-a-long-random-string-here-at-least-32-characters
```

**Important**: Generate a secure SECRET_KEY. You can use Python:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize database tables
```bash
python -c "from models import init_db; init_db()"
```

### 6. Start the backend server
```bash
python app.py
```

The first run will download the AI model (~4.7GB). This may take 10-30 minutes depending on your internet speed.

## Step 3: Frontend Setup

### 1. Open a new terminal and navigate to frontend directory
```bash
cd frontend
```

### 2. Install Node dependencies
```bash
npm install
```

### 3. Start development server
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Step 4: First Use

1. Open `http://localhost:5173` in your browser
2. Click "Don't have an account? Register"
3. Create your account (username must be 3+ chars, password 6+ chars)
4. You'll be automatically logged in
5. Start chatting!

## Build a Windows EXE

Use this if you want a single backend executable that also serves the built frontend.

### Prerequisites (on Windows)
- Python virtual environment created in `backend\\venv`
- Node.js + npm installed
- MySQL installed and running
- `backend\\.env` configured

### Build steps
```bat
cd backend
build_windows_exe.bat
```

Output:
- `backend\\dist\\JailbrokeGPTBackend.exe`

Before running on another machine:
- Put `.env` next to the EXE
- Ensure MySQL is available and credentials in `.env` are valid
- Expect first startup to take longer while model files download

## Troubleshooting

### Backend Issues

**Error: "Access denied for user..."**
- Check your MySQL credentials in `.env`
- Make sure MySQL server is running

**Error: "Can't connect to MySQL server"**
- Verify MySQL is running: `mysql -u root -p`
- Check DB_HOST and DB_PORT in `.env`

**Error: "Model loading failed"**
- Check you have enough RAM (8GB+ recommended)
- Model file might be corrupted - delete `models/` folder and restart
- Check internet connection for model download

**Error: "Invalid token" on API calls**
- SECRET_KEY might have changed - clear localStorage in browser
- Token might be expired (7 days) - login again

### Frontend Issues

**Error: "Failed to fetch" or CORS errors**
- Make sure backend is running on port 5000
- Check backend terminal for error messages

**Login fails with "Network error"**
- Backend might not be running
- Check backend logs and verify it is available on port 5000

### Performance Issues

**Slow responses (60+ seconds)**
- This is normal on CPU-only inference
- Consider upgrading to Q3_K_M quantization for faster responses (but higher RAM)
- Or use smaller model like TinyLlama for testing

**High RAM usage**
- Reduce MAX_TOKENS in `.env` (try 256)
- Use smaller quantization (Q4_K_S → Q3_K_S)

## Production Deployment

### Backend

1. Use a production WSGI server (Gunicorn or waitress):
```bash
pip install gunicorn
gunicorn -w 1 -b 0.0.0.0:5000 app:app
```

2. Set up as a system service (systemd on Linux, nssm on Windows)

3. Use environment variables instead of `.env` file

4. Enable HTTPS with nginx/Apache reverse proxy

### Frontend

1. Build for production:
```bash
npm run build
```

2. Serve `dist/` folder with nginx/Apache

3. Update API URLs to production backend

### Database

1. Regular backups:
```bash
mysqldump -u root -p jailbrokegpt > backup.sql
```

2. Enable MySQL slow query log

3. Add indexes if needed for large conversation history

## Updating the Model

To switch to a different model:

1. Update `.env`:
```env
MODEL_REPO=new-repo/model-name
MODEL_FILE=model-file.gguf
```

2. Delete cached models (optional):
```bash
rm -rf models/
```

3. Restart backend - new model will download

## Security Notes

- **CHANGE SECRET_KEY** in production!
- Use strong MySQL passwords
- Don't commit `.env` to git (already in .gitignore)
- Consider rate limiting for production
- Use HTTPS in production
- Regular database backups

## Getting Help

- Check logs in backend terminal
- Check browser console (F12) for frontend errors
- Verify all services are running (MySQL, backend, frontend)
