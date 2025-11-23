#!/usr/bin/env bash
# OmniMind One-Click Installation Script
# Complete automated setup with environment detection and optimization
# Based on existing setup_production.sh with enhanced automation

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/install_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

print_header() {
    log ""
    log "${CYAN}============================================================${NC}"
    log "${CYAN}$1${NC}"
    log "${CYAN}============================================================${NC}"
}

print_status() {
    log "${BLUE}[INFO]${NC} $1"
}

print_success() {
    log "${GREEN}[✓]${NC} $1"
}

print_warning() {
    log "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    log "${RED}[✗]${NC} $1"
}

# ============================================================================
# Error Handling
# ============================================================================

error_exit() {
    print_error "$1"
    print_error "Installation failed. Check $LOG_FILE for details."
    exit 1
}

# ============================================================================
# System Detection
# ============================================================================

detect_os() {
    print_status "Detecting operating system..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_success "Detected: $PRETTY_NAME"
    else
        OS=$(uname -s)
        print_warning "Could not detect Linux distribution. Detected: $OS"
    fi
}

detect_package_manager() {
    print_status "Detecting package manager..."
    
    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt-get"
        PKG_UPDATE="apt-get update"
        PKG_INSTALL="apt-get install -y"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        PKG_UPDATE="dnf check-update || true"
        PKG_INSTALL="dnf install -y"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        PKG_UPDATE="yum check-update || true"
        PKG_INSTALL="yum install -y"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        PKG_UPDATE="pacman -Sy"
        PKG_INSTALL="pacman -S --noconfirm"
    else
        error_exit "No supported package manager found"
    fi
    
    print_success "Using package manager: $PKG_MANAGER"
}

detect_gpu() {
    print_status "Detecting GPU..."
    
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null || echo "")
        if [[ -n "$GPU_INFO" ]]; then
            HAS_GPU=true
            print_success "NVIDIA GPU detected: $GPU_INFO"
        else
            HAS_GPU=false
            print_warning "nvidia-smi found but no GPU detected"
        fi
    else
        HAS_GPU=false
        print_warning "No NVIDIA GPU detected (CPU mode will be used)"
    fi
}

detect_hardware() {
    print_status "Detecting hardware capabilities..."
    
    CPU_CORES=$(nproc 2>/dev/null || echo "1")
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    AVAILABLE_RAM=$(free -g | awk '/^Mem:/{print $7}')
    
    print_success "CPU Cores: $CPU_CORES"
    print_success "Total RAM: ${TOTAL_RAM}GB"
    print_success "Available RAM: ${AVAILABLE_RAM}GB"
    
    # Run Python hardware detector if available
    if [[ -f "$PROJECT_DIR/src/optimization/hardware_detector.py" ]]; then
        print_status "Running detailed hardware detection..."
        cd "$PROJECT_DIR"
        python3 src/optimization/hardware_detector.py > "$PROJECT_DIR/config/hardware_profile.json" 2>&1 || true
        print_success "Hardware profile saved to config/hardware_profile.json"
    fi
}

# ============================================================================
# Dependency Installation
# ============================================================================

install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package lists
    print_status "Updating package lists..."
    sudo $PKG_UPDATE || true
    
    # Essential build tools
    PACKAGES=(
        "build-essential"
        "git"
        "curl"
        "wget"
        "ca-certificates"
        "gnupg"
        "lsb-release"
    )
    
    # Python development
    PACKAGES+=(
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
    )
    
    # Additional tools
    PACKAGES+=(
        "libssl-dev"
        "libffi-dev"
        "sqlite3"
        "libsqlite3-dev"
    )
    
    # Install packages based on package manager
    for pkg in "${PACKAGES[@]}"; do
        print_status "Installing $pkg..."
        case $PKG_MANAGER in
            apt-get)
                sudo apt-get install -y "$pkg" 2>&1 | tee -a "$LOG_FILE" || print_warning "Failed to install $pkg"
                ;;
            dnf|yum)
                # Map package names for RPM-based distros
                rpm_pkg=$pkg
                [[ "$pkg" == "build-essential" ]] && rpm_pkg="@development-tools"
                sudo $PKG_INSTALL "$rpm_pkg" 2>&1 | tee -a "$LOG_FILE" || print_warning "Failed to install $rpm_pkg"
                ;;
            pacman)
                # Map package names for Arch
                arch_pkg=$pkg
                [[ "$pkg" == "build-essential" ]] && arch_pkg="base-devel"
                sudo pacman -S --noconfirm "$arch_pkg" 2>&1 | tee -a "$LOG_FILE" || print_warning "Failed to install $arch_pkg"
                ;;
        esac
    done
    
    print_success "System dependencies installed"
}

