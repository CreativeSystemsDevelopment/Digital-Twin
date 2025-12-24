# Digital Twin Documentation Pipeline

This project ingests all documentation for a specific diecast machine and converts it into a searchable database/vector store for semantic querying. It features a beautiful dark neumorphic UI with AI-powered document extraction capabilities.

## ⚡ Quick Start (Recommended)

### Prerequisites
- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)

### Automatic Setup & Start

#### On Linux/Mac:
```bash
# 1. Setup (run once)
./setup.sh

# 2. Start the application
./start.sh
```

#### On Windows:
```cmd
REM 1. Setup (run once)
setup.bat

REM 2. Start the application
start.bat
```

That's it! 🎉 The application will be available at:
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Agent Monitor Dashboard**: http://localhost:8000/monitor/dashboard

### What the Scripts Do

**setup.sh / setup.bat**:
- ✅ Checks Python and Node.js versions
- ✅ Creates Python virtual environment
- ✅ Installs backend dependencies
- ✅ Installs frontend dependencies (using pnpm or npm)
- ✅ Creates .env file from template
- ✅ Sets up data directories

**start.sh / start.bat**:
- ✅ Starts backend (FastAPI) on port 8000
- ✅ Starts frontend (Vite + React) on port 5173
- ✅ Monitors both services
- ✅ Creates log files in `logs/` directory
- ✅ Auto-opens browser (Windows)

Press `Ctrl+C` to stop all services.

---

## 📖 Manual Setup (Alternative)

If you prefer to set up manually or the scripts don't work on your system:

### Backend Setup
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate.bat  # Windows

# 3. Install dependencies
pip install -e .

# 4. Create .env file (optional, for AI features)
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Frontend Setup
```bash
cd frontend

# Install dependencies (using pnpm recommended, or npm)
pnpm install
# or
npm install
```

### Running Manually

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows
uvicorn src.digital_twin.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pnpm run dev  # or npm run dev
```

---

## 🎨 Features

### Beautiful Dark Neumorphic UI
- Modern dark theme with soft 3D-style design
- Responsive and accessible interface
- Smooth animations and transitions
- Built with React 19 + TypeScript

### Document Management
- **Upload**: Drag-and-drop document upload with real-time progress
- **Library**: Browse, search, and filter documents
- **Categories**: Auto-detection of document types (schematics, wiring diagrams, parts lists, etc.)
- **Machine Organization**: Organize documents by machine/production line

### AI-Powered Extraction (Optional)
- **Gemini AI Integration**: Extract structured data from schematics
- **Component Detection**: Identify electrical components and symbols
- **Wiring Analysis**: Extract wire connections and terminal information
- **Real-time Feedback**: Visual step-by-step extraction workflow

### Agent Monitoring System 🆕
- **Multi-Agent Tracking**: Monitor multiple extraction agents in real-time
- **Task Management**: Assign, track, and manage extraction tasks
- **Progress Reporting**: Live progress updates with page-level granularity
- **Dashboard**: Visual monitoring interface with auto-refresh
- **Heartbeat System**: Detect stalled or unresponsive agents
- **RESTful API**: Complete API for programmatic monitoring

### Dashboard
- System status monitoring
- Recent activity feed
- Statistics and metrics
- Machine sync status
- Agent monitoring dashboard

---

## 🏗️ Project Structure

```
Digital-Twin/
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   └── index.css      # Neumorphic design system
│   └── package.json
├── src/
│   └── digital_twin/      # Python backend
│       ├── app.py         # FastAPI application
│       ├── config.py      # Configuration
│       ├── agent_monitor.py    # Agent monitoring system 🆕
│       └── gemini_service.py  # AI extraction service
├── data/                  # Document storage (gitignored)
├── examples/              # Example scripts
│   └── monitor_demo.py    # Agent monitoring demo 🆕
├── logs/                  # Application logs (created on startup)
├── setup.sh / setup.bat   # Setup scripts
├── start.sh / start.bat   # Startup scripts
└── pyproject.toml         # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Gemini API Key (optional, for AI extraction)
GEMINI_API_KEY=your_api_key_here
```

### Storage Layout
- **Uploaded files**: `data/<machine_id>/raw_data/<timestamp>_<filename>`
- **Imported files**: `data/<machine_id>/imported/`
- **Metadata**: `src/data/metadata.json`

All raw uploads and metadata are gitignored by default.

---

## 🚀 API Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload Documents
```bash
curl -X POST \
  -F "files=@/path/to/document.pdf" \
  -F "machine_label=Machine-001" \
  http://localhost:8000/upload/stream
