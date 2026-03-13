#!/bin/bash

# 🚀 RÉVOLVER.AI.BOT - PRODUCTION DEPLOYMENT SCRIPT
# Date: 29 Juillet 2025
# Version: 1.0.0

set -e  # Exit on any error

echo "🎯 RÉVOLVER.AI.BOT - PRODUCTION DEPLOYMENT"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1 # Exit on error
}

# Step 1: Pre-deployment checks
print_status "Step 1: Pre-deployment checks..."

# Check if we're in the right directory
if [ ! -f "src/api/main.py" ]; then
    print_error "Not in the correct directory. Please run from project root."
fi

# Check Python environment
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not detected. Attempting to activate..."
    source venv/bin/activate 2>/dev/null || {
        print_error "Virtual environment not found. Please activate it manually or create one."
    }
fi

print_success "Pre-deployment checks passed"

# Step 2: Environment setup
print_status "Step 2: Environment setup..."

# Check for .env file
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    if [ -f "config/secrets.example.env" ]; then
        cp config/secrets.example.env .env
        print_warning "Please edit .env file with your production credentials"
        print_warning "Required variables:"
        echo "  - SLACK_BOT_TOKEN"
        echo "  - SLACK_SIGNING_SECRET"
        echo "  - OPENAI_API_KEY"
        echo "  - DATABASE_URL (optional)"
        echo "  - REDIS_URL (optional)"
        echo ""
        read -p "Press Enter after configuring .env file..."
    else
        print_error "No .env template found. Please create .env file manually."
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    print_success "Environment variables loaded"
else
    print_error "No .env file found. Cannot proceed without environment variables."
fi

# Step 3: Dependencies check
print_status "Step 3: Dependencies check..."

# Install/upgrade dependencies
print_status "Installing/upgrading dependencies from requirements.txt..."
pip install -r requirements.txt --upgrade || print_error "Failed to install dependencies."

# Check critical dependencies
python3 -c "
import sys
required_packages = ['fastapi', 'uvicorn', 'slack_sdk', 'openai', 'pandas']
missing = []
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing.append(package)
if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
print('All required packages installed')
" || print_error "Dependencies check failed."

print_success "Dependencies check passed"

# Step 4: Final tests
print_status "Step 4: Running final production readiness tests..."

# Quick functionality test
if [ -f "test_production_readiness.py" ]; then
    python3 test_production_readiness.py || print_error "Production readiness test failed. Fix issues before deployment."
else
    print_warning "test_production_readiness.py not found. Skipping..."
fi

print_success "Final tests passed"

# Step 5: Production deployment
print_status "Step 5: Production deployment..."

# Create production logs directory
mkdir -p logs/production || print_warning "Could not create logs/production directory (might already exist)."

# Start the production server
print_status "Starting RÉVOLVER.AI.BOT production server..."

# Production server configuration
export PRODUCTION_MODE=true
export LOG_LEVEL=INFO
export HOST=${HOST:-0.0.0.0} # Use existing HOST or default to 0.0.0.0
export PORT=${PORT:-8000}   # Use existing PORT or default to 8000
export WORKERS=${WORKERS:-4} # Use existing WORKERS or default to 4

# Start with uvicorn
print_status "Launching with uvicorn..."
print_status "Host: $HOST"
print_status "Port: $PORT"
print_status "Workers: $WORKERS"
echo ""

# Execute uvicorn. 'exec' replaces the current shell process with uvicorn.
# This means the script will stop when uvicorn stops.
exec uvicorn src.api.main:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --access-log \
    --reload=false \
    --proxy-headers \
    --forwarded-allow-ips="*"

# Note: This script will keep running the server until stopped (e.g., Ctrl+C).
# To run in background: nohup ./deploy_production.sh & 