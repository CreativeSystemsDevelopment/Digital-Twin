# Digital Twin - Complete Startup Guide

## Overview

This guide provides comprehensive instructions for setting up and running the Digital Twin application. The application consists of:

- **Backend**: FastAPI-based Python server (port 8000)
- **Frontend**: React + TypeScript + Vite application (port 5173)

---

## 🚀 Quick Start (Automated)

### Step 1: Run Setup Script

The setup script will install all dependencies and configure the environment.

**On Linux/Mac:**
```bash
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

**What the setup script does:**
- ✅ Verifies Python 3.10+ and Node.js 18+ are installed
- ✅ Creates Python virtual environment (`.venv`)
- ✅ Installs all Python dependencies from `pyproject.toml`
- ✅ Installs all Node.js dependencies for the frontend
- ✅ Creates `.env` file from `.env.example` template
- ✅ Creates necessary data directories

**Time required:** 2-5 minutes (depending on internet speed)

### Step 2: Configure API Key (Optional)

If you want to use AI-powered extraction features:

1. Open the `.env` file in the root directory
2. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Get an API key from: https://makersuite.google.com/app/apikey

**Note:** The application works without an API key, but AI extraction features will be disabled.

### Step 3: Start the Application

**On Linux/Mac:**
```bash
./start.sh
```

**On Windows:**
```cmd
start.bat
```

**What the start script does:**
- ✅ Starts the backend server on port 8000
- ✅ Starts the frontend development server on port 5173
- ✅ Creates log files in the `logs/` directory
- ✅ Monitors both services
- ✅ Opens browser automatically (Windows only)

### Step 4: Access the Application

Once both services are running, open your browser to:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 5: Stop the Application

Press `Ctrl+C` in the terminal where `start.sh` or `start.bat` is running.

On Windows, you can also close the Backend and Frontend command prompt windows.

---

## 📖 Manual Setup (Alternative)

If the automated scripts don't work on your system, follow these manual steps:

### Backend Setup

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate.bat

# 3. Install dependencies
pip install -e .

# 4. Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY if needed
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (pnpm recommended, or npm)
pnpm install
# or
npm install
```

### Running Manually

**Terminal 1 - Backend:**
```bash
# Activate virtual environment first
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows

# Start backend
uvicorn src.digital_twin.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pnpm run dev  # or npm run dev
```

---

## 🔧 Configuration

### Environment Variables

Edit the `.env` file in the root directory:

```bash
# Gemini API Key for AI extraction (optional)
GEMINI_API_KEY=your_api_key_here
```

### Port Configuration

To change the default ports:

**Backend (default: 8000):**
- Edit `start.sh` or `start.bat`
- Change `--port 8000` to your desired port

**Frontend (default: 5173):**
- Edit `frontend/vite.config.ts`
- Change `port: 5173` in the server configuration

---

## 📂 Directory Structure

```
Digital-Twin/
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
├── src/
│   └── digital_twin/      # Python backend
│       ├── app.py         # FastAPI application
│       ├── config.py      # Configuration
│       └── gemini_service.py  # AI extraction service
├── data/                  # Document storage (gitignored)
│   └── <machine_id>/
│       ├── raw_data/      # Uploaded documents
│       └── imported/      # Processed documents
├── logs/                  # Application logs (created at runtime)
│   ├── backend.log        # Backend server logs
│   └── frontend.log       # Frontend build logs
├── .env                   # Environment variables (gitignored)
├── .env.example           # Environment template
├── setup.sh / setup.bat   # Setup scripts
├── start.sh / start.bat   # Startup scripts
├── pyproject.toml         # Python dependencies
└── README.md              # Main documentation
```

---

## 🛠️ Troubleshooting

### Setup Issues

#### "Python is not installed" or "Node.js is not installed"

**Solution:**
- Install Python 3.10+ from https://www.python.org/downloads/
- Install Node.js 18+ from https://nodejs.org/
- Make sure they are added to your system PATH
- Restart your terminal after installation

**Verify installation:**
```bash
python --version  # or python3 --version
node --version
```

#### "Permission denied" when running setup.sh or start.sh (Linux/Mac)

**Solution:**
```bash
chmod +x setup.sh start.sh
./setup.sh
```

#### "Virtual environment activation failed" (Windows PowerShell)

**Solution:**
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or use Command Prompt instead of PowerShell.

#### "pip install failed" or "npm install failed"

**Solution:**
```bash
# For Python:
pip install --upgrade pip
pip cache purge
pip install -e .

# For Node.js:
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Runtime Issues

#### "Port 8000 already in use" or "Port 5173 already in use"

**Solution:**

Find and stop the process using the port:

**Linux/Mac:**
```bash
# Find process
lsof -i :8000  # or :5173

