# D-Bus Dependency Setup Guide

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)
**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)

---

## Visão Geral

O projeto OmniMind usa `dbus-python` para integração com o sistema (controle de media player, monitoramento de rede, gerenciamento de energia, etc.). Isso requer que as bibliotecas de desenvolvimento D-Bus sejam instaladas no nível do sistema.

**Módulo**: `src/integrations/dbus_controller.py`
- `DBusSessionController`: Controle de sessão D-Bus
- `DBusSystemController`: Controle de sistema D-Bus

## Required System Dependencies

### Linux (Debian/Ubuntu/Kali)
```bash
sudo apt-get update
sudo apt-get install -y libdbus-1-dev pkg-config
```

**Nota**: No Kali Linux, as bibliotecas D-Bus geralmente já estão instaladas, mas é recomendado verificar.

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

## Ordem de Instalação

**CRÍTICO**: Dependências do sistema devem ser instaladas **antes** das dependências Python.

### Ordem Correta:
```bash
# 1. Instalar dependências do sistema primeiro
sudo apt-get install -y libdbus-1-dev pkg-config

# 2. Depois instalar dependências Python
pip install -r requirements/requirements-core.txt
```

**Nota**: Se instalar dependências Python antes das dependências do sistema, o `dbus-python` falhará na compilação.

### Common Error
If you see this error:
```
Run-time dependency dbus-1 found: NO (tried pkgconfig and cmake)
ERROR: Dependency "dbus-1" not found, tried pkgconfig and cmake
```

This means you forgot to install the system dependencies first.

## Verificação de Instalação

### Verificar se D-Bus está disponível

```bash
# Verificar bibliotecas do sistema
pkg-config --modversion dbus-1

# Verificar se dbus-python está instalado
python3 -c "import dbus; print('D-Bus disponível')"
```

### Testar Integração

```python
from src.integrations.dbus_controller import DBusSessionController

try:
    controller = DBusSessionController()
    print("✅ D-Bus funcionando corretamente")
except Exception as e:
    print(f"❌ Erro ao inicializar D-Bus: {e}")
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

### Problema: pip install falha com "dbus-1 not found"

**Solução**: Instalar dependências do sistema primeiro
```bash
# Ubuntu/Debian/Kali
sudo apt-get install -y libdbus-1-dev pkg-config

# Depois tentar novamente pip install
pip install -r requirements/requirements-core.txt
```

### Problema: ImportError ao importar dbus

**Solução**: Verificar se dbus-python está instalado
```bash
# Verificar instalação
pip list | grep dbus-python

# Se não estiver, instalar
pip install dbus-python
```

### Problema: D-Bus não disponível no sistema

**Solução**: Verificar se D-Bus está rodando
```bash
# Verificar serviço D-Bus
systemctl status dbus

# Se não estiver rodando, iniciar
sudo systemctl start dbus
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
