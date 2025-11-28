"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Validação dedicada do Hugging Face Space devbrain-inference.

Testa conexão, latência e resposta do endpoint /generate.
"""

import logging
import os
import sys
import time
from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("SpaceValidator")


def validate_space():
    """Valida o Space HF com timeout estendido e retry."""
    space_url = os.getenv("HF_SPACE_URL")
    hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

    if not space_url or not hf_token:
        logger.error("❌ HF_SPACE_URL ou HUGGING_FACE_HUB_TOKEN não configurados")
        return False

    logger.info(f"🔍 Validando Space: {space_url}")

    # Test 1: Health check (se disponível)
    try:
        logger.info("Test 1: Health check...")
        health_url = f"{space_url}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Health check OK: {response.json()}")
        else:
            logger.warning(f"⚠️ Health endpoint não disponível (status {response.status_code})")
    except Exception as e:
        logger.warning(f"⚠️ Health check falhou (normal se endpoint não existe): {e}")

    # Test 2: Inference com timeout estendido (120s para cold start)
    try:
        logger.info("Test 2: Inference test (timeout=120s para cold start)...")
        start_time = time.time()

        url = f"{space_url}/generate"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {
            "inputs": "What is 2+2?",
            "parameters": {"max_new_tokens": 50, "temperature": 0.7},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        elapsed = time.time() - start_time

        response.raise_for_status()
        data = response.json()

        logger.info(f"✅ Inference bem-sucedida em {elapsed:.2f}s")
        logger.info(f"📊 Resposta: {data.get('generated_text', '')[:100]}...")

        if elapsed > 30:
            logger.warning(f"⚠️ Latência alta ({elapsed:.2f}s) - cold start detectado")

        return True

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout após 120s - Space pode estar sobrecarregado ou em cold start")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.exception(f"❌ Erro inesperado durante validação: {e}")
        return False


if __name__ == "__main__":
    success = validate_space()
    sys.exit(0 if success else 1)
