# D-Bus Dependency Setup Guide

## Overview

The OmniMind project uses `dbus-python` for system integration features (media player control, network monitoring, power management, etc.). This requires the D-Bus development libraries to be installed at the system level.

## Required System Dependencies

### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y libdbus-1-dev pkg-config
```

### Linux (Fedora/RHEL/CentOS)
```bash
sudo dnf install dbus-devel pkgconfig
```

### Linux (Arch Linux)
```bash
sudo pacman -S dbus pkgconfig
```

### macOS
```bash
brew install dbus pkg-config
```

## Installation Order

**IMPORTANT**: System dependencies must be installed **before** Python dependencies.

### Correct Order:
```bash
# 1. Install system dependencies first
sudo apt-get install -y libdbus-1-dev pkg-config

# 2. Then install Python dependencies
pip install -r requirements.txt
```

### Common Error
If you see this error:
```
Run-time dependency dbus-1 found: NO (tried pkgconfig and cmake)
ERROR: Dependency "dbus-1" not found, tried pkgconfig and cmake
```

This means you forgot to install the system dependencies first.

## CI/CD Integration

### GitHub Actions
The workflow already includes the required system dependencies:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libdbus-1-dev pkg-config

- name: Install Python dependencies
  run: |
    pip install -r requirements.txt
```

### Docker
The Dockerfile includes both build-time and runtime dependencies:

**Builder stage** (for compiling dbus-python):
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libdbus-1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
```

**Runtime stage** (for running the application):
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*
```

## Troubleshooting

### Problem: pip install fails with dbus-1 not found

**Solution**: Install system dependencies first
```bash
# Ubuntu/Debian
sudo apt-get install -y libdbus-1-dev pkg-config

# Then retry pip install
pip install -r requirements.txt
```

### Problem: Docker build fails

**Solution**: Ensure Dockerfile includes libdbus-1-dev in builder stage
```dockerfile
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y \
    libdbus-1-dev \
    pkg-config
```

### Problem: Application runs but D-Bus features don't work

**Solution**: Install runtime library
```bash
# Ubuntu/Debian
sudo apt-get install -y libdbus-1-3
```

## Why Do We Need This?

The `dbus-python` package provides Python bindings for D-Bus, which is used for:

1. **Media Player Control**: Control VLC, Spotify, etc. via `org.mpris.MediaPlayer2`
2. **Network Monitoring**: Monitor network status via NetworkManager
3. **Power Management**: Get battery status and power state via UPower
4. **System Services**: Query and control systemd services
5. **Desktop Notifications**: Send desktop notifications

These integrations are part of the D-Bus system integration features in `src/integrations/dbus_controller.py`.

## Testing D-Bus Installation

After installation, verify D-Bus works:

```python
import dbus

# Test session bus
session_bus = dbus.SessionBus()
print("Session bus connected:", session_bus is not None)

# Test system bus
system_bus = dbus.SystemBus()
print("System bus connected:", system_bus is not None)
```

## Optional: Skip D-Bus Installation

If you don't need D-Bus features, you can:

1. Comment out `dbus-python` in `requirements.txt`
2. Avoid importing `DBusSessionController` or `DBusSystemController`

However, this will disable system integration features.

## References

- [D-Bus Python Tutorial](https://dbus.freedesktop.org/doc/dbus-python/)
- [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html)
- [GitHub Actions - Setup Dependencies](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
