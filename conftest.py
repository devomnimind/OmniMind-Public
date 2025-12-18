"""
conftest.py - Configuração global de testes

Configura modo offline para usar modelos em cache local.
"""

import os
import sys

# Adicionar src ao path para poder importar utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Chamar setup_offline_mode ANTES de qualquer import de transformers
from utils.offline_mode import setup_offline_mode  # noqa: E402

setup_offline_mode()

import pytest  # noqa: E402,F401
