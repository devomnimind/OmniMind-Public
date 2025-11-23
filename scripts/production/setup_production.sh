#!/bin/bash

# OmniMind Production Setup Script
# Automated installation and configuration for production deployment

set -e

echo "🚀 OmniMind Production Setup Script"
echo "===================================="

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
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

print_status "Setting up OmniMind production environment in: $PROJECT_DIR"

# Step 1: Check system requirements
print_status "Step 1: Checking system requirements..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l) -eq 1 ]]; then
    print_success "Python version: $PYTHON_VERSION ✓"
else
    print_error "Python 3.12+ required. Current: $PYTHON_VERSION"
    exit 1
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    print_success "Docker is installed ✓"
else
    print_warning "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker installed. Please log out and back in for group changes to take effect."
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    print_success "Docker Compose is available ✓"
else
    print_warning "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed ✓"
fi

# Step 2: Install Python dependencies
print_status "Step 2: Installing Python dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created ✓"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
print_status "Installing Python packages from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Python dependencies installed ✓"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Step 3: Setup environment configuration
print_status "Step 3: Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp .env.template .env
        print_warning "Environment file created from template. Please edit .env with your actual values:"
        print_warning "- Qdrant URL and API key"
        print_warning "- Supabase credentials"
        print_warning "- HuggingFace token"
        print_warning "- Other service credentials"
    else
        print_error ".env.template not found"
        exit 1
    fi
else
    print_success "Environment file already exists ✓"
fi

# Step 4: Create missing configuration files
print_status "Step 4: Creating missing configuration files..."

# Create omnimind.yaml if it doesn't exist
if [ ! -f "config/omnimind.yaml" ]; then
    cat > config/omnimind.yaml << EOF
# OmniMind Main Configuration
version: "1.0"
environment: "production"

# Server configuration
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false

# Database configuration
database:
  type: "qdrant"
  url: "\${OMNIMIND_QDRANT_URL}"
  api_key: "\${OMNIMIND_QDRANT_API_KEY}"
  collection: "\${OMNIMIND_QDRANT_COLLECTION}"

# Security configuration
security:
  jwt_secret: "change-this-in-production"
  cors_origins:
    - "http://localhost:4173"
    - "http://localhost:3000"

# Monitoring configuration
monitoring:
  enabled: true
  health_check_interval: 30
  metrics_enabled: true

# Logging configuration
logging:
  level: "INFO"
  format: "json"
  file: "logs/omnimind.log"
EOF
    print_success "config/omnimind.yaml created ✓"
else
    print_success "config/omnimind.yaml already exists ✓"
fi

# Step 5: Setup directories
print_status "Step 5: Setting up required directories..."

mkdir -p logs
mkdir -p data
mkdir -p backups
mkdir -p temp

print_success "Directories created ✓"

# Step 6: Initialize Docker services
print_status "Step 6: Initializing Docker services..."

# Check if docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    print_status "Building Docker images..."
    docker-compose build

    if [ $? -eq 0 ]; then
        print_success "Docker images built ✓"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
else
    print_error "docker-compose.yml not found"
    exit 1
fi

# Step 7: Run initial health checks
print_status "Step 7: Running initial health checks..."

# Activate virtual environment again (in case it was lost)
source venv/bin/activate

# Run diagnostic script
if [ -f "scripts/diagnose.py" ]; then
    print_status "Running system diagnostic..."
    python scripts/diagnose.py --quick > logs/setup_diagnostic.log 2>&1

    if [ $? -eq 0 ]; then
        print_success "Diagnostic completed. Check logs/setup_diagnostic.log for details."
    else
        print_warning "Diagnostic completed with warnings. Check logs/setup_diagnostic.log"
    fi
fi

# Step 8: Create startup scripts
print_status "Step 8: Creating production startup scripts..."

# Create production start script
cat > start_production.sh << 'EOF'
#!/bin/bash
# OmniMind Production Startup Script

echo "🚀 Starting OmniMind Production Environment"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run health check
echo "Running health checks..."
python scripts/diagnose.py --quick

echo ""
echo "🎉 OmniMind Production Environment Started!"
echo "🌐 Frontend: http://localhost:4173"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
EOF

chmod +x start_production.sh
print_success "Production startup script created ✓"

# Create development start script
cat > start_development.sh << 'EOF'
#!/bin/bash
# OmniMind Development Startup Script

echo "🚀 Starting OmniMind Development Environment"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start Qdrant (if using local instance)
# docker run -d -p 6333:6333 -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant

# Start backend in development mode
echo "Starting backend server..."
cd web/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend in development mode
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 OmniMind Development Environment Started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"

# Wait for processes
wait
EOF

chmod +x start_development.sh
print_success "Development startup script created ✓"

print_success "OmniMind production setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual credentials"
echo "2. Run: ./start_production.sh"
echo "3. Check logs/setup_diagnostic.log for any issues"
echo "4. Access the application at http://localhost:4173"
echo ""
echo "📚 For development: ./start_development.sh"
echo "🛑 To stop production: docker-compose down"
echo "📊 To monitor: python scripts/diagnose.py --full"