```

### List Documents
```bash
# All documents
curl http://localhost:8000/files

# Filter by machine
curl "http://localhost:8000/files?machine_id=Machine-001"
```

### API Documentation
Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Troubleshooting

### Setup Issues

**"Python is not installed"**
- Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
- Make sure Python is in your PATH

**"Node.js is not installed"**
- Install Node.js 18+ from [nodejs.org](https://nodejs.org/)
- Make sure Node is in your PATH

**"Virtual environment activation failed"**
- On Windows, you may need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use Command Prompt instead of PowerShell

**"Frontend dependencies failed to install"**
- Clear npm cache: `npm cache clean --force`
- Delete `frontend/node_modules` and `frontend/package-lock.json`
- Run setup again

### Runtime Issues

**"Port 8000 or 5173 already in use"**
- Check for other processes: `lsof -i :8000` (Mac/Linux) or `netstat -ano | findstr :8000` (Windows)
- Stop conflicting processes or change ports in the code

**"Backend not responding"**
- Check `logs/backend.log` for errors
- Ensure virtual environment is activated
- Verify Python dependencies are installed

**"Frontend shows blank page"**
- Check `logs/frontend.log` for errors
- Clear browser cache and reload
- Check browser console for JavaScript errors

**"AI extraction not working"**
- Verify `GEMINI_API_KEY` is set in `.env` file
- Check if API key is valid at http://localhost:8000/gemini/status
- Ensure required document files are in place

### Getting Help

Check the logs:
```bash
# View backend logs
tail -f logs/backend.log

# View frontend logs  
tail -f logs/frontend.log
```

For more detailed documentation:
- `QUICK_START.md` - Detailed quick start guide
- `UI_DESIGN_COMPLETE.md` - UI/UX documentation
- `COMPONENT_SHOWCASE.md` - Component library details

---

## 📝 Development

### Backend Development
```bash
source .venv/bin/activate
uvicorn src.digital_twin.app:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
pnpm run dev  # or npm run dev
```

### Building for Production
```bash
cd frontend
pnpm run build  # or npm run build
```

### Linting
```bash
cd frontend
pnpm run lint  # or npm run lint
```

---

## 🤖 Agent Monitoring

The system includes a comprehensive agent monitoring solution for tracking extraction agents working on schematic digitization.

### Quick Start

View the monitoring dashboard:
```
http://localhost:8000/monitor/dashboard
```

Run the demo:
```bash
python examples/monitor_demo.py
```

### Features

- **Real-time Tracking**: Monitor multiple agents and their tasks
- **Progress Updates**: Track extraction progress at page-level granularity
- **Status Management**: View agent and task statuses (pending, running, completed, failed)
- **Heartbeat System**: Detect stalled or unresponsive agents
- **Persistence**: State survives server restarts
- **RESTful API**: Complete programmatic access

### API Endpoints

Key monitoring endpoints:
- `GET /monitor/summary` - Overall system summary
- `GET /monitor/agents` - List all agents
- `GET /monitor/tasks` - List all tasks
- `POST /monitor/agents/register` - Register new agent
- `POST /monitor/tasks/assign` - Assign task to agent
- `PUT /monitor/tasks/{task_id}/progress` - Update task progress

### Example Usage

```python
from src.digital_twin.agent_monitor import get_monitor, AgentStatus

# Get monitor instance
monitor = get_monitor()

# Register an agent
agent_id = monitor.register_agent("My Extractor", "gemini_extractor")

# Assign a task
task_id = monitor.assign_task(
    agent_id, 
    "Extract pages 1-50",
    "page_extraction",
    pages=list(range(1, 51))
)

# Update progress
monitor.update_task_progress(task_id, 0.5)
monitor.heartbeat(agent_id, task_id)
```

For complete documentation, see [AGENT_MONITOR_DOCS.md](AGENT_MONITOR_DOCS.md)

---

## 🔒 Security

- All API keys should be stored in `.env` (gitignored)
- Uploaded documents are stored locally and not committed to git
- CORS is configured for development (update for production)

---

## 📄 License

[Add your license information here]

---

## 🤝 Contributing

[Add contribution guidelines here]