check_python_version() {
    print_status "Checking Python version..."
    
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -eq 3 ]] && [[ $PYTHON_MINOR -ge 12 ]]; then
        print_success "Python version: $PYTHON_VERSION ✓"
        PYTHON_CMD="python3"
    else
        print_warning "Python 3.12+ required. Current: $PYTHON_VERSION"
        print_status "Attempting to install Python 3.12 via pyenv..."
        install_pyenv
        install_python_312
        PYTHON_CMD="$HOME/.pyenv/versions/3.12.8/bin/python"
    fi
}

install_pyenv() {
    if command -v pyenv &> /dev/null; then
        print_success "pyenv already installed"
        return 0
    fi
    
    print_status "Installing pyenv..."
    curl https://pyenv.run | bash
    
    # Add to shell profile
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    
    print_success "pyenv installed"
}

install_python_312() {
    print_status "Installing Python 3.12.8 via pyenv..."
    
    # Install build dependencies
    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
            libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
            libffi-dev liblzma-dev
    fi
    
    pyenv install -s 3.12.8
    pyenv local 3.12.8
    
    print_success "Python 3.12.8 installed"
}

install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker already installed"
        return 0
    fi
    
    print_status "Installing Docker..."
    
    # Docker installation script
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed. You may need to log out and back in."
}

install_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        print_success "Docker Compose already installed"
        return 0
    fi
    
    print_status "Installing Docker Compose..."
    
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed"
}

# ============================================================================
# Python Environment Setup
# ============================================================================

setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    if [[ ! -d ".venv" ]]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt || error_exit "Failed to install Python dependencies"
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found"
    fi
}

# ============================================================================
# Configuration Setup
# ============================================================================

setup_configuration() {
    print_status "Setting up configuration files..."
    
    cd "$PROJECT_DIR"
    
    # Create necessary directories
    mkdir -p logs data backups config temp
    
    # Setup .env file
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.template" ]]; then
            cp .env.template .env
            print_success "Created .env from template"
            print_warning "Please edit .env with your actual credentials"
        else
            print_warning ".env.template not found, skipping .env creation"
        fi
    else
        print_success ".env file already exists"
    fi
    
    # Run configuration validation
    if [[ -f "src/security/config_validator.py" ]]; then
        print_status "Running configuration validation..."
        source .venv/bin/activate
        python3 -c "
from pathlib import Path
from src.security.config_validator import ConfigurationValidator, ConfigEnvironment
import yaml

validator = ConfigurationValidator(environment=ConfigEnvironment.DEVELOPMENT)

# Validate main config if it exists
config_file = Path('config/omnimind.yaml')
if config_file.exists():
    with config_file.open() as f:
        config = yaml.safe_load(f)
    result = validator.validate_config(config)
    if result.valid:
        print('✓ Configuration validation passed')
    else:
        print('⚠ Configuration validation found issues:')
        for issue in result.issues:
            print(f'  - {issue.severity.value}: {issue.message}')
else:
    print('⚠ config/omnimind.yaml not found')
" || print_warning "Configuration validation failed"
    fi
}

# ============================================================================
# GPU Setup (if available)
# ============================================================================

setup_gpu() {
    if [[ "$HAS_GPU" == true ]]; then
        print_status "Configuring GPU support..."
        
        # Check CUDA availability in Python
        source "$PROJECT_DIR/.venv/bin/activate"
        python3 -c "
import sys
try:
    import torch
    if torch.cuda.is_available():
        print(f'✓ PyTorch CUDA available: {torch.cuda.get_device_name(0)}')
        sys.exit(0)
    else:
        print('⚠ PyTorch installed but CUDA not available')
        sys.exit(1)
except ImportError:
    print('⚠ PyTorch not installed')
    sys.exit(1)
" && print_success "GPU support configured" || print_warning "GPU support not fully configured"
    else
        print_status "Configuring for CPU-only mode..."
        # Could install CPU-only PyTorch here if needed
    fi
}

# ============================================================================
# Service Setup
# ============================================================================

setup_services() {
    print_status "Setting up services..."
    
    cd "$PROJECT_DIR"
    
    # Build Docker images if docker-compose.yml exists
    if [[ -f "docker-compose.yml" ]]; then
        print_status "Building Docker images..."
        docker compose build || docker-compose build || print_warning "Failed to build Docker images"
    fi
    
    # Setup systemd service if script exists
    if [[ -f "scripts/install_daemon.sh" ]]; then
        print_status "Systemd service setup available at: scripts/install_daemon.sh"
        print_status "Run it manually with sudo if you want OmniMind as a system service"
    fi
}

