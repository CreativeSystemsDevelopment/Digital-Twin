#!/bin/bash

# Digital Twin - Startup Script
# This script starts both backend and frontend services

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Digital Twin - Starting Application               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if setup has been run
if [ ! -d ".venv" ] || [ ! -d "frontend/node_modules" ]; then
    print_error "Setup not complete. Please run ./setup.sh first"
    exit 1
fi

# Check if pnpm is available, if not use npm
if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
else
    PACKAGE_MANAGER="npm"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    print_warning "Shutting down services..."
    # Kill all background jobs
    jobs -p | xargs -r kill 2>/dev/null || true
    print_success "Services stopped"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Create log directory
mkdir -p logs

# Start Backend
print_step "Starting Backend (FastAPI on port 8000)..."
source .venv/bin/activate
uvicorn src.digital_twin.app:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    print_success "Backend started successfully (PID: $BACKEND_PID)"
else
    print_error "Backend failed to start. Check logs/backend.log for details"
    exit 1
fi

# Start Frontend
print_step "Starting Frontend (Vite on port 5173)..."
cd frontend
$PACKAGE_MANAGER run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend is running
if kill -0 $FRONTEND_PID 2>/dev/null; then
    print_success "Frontend started successfully (PID: $FRONTEND_PID)"
else
    print_error "Frontend failed to start. Check logs/frontend.log for details"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Print status
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Application Started Successfully! ✓           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
print_info "Services are running:"
echo ""
echo "  🎨 Frontend:  ${GREEN}http://localhost:5173${NC}"
echo "  🔧 Backend:   ${GREEN}http://localhost:8000${NC}"
echo "  📚 API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo "  ❤️  Health:   ${GREEN}http://localhost:8000/health${NC}"
echo ""
print_info "Process IDs:"
echo "  Backend:  ${BACKEND_PID}"
echo "  Frontend: ${FRONTEND_PID}"
echo ""
print_info "Logs are being written to:"
echo "  Backend:  ${BLUE}logs/backend.log${NC}"
echo "  Frontend: ${BLUE}logs/frontend.log${NC}"
echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Tail logs in real-time
print_step "Streaming logs (press Ctrl+C to stop)..."
echo ""
tail -f logs/backend.log logs/frontend.log 2>/dev/null || wait