# Stop process
kill -9 <PID>
```

**Windows:**
```cmd
# Find process
netstat -ano | findstr :8000

# Stop process (replace <PID> with the actual process ID)
taskkill /PID <PID> /F
```

Or change the port in the configuration files.

#### "Backend not responding" or "502 Bad Gateway"

**Solution:**
1. Check backend logs: `tail -f logs/backend.log` (or open in text editor)
2. Verify virtual environment is activated
3. Ensure all Python dependencies are installed
4. Check if port 8000 is accessible: `curl http://localhost:8000/health`

#### "Frontend shows blank page" or "Vite error"

**Solution:**
1. Check frontend logs: `tail -f logs/frontend.log` (or open in text editor)
2. Clear browser cache and hard reload (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for JavaScript errors (F12)
4. Verify backend is running and accessible
5. Try rebuilding:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

#### "AI extraction not working"

**Solution:**
1. Verify `GEMINI_API_KEY` is set in `.env` file
2. Check API key validity at: http://localhost:8000/gemini/status
3. View backend logs for specific error messages
4. Ensure required document files exist in the `data/` directory

#### "Cannot connect to backend" (CORS errors)

**Solution:**
1. Ensure backend is running on port 8000
2. Check `frontend/vite.config.ts` proxy configuration
3. Try accessing backend directly: http://localhost:8000/health
4. Check if firewall is blocking connections

---

## 📊 Monitoring and Logs

### View Logs

**Linux/Mac:**
```bash
# View backend logs
tail -f logs/backend.log

# View frontend logs
tail -f logs/frontend.log

# View both simultaneously
tail -f logs/backend.log logs/frontend.log
```

**Windows:**
```cmd
# View in Notepad or any text editor
notepad logs\backend.log
notepad logs\frontend.log
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Expected response: {"status":"ok"}

# API status
curl http://localhost:8000/gemini/status

# List uploaded files
curl http://localhost:8000/files
```

---

## 🔐 Security Notes

- **API Keys**: Never commit `.env` file to git (it's in `.gitignore`)
- **Documents**: Uploaded documents are stored locally and gitignored
- **CORS**: Update CORS settings in production (currently allows all origins for development)
- **Network**: Backend binds to `0.0.0.0` for Docker compatibility; restrict in production

---

## 🚢 Production Deployment

For production deployment, consider:

1. **Build the frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve frontend build with a web server** (nginx, Apache, etc.)

3. **Run backend with production ASGI server:**
   ```bash
   gunicorn src.digital_twin.app:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

4. **Set up reverse proxy** (nginx) to route traffic

5. **Use environment variables** for configuration

6. **Enable HTTPS** with SSL certificates

7. **Configure proper CORS** settings

8. **Set up monitoring** and log aggregation

9. **Use a process manager** (systemd, supervisord, pm2)

---

## 📞 Getting Help

### Check Documentation

- `README.md` - Main documentation
- `QUICK_START.md` - Quick start guide for the UI
- `UI_DESIGN_COMPLETE.md` - UI/UX documentation
- `COMPONENT_SHOWCASE.md` - Component library details

### Common Resources

- **Backend API Docs**: http://localhost:8000/docs (when running)
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Vite Documentation**: https://vitejs.dev/
- **React Documentation**: https://react.dev/

---

## 🎯 Next Steps

After successfully starting the application:

1. **Explore the UI**:
   - Navigate through Dashboard, Library, Import, and other pages
   - Familiarize yourself with the dark neumorphic design

2. **Upload Documents**:
   - Go to Import page
   - Select or create a machine
   - Upload PDF documents (schematics, manuals, etc.)

3. **Browse Library**:
   - View all uploaded documents
   - Filter by machine or category
   - Download or view documents

4. **Try AI Extraction** (if API key configured):
   - Go to AI Extraction page
   - Run sample extraction to see AI in action
   - View extracted components and wiring information

5. **Monitor System**:
   - Check Dashboard for system overview
   - View recent activity and statistics
   - Monitor machine sync status

---

## 📝 Tips for Development

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Changes to `.py` files automatically reload the server
- Frontend: Changes to `.tsx`, `.ts`, `.css` files automatically rebuild

### Debugging

**Backend (Python):**
- Add `import pdb; pdb.set_trace()` for breakpoints
- View logs in `logs/backend.log`
- Use FastAPI's automatic API docs at `/docs`

**Frontend (React):**
- Use browser DevTools (F12)
- Install React DevTools extension
- Check console for errors and warnings

### Code Quality

```bash
# Backend linting (if configured)
pylint src/

# Frontend linting
cd frontend
npm run lint
```

---

**Happy coding! 🚀**