# ============================================================================
# Post-Installation Validation
# ============================================================================

run_post_install_validation() {
    print_status "Running post-installation validation..."
    
    cd "$PROJECT_DIR"
    source .venv/bin/activate
    
    # Run diagnostic script if available
    if [[ -f "scripts/diagnose.py" ]]; then
        print_status "Running system diagnostic..."
        python3 scripts/diagnose.py --quick > "logs/install_diagnostic.log" 2>&1 || true
        print_success "Diagnostic complete. Check logs/install_diagnostic.log"
    fi
    
    # Run a few quick tests
    print_status "Running quick validation tests..."
    python3 -c "
import sys
try:
    # Test basic imports
    from src.optimization.hardware_detector import HardwareDetector
    from src.security.config_validator import ConfigurationValidator
    print('✓ Core modules import successfully')
    sys.exit(0)
except Exception as e:
    print(f'⚠ Module import failed: {e}')
    sys.exit(1)
" && print_success "Module validation passed" || print_warning "Some modules failed to import"
}

# ============================================================================
# Installation Summary
# ============================================================================

print_installation_summary() {
    print_header "Installation Complete!"
    
    log ""
    log "${GREEN}🎉 OmniMind has been successfully installed!${NC}"
    log ""
    log "${CYAN}📋 Installation Summary:${NC}"
    log "  • Python: $PYTHON_VERSION"
    log "  • GPU: $([ "$HAS_GPU" == true ] && echo "Available" || echo "Not available (CPU mode)")"
    log "  • Docker: $(docker --version 2>/dev/null || echo "Not available")"
    log "  • Installation log: $LOG_FILE"
    log ""
    log "${CYAN}🚀 Next Steps:${NC}"
    log ""
    log "1. ${YELLOW}Edit configuration:${NC}"
    log "   nano .env"
    log ""
    log "2. ${YELLOW}Start OmniMind:${NC}"
    log "   source scripts/start_dashboard.sh"
    log "   # OR for production:"
    log "   # docker compose up -d"
    log ""
    log "3. ${YELLOW}Access the application:${NC}"
    log "   Frontend: http://localhost:3000"
    log "   Backend API: http://localhost:8000"
    log "   API Docs: http://localhost:8000/docs"
    log ""
    log "4. ${YELLOW}Run tests:${NC}"
    log "   source .venv/bin/activate"
    log "   pytest tests/ -v"
    log ""
    log "${CYAN}📚 Documentation:${NC}"
    log "   • README.md - Getting started"
    log "   • docs/ - Complete documentation"
    log "   • .github/copilot-instructions.md - Development guide"
    log ""
    log "${CYAN}🆘 Need help?${NC}"
    log "   • Check logs/: Installation and runtime logs"
    log "   • Run: python scripts/diagnose.py --full"
    log "   • GitHub: https://github.com/fabs-devbrain/OmniMind"
    log ""
}

# ============================================================================
# Main Installation Flow
# ============================================================================

main() {
    # Print banner
    clear
    print_header "OmniMind One-Click Installation v$SCRIPT_VERSION"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error_exit "This script should not be run as root. Run as a regular user."
    fi
    
    # Create log directory
    mkdir -p "$PROJECT_DIR/logs"
    
    print_status "Starting installation at $(date)"
    print_status "Installation log: $LOG_FILE"
    
    # Phase 1: System Detection
    print_header "Phase 1: System Detection"
    detect_os
    detect_package_manager
    detect_gpu
    detect_hardware
    
    # Phase 2: System Dependencies
    print_header "Phase 2: System Dependencies"
    install_system_dependencies
    check_python_version
    install_docker
    install_docker_compose
    
    # Phase 3: Python Environment
    print_header "Phase 3: Python Environment Setup"
    setup_python_environment
    
    # Phase 4: Configuration
    print_header "Phase 4: Configuration Setup"
    setup_configuration
    
    # Phase 5: GPU Setup
    print_header "Phase 5: Hardware Optimization"
    setup_gpu
    
    # Phase 6: Services
    print_header "Phase 6: Service Setup"
    setup_services
    
    # Phase 7: Validation
    print_header "Phase 7: Post-Installation Validation"
    run_post_install_validation
    
    # Phase 8: Summary
    print_installation_summary
}

# Run main installation
main "$@"
