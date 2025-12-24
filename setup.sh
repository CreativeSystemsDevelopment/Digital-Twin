#!/bin/bash

# Digital Twin - Complete Setup Script
# This script sets up both backend (Python) and frontend (Node.js) dependencies

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Digital Twin - Complete Setup Script               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
print_step "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check Node.js version
print_step "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

# Setup Backend (Python)
echo ""
print_step "Setting up Backend (Python)..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
print_step "Installing Python dependencies..."
pip install --upgrade pip
pip install -e .
print_success "Backend dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_step "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file and add your GEMINI_API_KEY if you plan to use AI extraction"
else
    print_success ".env file already exists"
fi

# Create data directories
print_step "Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
print_success "Data directories created"

# Setup Frontend (Node.js)
echo ""
print_step "Setting up Frontend (Node.js)..."

# Check if pnpm is available, if not use npm
if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
    print_success "Using pnpm as package manager"
else
    PACKAGE_MANAGER="npm"
    print_warning "pnpm not found, using npm instead"
    print_warning "For better performance, consider installing pnpm: npm install -g pnpm"
fi

# Install frontend dependencies
cd frontend
print_step "Installing frontend dependencies (this may take a few minutes)..."
$PACKAGE_MANAGER install
print_success "Frontend dependencies installed"

cd ..

# Final setup verification
echo ""
print_step "Verifying setup..."

# Check if backend can be imported
if python3 -c "import digital_twin" 2>/dev/null; then
    print_success "Backend module can be imported"
else
    print_warning "Backend module import check failed (this may be normal)"
fi

# Check if frontend node_modules exists
if [ -d "frontend/node_modules" ]; then
    print_success "Frontend dependencies are in place"
else
    print_error "Frontend dependencies are missing"
    exit 1
fi

# Print final instructions
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! ✓                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. (Optional) Configure your Gemini API key in .env file"
echo ""
echo "  2. Start the application using:"
echo "     ${GREEN}./start.sh${NC}"
echo ""
echo "  Or start services manually:"
echo "     Backend:  ${BLUE}source .venv/bin/activate && uvicorn src.digital_twin.app:app --reload --port 8000${NC}"
echo "     Frontend: ${BLUE}cd frontend && $PACKAGE_MANAGER run dev${NC}"
echo ""
echo "  3. Access the application:"
echo "     Frontend: ${YELLOW}http://localhost:5173${NC}"
echo "     Backend:  ${YELLOW}http://localhost:8000${NC}"
echo "     API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
