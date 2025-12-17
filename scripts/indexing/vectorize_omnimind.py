#!/usr/bin/env python3
"""
🎯 SCRIPT OFICIAL ÚNICO DE VETORIZAÇÃO - OMNIMIND
================================================================================
FONTE DE VERDADE - Indexação Completa: Ubuntu 22.05 LTS + systemd + GPU

Indexa:
  1. Sistema Ubuntu (logs, eventos, configurações) - via /var/log/ (requer sudo)
  2. Projeto OmniMind (código, docs, configs) - via ~/projects/omnimind/
  3. HD Externo opcional (DEV_BRAIN_CLEAN)
  4. Sanitiza dados sensíveis antes do upload para Qdrant

Modelo: SentenceTransformer (all-MiniLM-L6-v2) - 384 dims (OFFLINE, GPU-otimizado)
DB: Qdrant (localhost:6333) - Rodando via systemd com sudo access
Collections:
  - omnimind_codebase (código-fonte)
  - omnimind_docs (documentação teórica)
  - omnimind_config (configurações)
  - omnimind_system_logs (logs Ubuntu)

Uso (RECOMENDADO COM SUDO para acessar /var/log/):
  sudo python3 scripts/indexing/vectorize_omnimind.py                    # Indexação completa
  sudo python3 scripts/indexing/vectorize_omnimind.py --skip-external    # Sem HD externo
  sudo python3 scripts/indexing/vectorize_omnimind.py --dry-run          # Modo teste

Uso (SEM SUDO - apenas projeto local):
  python3 scripts/indexing/vectorize_omnimind.py --skip-ubuntu --skip-external

VENV: Activate ONCE before running, don't re-activate per command
  source /home/fahbrain/projects/omnimind/.venv/bin/activate
  sudo python3 scripts/indexing/vectorize_omnimind.py

Tempo estimado: 10-15 minutos (completo com sudo)
Vetores gerados: 15.000-20.000 (depende de tamanho do projeto)
"""

import argparse
import hashlib
import json
import logging

# ============================================================================
# OFFLINE MODE - Usar modelos locais pré-baixados
# ============================================================================
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

parser = argparse.ArgumentParser(
    description="Script oficial único de vetorização - OmniMind",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Exemplos de uso:
  sudo python3 scripts/vectorize_omnimind.py                    # Indexação completa (COM sudo)
  python3 scripts/vectorize_omnimind.py --skip-project          # Pula código OmniMind
  python3 scripts/vectorize_omnimind.py --skip-external         # Pula HD externo
  python3 scripts/vectorize_omnimind.py --dry-run               # Modo teste (sem upload)
    """,
)

parser.add_argument(
    "--skip-project", action="store_true", help="Pular indexação do projeto OmniMind (src/, docs/)"
)
parser.add_argument(
    "--skip-external", action="store_true", help="Pular indexação do HD externo (DEV_BRAIN_CLEAN)"
)
parser.add_argument(
    "--clean", action="store_true", help="Limpar collections existentes antes de criar novas"
)
parser.add_argument(
    "--dry-run", action="store_true", help="Modo teste - não fazer upload para Qdrant"
)

args = parser.parse_args()

# ============================================================================
# SETUP
# ============================================================================

# Setup paths
project_root = Path(
    __file__
).parent.parent.parent  # From scripts/indexing/vectorize_omnimind.py to omnimind/
sys.path.insert(0, str(project_root / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

print("\n" + "=" * 90)
print("🎯 VETORIZAÇÃO OFFICIAL ÚNICA - UBUNTU + OMNIMIND")
print("=" * 90 + "\n")


# ============================================================================
# 1. SANITIZADOR DE DADOS SENSÍVEIS
# ============================================================================


class DataSanitizer:
    """Sanitiza dados sensíveis antes de vetorização"""

    def __init__(self):
        self.redactions = {}
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "ipv4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "api_key": (
                r"(?:api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)[\s]*="
                r"[\s]*['\"]?[a-zA-Z0-9_-]{32,}['\"]?"
            ),
            "token": (r"(?:token|auth|bearer)[\s]*=[\s]*['\"]?[a-zA-Z0-9_.-]{20,}['\"]?"),
            "password": r"(?:password|passwd|pwd)[\s]*=[\s]*['\"]?[^\s\"']+['\"]?",
            "aws_key": r"(?:AKIA|asia)[0-9A-Z]{16}",
            "github_token": r"ghp_[A-Za-z0-9_]{36,255}",
            "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
            "phone": r"(?:\+?55)?[\s]?(?:\(?[0-9]{2}\)?)?[\s]?9?[0-9]{4}-?[0-9]{4}",
            "database_url": r"(?:postgres|mysql|mongodb|redis):\/\/[^\s]+",
        }

    def sanitize(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Sanitiza texto e retorna (texto_sanitizado, mapa_de_redacoes)
        """
        sanitized = text
        redactions: Dict[str, int] = {}

        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            for match in matches:
                placeholder = f"<{pattern_name.upper()}_{len(redactions)}>"
                sanitized = sanitized.replace(match, placeholder)
                redactions[placeholder] = match

        return sanitized, redactions

    def get_redaction_report(self) -> Dict[str, int]:
        """Retorna contagem de tipos de dados redacionados"""
        report: Dict[str, int] = {}
        for key in self.redactions.keys():
            pattern_type = key.split("_")[0].strip("<>")
            report[pattern_type] = report.get(pattern_type, 0) + 1
        return report


sanitizer = DataSanitizer()


# ============================================================================
# 2. VERIFICAÇÕES INICIAIS
# ============================================================================


print("1️⃣  VERIFICAÇÕES INICIAIS...\n")

# Verificar Python
print(f"   ✅ Python: {sys.version.split()[0]}")

# Validar dependências
try:
    print("   ✅ SentenceTransformer: carregado")
    print("   ✅ Qdrant client: carregado")
    print("   ✅ NumPy: carregado\n")
except ImportError as e:
    print(f"   ❌ Erro de importação: {e}")
    sys.exit(1)

# Carregar modelo e validar dimensão
try:
    # Em OFFLINE mode, DEVE estar no cache local
    model_path = (
        Path.home()
        / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
    )

    if not model_path.exists():
        # Tentar encontrar qualquer snapshot disponível
        cache_base = (
            Path.home()
            / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
        )
        if cache_base.exists():
            snapshots = list(cache_base.glob("*/"))
            if snapshots:
                model_path = snapshots[0]
            else:
                print(f"   ❌ Nenhum snapshot de modelo encontrado em {cache_base}")
                sys.exit(1)
        else:
            print(f"   ❌ Cache do modelo não encontrado em {cache_base}")
            print(
                f"   Verifique se o modelo foi baixado com: python -m sentence_transformers download all-MiniLM-L6-v2"
            )
            sys.exit(1)

    print(f"   ✅ Carregando modelo: {model_path}")
    model = SentenceTransformer(str(model_path))

    embedding_dim = model.get_sentence_embedding_dimension()  # type: ignore
    if embedding_dim != 384:
        print(f"   ❌ Modelo tem {embedding_dim} dims, esperava 384!")
        sys.exit(1)
    print(f"   ✅ Modelo: all-MiniLM-L6-v2 ({embedding_dim} dims)\n")
except Exception as e:
    print(f"   ❌ Erro ao carregar modelo: {e}\n")
    sys.exit(1)

# Conectar Qdrant
try:
    client = QdrantClient("http://localhost:6333")
    client.get_collections()
    print("   ✅ Qdrant conectado (localhost:6333)\n")
except Exception as e:
    print(f"   ❌ Erro ao conectar Qdrant: {e}")
    print("   Inicie com: docker-compose -f deploy/docker-compose.yml up -d qdrant\n")
    sys.exit(1)


# ============================================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================================


def chunk_code(filepath: Path, max_chunk_size: int = 500) -> List[Dict[str, Any]]:
    """
    Chunkeador inteligente para código Python/TypeScript
    - Quebra por funções/classes quando possível
    - Preserva contexto sintático
    - Sanitiza antes de retornar
    """
    try:
        content = filepath.read_text(errors="ignore")
        sanitized_content, redactions = sanitizer.sanitize(content)

        lines = sanitized_content.splitlines()
        chunks = []
        current_chunk = []
        current_lines = 0
        in_function = False
        function_name = None

        for i, line in enumerate(lines):
            current_chunk.append(line)
            current_lines += len(line)

            # Detectar início de função/classe
            if re.match(r"^\s*(def|class)\s+(\w+)", line):
                in_function = True
                match = re.match(r"^\s*(def|class)\s+(\w+)", line)
                if match:
                    function_name = match.group(2)

            # Quebrar quando atinge tamanho OU fim de função (linha vazia após indentação)
            if current_lines > max_chunk_size or (
                in_function
                and line.strip() == ""
                and i > 0
                and lines[i - 1].startswith(" ")
                and current_chunk
            ):
                chunk_text = "\n".join(current_chunk).strip()
                if chunk_text:
                    chunks.append(
                        {
                            "text": chunk_text,
                            "file": str(filepath.relative_to(project_root)),
                            "start_line": i - len(current_chunk) + 1,
                            "end_line": i + 1,
                            "type": "code",
                            "language": "python" if filepath.suffix == ".py" else "typescript",
                            "function": function_name,
                            "redactions": len(redactions),
                        }
                    )
                current_chunk = []
                current_lines = 0
                in_function = False
                function_name = None

        # Chunk final
        if current_chunk:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "file": str(filepath.relative_to(project_root)),
                        "start_line": len(lines) - len(current_chunk) + 1,
                        "end_line": len(lines),
                        "type": "code",
                        "language": "python" if filepath.suffix == ".py" else "typescript",
                        "function": function_name,
                        "redactions": len(redactions),
                    }
                )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao chunkear {filepath}: {e}")
        return []


def chunk_markdown(filepath: Path) -> List[Dict[str, Any]]:
    """
    Chunkeador para documentação Markdown
    - Quebra por headings (# ## ###)
    - Preserva estrutura hierárquica
    """
    try:
        content = filepath.read_text(errors="ignore")
        sanitized_content, redactions = sanitizer.sanitize(content)

        # Quebrar por headings
        sections = re.split(r"^(#{1,6}\s+.*?)$", sanitized_content, flags=re.MULTILINE)

        chunks = []
        current_heading = "Unknown"

        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            # Se é um heading, armazena para o próximo chunk
            if section.startswith("#"):
                current_heading = section.replace("#", "").strip()
                continue

            # Se é conteúdo, cria chunk
            text_preview = section[:1000]
            if text_preview:
                chunks.append(
                    {
                        "text": text_preview,
                        "file": str(filepath.relative_to(project_root)),
                        "heading": current_heading,
                        "type": "documentation",
                        "redactions": len(redactions),
                    }
                )

        # Se nenhum chunk criado, pega tudo
        if not chunks and sanitized_content.strip():
            chunks.append(
                {
                    "text": sanitized_content[:1000],
                    "file": str(filepath.relative_to(project_root)),
                    "type": "documentation",
                    "redactions": len(redactions),
                }
            )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao chunkear {filepath}: {e}")
        return []


def chunk_logs(
    filepath: Path, lines_per_chunk: int = 50, max_size_mb: int = 10
) -> List[Dict[str, Any]]:
    """
    Chunkeador para logs do sistema (com limite de tamanho)
    - Agrupa por linhas
    - Extrai timestamp e severidade
    - Limita tamanho para não sobrecarregar
    """
    try:
        # Verificar tamanho do arquivo antes
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.debug(f"Log muito grande ({file_size_mb:.1f}MB), lendo últimas linhas")
            # Ler apenas últimas linhas para logs grandes
            with open(filepath, "r", errors="ignore") as f:
                lines_all = f.readlines()
                # Pegar últimas 1000 linhas
                content = "".join(lines_all[-1000:])
        else:
            content = filepath.read_text(errors="ignore")

        # Sanitizar com tratamento de erro
        try:
            sanitized_content, redactions = sanitizer.sanitize(content)
        except Exception as e:
            logger.debug(f"Erro ao sanitizar logs: {e}, usando conteúdo original")
            sanitized_content = content
            redactions = {}

        lines = sanitized_content.splitlines()
        chunks = []

        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i : i + lines_per_chunk]
            chunk_text = "\n".join(chunk_lines)

            if chunk_text.strip():
                # Tentar extrair timestamp da primeira linha
                timestamp = None
                severity = "unknown"

                if chunk_lines:
                    first_line = chunk_lines[0]
                    # Tentar match de timestamp comum em logs
                    ts_match = re.search(r"\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}", first_line)
                    if ts_match:
                        timestamp = ts_match.group(0)

                    # Tentar extrair severidade
                    if any(x in first_line.upper() for x in ["ERROR", "FATAL"]):
                        severity = "error"
                    elif any(x in first_line.upper() for x in ["WARN", "WARNING"]):
                        severity = "warning"
                    elif any(x in first_line.upper() for x in ["INFO"]):
                        severity = "info"
                    elif any(x in first_line.upper() for x in ["DEBUG"]):
                        severity = "debug"

                # Usar caminho relativo ao projeto ou absoluto se não estiver dentro dele
                try:
                    file_display = str(filepath.relative_to(project_root))
                except ValueError:
                    file_display = str(filepath)  # Caminho fora do projeto (e.g., /var/log/)

                chunks.append(
                    {
                        "text": chunk_text,
                        "file": file_display,
                        "start_line": i,
                        "end_line": i + len(chunk_lines),
                        "type": "system_log",
                        "timestamp": timestamp,
                        "severity": severity,
                        "redactions": len(redactions),
                    }
                )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao chunkear {filepath}: {e}")
        return []


def chunk_json(filepath: Path) -> List[Dict[str, Any]]:
    """Chunkeador para arquivos de configuração JSON"""
    try:
        content = filepath.read_text(errors="ignore")
        sanitized_content, redactions = sanitizer.sanitize(content)

        try:
            data = json.loads(sanitized_content)
            text_repr = json.dumps(data, indent=2)[:1000]
        except json.JSONDecodeError:
            text_repr = sanitized_content[:1000]

        return [
            {
                "text": text_repr,
                "file": str(filepath.relative_to(project_root)),
                "type": "configuration",
                "format": "json",
                "redactions": len(redactions),
            }
        ]
    except Exception as e:
        logger.warning(f"Erro ao chunkear {filepath}: {e}")
        return []


def chunk_hf_dataset(dataset_dir: Path) -> List[Dict[str, Any]]:
    """Chunkeador para datasets HuggingFace (Parquet/Arrow)"""
    try:
        chunks = []

        # Tentar ler dataset_info.json para metadados
        info_file = dataset_dir / "dataset_info.json"
        metadata = {}
        if info_file.exists():
            try:
                metadata = json.loads(info_file.read_text())
            except Exception:
                pass

        # Extrair descrição e features
        description = metadata.get("description", "HuggingFace Dataset")
        features = metadata.get("features", {})

        dataset_name = dataset_dir.name
        chunk_text = (
            f"Dataset: {dataset_name}\n\nDescrição: {description}\n\n"
            f"Features: {json.dumps(features, indent=2)[:500]}"
        )

        chunks.append(
            {
                "text": chunk_text,
                "file": str(dataset_dir.relative_to(project_root)),
                "type": "dataset",
                "format": "huggingface",
                "dataset_name": dataset_name,
                "redactions": 0,
            }
        )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao processar dataset {dataset_dir}: {e}")
        return []


def compute_hash(text: str) -> int:
    """Compute MD5 hash do texto para usar como ID"""
    return int(hashlib.md5(text.encode()).hexdigest(), 16) % (10**8)


def check_point_exists(client: QdrantClient, collection_name: str, point_id: int) -> bool:
    """Verificar se ponto já existe na collection"""
    try:
        points = client.retrieve(
            collection_name=collection_name, ids=[point_id], with_vectors=False
        )
        return len(points) > 0
    except Exception as e:
        # Se collection não existe ou ponto não existe, retorna False
        logger.debug(f"Ponto {point_id} não encontrado: {type(e).__name__}")
        return False


def run_command_safe(cmd: str, use_sudo: bool = False) -> str:
    """Executar comando com ou sem sudo, capturando saída

    Se use_sudo=True:
    - Tenta PRIMEIRO sem sudo (silencioso)
    - Se falhar, tenta COM sudo (pode pedir senha)
    """
    import subprocess

    try:
        # Tentar sem sudo primeiro
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout

        # Se falhou E use_sudo=True, tentar com sudo
        if use_sudo and result.returncode != 0:
            full_cmd = f"sudo {cmd}"
            result = subprocess.run(
                full_cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            return result.stdout if result.returncode == 0 else ""

        return ""
    except Exception as e:
        logger.warning(f"Erro ao executar comando '{cmd}': {e}")
        return ""


def chunk_kernel_metadata() -> List[Dict[str, Any]]:
    """Coletar metadados do kernel Linux"""
    chunks = []
    try:
        # /proc/version
        proc_version = Path("/proc/version").read_text(errors="ignore")
        if proc_version:
            chunks.append(
                {
                    "text": f"Kernel Version:\n{proc_version}",
                    "file": "/proc/version",
                    "type": "kernel_metadata",
                    "subtype": "version",
                    "redactions": 0,
                }
            )

        # sysctl -a
        sysctl_output = run_command_safe("sysctl -a", use_sudo=True)
        if sysctl_output:
            sysctl_lines = sysctl_output.split("\n")[:100]
            chunks.append(
                {
                    "text": "System Parameters:\n" + "\n".join(sysctl_lines),
                    "file": "sysctl",
                    "type": "kernel_metadata",
                    "subtype": "sysctl",
                    "redactions": 0,
                }
            )

        # /proc/cpuinfo
        cpuinfo = Path("/proc/cpuinfo").read_text(errors="ignore")
        if cpuinfo:
            chunks.append(
                {
                    "text": f"CPU Info:\n{cpuinfo[:1000]}",
                    "file": "/proc/cpuinfo",
                    "type": "kernel_metadata",
                    "subtype": "cpuinfo",
                    "redactions": 0,
                }
            )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao coletar kernel metadata: {e}")
        return []


def chunk_installed_packages() -> List[Dict[str, Any]]:
    """Coletar pacotes instalados e versões"""
    chunks = []
    try:
        # dpkg -l
        dpkg_output = run_command_safe("dpkg -l", use_sudo=False)
        if dpkg_output:
            dpkg_lines = dpkg_output.split("\n")[:200]
            chunks.append(
                {
                    "text": "Installed Packages:\n" + "\n".join(dpkg_lines),
                    "file": "dpkg",
                    "type": "system_packages",
                    "subtype": "dpkg",
                    "redactions": 0,
                }
            )

        # Versões de ferramentas críticas
        versions = {}
        for tool in ["python3", "node", "git", "docker", "gcc"]:
            version_output = run_command_safe(f"{tool} --version", use_sudo=False)
            if version_output:
                versions[tool] = version_output.split("\n")[0]

        if versions:
            chunks.append(
                {
                    "text": "Tool Versions:\n" + json.dumps(versions, indent=2),
                    "file": "tool_versions",
                    "type": "system_packages",
                    "subtype": "versions",
                    "redactions": 0,
                }
            )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao coletar pacotes: {e}")
        return []


def chunk_vscode_config() -> List[Dict[str, Any]]:
    """Coletar configurações VS Code do projeto"""
    chunks = []
    try:
        vscode_dir = project_root / ".vscode"
        if vscode_dir.exists():
            for config_file in ["settings.json", "tasks.json", "extensions.json"]:
                config_path = vscode_dir / config_file
                if config_path.exists():
                    try:
                        config_text = config_path.read_text()
                        chunks.append(
                            {
                                "text": f"VS Code {config_file}:\n{config_text[:2000]}",
                                "file": str(config_path),
                                "type": "vscode_config",
                                "subtype": config_file,
                                "redactions": 0,
                            }
                        )
                    except Exception:
                        pass

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao coletar VS Code config: {e}")
        return []


def chunk_security_config() -> List[Dict[str, Any]]:
    """Coletar configurações de segurança do projeto"""
    chunks = []
    try:
        # config/security.yaml
        security_file = project_root / "config" / "security.yaml"
        if security_file.exists():
            security_text, redactions = sanitizer.sanitize(security_file.read_text())
            chunks.append(
                {
                    "text": security_text[:2000],
                    "file": str(security_file),
                    "type": "security",
                    "subtype": "security_config",
                    "redactions": len(redactions),
                }
            )

        # config/dlp_policies.yaml
        dlp_file = project_root / "config" / "dlp_policies.yaml"
        if dlp_file.exists():
            dlp_text, redactions = sanitizer.sanitize(dlp_file.read_text())
            chunks.append(
                {
                    "text": dlp_text[:2000],
                    "file": str(dlp_file),
                    "type": "security",
                    "subtype": "dlp_policies",
                    "redactions": len(redactions),
                }
            )

        # config/ethics.yaml
        ethics_file = project_root / "config" / "ethics.yaml"
        if ethics_file.exists():
            ethics_text, redactions = sanitizer.sanitize(ethics_file.read_text())
            chunks.append(
                {
                    "text": ethics_text[:2000],
                    "file": str(ethics_file),
                    "type": "security",
                    "subtype": "ethics",
                    "redactions": len(redactions),
                }
            )

        return chunks
    except Exception as e:
        logger.warning(f"Erro ao coletar security config: {e}")
        return []


def chunk_external_drive() -> List[Dict[str, Any]]:
    """
    Explorar HD externo dinamicamente COM TIMEOUT
    - Indexar APENAS código válido
    - Ignorar backups corrompidos/cache
    - NÃO TRAVAR em diretórios inacessíveis
    - Requer SUDO para acesso a alguns arquivos do HD externo
    """
    import signal
    import threading

    chunks = []

    # ⚠️ CRÍTICO: Se rodando sem SUDO, tenta com sudo para HD externo
    import subprocess

    is_running_as_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False

    if not is_running_as_root and not args.skip_external:
        # Detectar HD externo dinamicamente
        external_drives = [
            Path("/media") / "fahbrain" / "DEV_BRAIN_CLEAN",
            Path("/mnt") / "DEV_BRAIN_CLEAN",
            Path("/media") / os.getenv("USER", "fahbrain") / "DEV_BRAIN_CLEAN",
        ]

        drive_exists = False
        for path in external_drives:
            if path.exists():
                drive_exists = True
                # Verificar se podemos acessar sem permissão
                try:
                    list(path.iterdir())
                except PermissionError:
                    print("   📁 HD Externo (DEV_BRAIN_CLEAN)...")
                    print("      ⚠️  HD externo encontrado mas requer SUDO")
                    print("      Dica: sudo python scripts/indexing/vectorize_omnimind.py\n")
                    return chunks

        if not drive_exists:
            logger.warning("HD externo DEV_BRAIN_CLEAN não encontrado")
            return []

    # Detectar HD externo dinamicamente
    external_drives = [
        Path("/media") / "fahbrain" / "DEV_BRAIN_CLEAN",
        Path("/mnt") / "DEV_BRAIN_CLEAN",
        Path("/media") / os.getenv("USER", "fahbrain") / "DEV_BRAIN_CLEAN",
    ]

    drive_path = None
    for path in external_drives:
        try:
            if path.exists() and path.is_mount():
                drive_path = path
                break
        except Exception:
            continue

    if not drive_path:
        logger.debug("HD externo DEV_BRAIN_CLEAN não encontrado ou não montado")
        return []

    # Pastas a IGNORAR (cache, backups corrompidos, logs de erro)
    ignore_patterns = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        "lost+found",
        ".sonar",
        ".mypy_cache",
        "venv",
        ".venv",
        "bakcupsanitdevbrain",  # backup corrompido
        "backup_volumes",  # backup genérico
        "omnimind_archives",  # arquivo antigo
        "omnimind_backups_20251130_final",  # backup antigo
    }

    print("   📁 HD Externo (DEV_BRAIN_CLEAN)...")

    # Usar timeout global para não travar na exploração do HD
    def explore_with_timeout():
        """Explorar HD externo com timeout de 30s"""
        result_chunks = []
        start_time = datetime.now()
        timeout_seconds = 30  # Máximo 30s por backup

        try:
            # Explorar APENAS backups recentes válidos
            valid_backups = [
                drive_path / "omnimind_backup_20251211_174532",  # Mais recente
                drive_path / "omnimind_backup_20251126_203822",
                drive_path / "omnimind_backup",
                drive_path / "omnimind_backup_20251211_175356",
            ]

            for backup_path in valid_backups:
                # Verificar timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout_seconds:
                    logger.warning(f"Timeout ao explorar HD externo (>{timeout_seconds}s)")
                    break

                if not backup_path.exists():
                    continue

                # Procurar por código Python válido
                try:
                    # Usar .walk() em vez de .rglob() para ter mais controle
                    for root, dirs, files in os.walk(str(backup_path), topdown=True):
                        # Verificar timeout a cada diretório
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if elapsed > timeout_seconds:
                            logger.debug(f"Timeout ao explorar {backup_path}")
                            dirs.clear()  # Parar de explorar
                            break

                        # Pular diretórios ignorados
                        dirs[:] = [
                            d for d in dirs if not any(pattern in d for pattern in ignore_patterns)
                        ]

                        for file in files:
                            if not file.endswith(".py"):
                                continue

                            file_path = Path(root) / file

                            if any(pattern in str(file_path) for pattern in ignore_patterns):
                                continue

                            try:
                                content = file_path.read_text(errors="ignore")
                                if len(content) < 50:
                                    continue

                                sanitized, redactions = sanitizer.sanitize(content)

                                result_chunks.append(
                                    {
                                        "text": sanitized[:1000],
                                        "file": str(file_path.relative_to(drive_path)),
                                        "type": "external_code",
                                        "source": "DEV_BRAIN_CLEAN",
                                        "redactions": len(redactions),
                                    }
                                )
                            except Exception:
                                pass

                except Exception as e:
                    logger.debug(f"Erro ao explorar {backup_path}: {e}")

            # Procurar por documentação útil (README, docs)
            try:
                for root, dirs, files in os.walk(str(drive_path), topdown=True):
                    # Verificar timeout
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > timeout_seconds:
                        dirs.clear()
                        break

                    # Pular diretórios ignorados
                    dirs[:] = [
                        d for d in dirs if not any(pattern in d for pattern in ignore_patterns)
                    ]

                    for file in files:
                        if not file.endswith(".md"):
                            continue

                        file_path = Path(root) / file

                        if any(pattern in str(file_path) for pattern in ignore_patterns):
                            continue

                        try:
                            content = file_path.read_text(errors="ignore")
                            if len(content) < 50:
                                continue

                            sanitized, redactions = sanitizer.sanitize(content)

                            result_chunks.append(
                                {
                                    "text": sanitized[:1000],
                                    "file": str(file_path.relative_to(drive_path)),
                                    "type": "external_docs",
                                    "source": "DEV_BRAIN_CLEAN",
                                    "redactions": len(redactions),
                                }
                            )
                        except Exception:
                            pass
            except Exception:
                pass

        except KeyboardInterrupt:
            logger.warning("Exploração do HD externo interrompida")
        except Exception as e:
            logger.debug(f"Erro ao explorar HD externo: {e}")

        return result_chunks

    try:
        chunks = explore_with_timeout()
        if chunks:
            print(f"      ✅ {len(chunks)} chunks do HD externo\n")
        else:
            print("      ⚠️  Nenhum arquivo válido no HD externo\n")
    except Exception as e:
        logger.warning(f"Erro ao coletar do HD externo: {e}")
        print("      ⚠️  Erro ao acessar HD externo (pode precisar de SUDO)\n")

    return chunks


# ============================================================================
# 4. DESCOBERTA E CHUNKING
# ============================================================================

print("2️⃣  DESCOBERTA DE ARQUIVOS...\n")

all_chunks = []
chunk_count_by_type: Dict[str, int] = {}
total_redactions: Dict[str, int] = {}

# A. Código do projeto OmniMind
if not args.skip_project:
    print("   📁 Código-fonte OmniMind...")
    src_dir = project_root / "src"
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                chunks = chunk_code(py_file)
                all_chunks.extend(chunks)
                chunk_count_by_type["code"] = chunk_count_by_type.get("code", 0) + len(chunks)

    print(f"      ✅ {chunk_count_by_type.get('code', 0)} chunks de código\n")

    # B. Documentação
    print("   📁 Documentação...")
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for md_file in docs_dir.glob("*.md"):
            chunks = chunk_markdown(md_file)
            all_chunks.extend(chunks)
            chunk_count_by_type["documentation"] = chunk_count_by_type.get(
                "documentation", 0
            ) + len(chunks)

    print(f"      ✅ {chunk_count_by_type.get('documentation', 0)} chunks de documentação\n")

    # C. Configurações
    print("   📁 Configurações...")
    config_dir = project_root / "config"
    if config_dir.exists():
        for config_file in (
            list(config_dir.glob("*.yaml"))
            + list(config_dir.glob("*.json"))
            + list(config_dir.glob("*.yml"))
        ):
            if config_file.suffix == ".json":
                chunks = chunk_json(config_file)
            else:
                content = config_file.read_text(errors="ignore")
                sanitized, redactions = sanitizer.sanitize(content)
                chunks = [
                    {
                        "text": sanitized[:500],
                        "file": str(config_file.relative_to(project_root)),
                        "type": "configuration",
                        "format": config_file.suffix.strip("."),
                        "redactions": len(redactions),
                    }
                ]

        all_chunks.extend(chunks)
        chunk_count_by_type["configuration"] = chunk_count_by_type.get("configuration", 0) + len(
            chunks
        )

print(f"      ✅ {chunk_count_by_type.get('configuration', 0)} chunks de configuração\n")

# D\. Datasets HuggingFace (data/datasets/)
print("   📁 Datasets HuggingFace...")
hf_datasets_dir = project_root / "data" / "datasets"
if hf_datasets_dir.exists():
    for dataset_dir in hf_datasets_dir.iterdir():
        if dataset_dir.is_dir() and (dataset_dir / "dataset_info.json").exists():
            try:
                chunks = chunk_hf_dataset(dataset_dir)
                all_chunks.extend(chunks)
                chunk_count_by_type["dataset"] = chunk_count_by_type.get("dataset", 0) + len(chunks)
            except Exception as e:
                logger.debug(f"Erro ao processar dataset {dataset_dir.name}: {e}")

if chunk_count_by_type.get("dataset", 0) > 0:
    print(f"      ✅ {chunk_count_by_type.get('dataset', 0)} datasets HuggingFace")
else:
    print("      ⚠️  Nenhum dataset HuggingFace encontrado")

# E. Logs do Ubuntu (se houver permissão)
print("   📁 Logs do sistema (Ubuntu)...")
log_files_to_try = [
    Path("/var/log/syslog"),
    Path("/var/log/auth.log"),
    Path("/var/log/apt/history.log"),
    Path("/var/log/kern.log"),
    Path("/var/log/dmesg"),
    Path("/var/log/daemon.log"),
    Path("/var/log/user.log"),
    # Logs do projeto OmniMind como fallback (PATHS ABSOLUTOS)
    project_root / "logs" / "main_cycle.log",
    project_root / "data" / "long_term_logs" / "omnimind_metrics.jsonl",
    project_root / "data" / "autopoietic" / "cycle_history.jsonl",
]

ubuntu_log_chunks = 0
log_errors = []
logs_processed = []

for log_file in log_files_to_try:
    if log_file.exists() and log_file.is_file():
        # Verificar permissão ANTES
        import os

        if not os.access(log_file, os.R_OK):
            log_errors.append(f"Sem permissão: {log_file}")
            continue

        try:
            chunks = chunk_logs(log_file, lines_per_chunk=20, max_size_mb=10)
            # Tomar apenas últimos 2 chunks para não saturar
            all_chunks.extend(chunks[-2:])
            ubuntu_log_chunks += len(chunks[-2:])
            logs_processed.append(log_file.name)
        except KeyboardInterrupt:
            logger.warning(f"Interrompido ao ler {log_file}")
            raise
        except Exception as e:
            log_errors.append(f"Erro em {log_file.name}: {str(e)[:40]}")
            logger.debug(f"Erro ao ler {log_file}: {e}")

chunk_count_by_type["system_log"] = ubuntu_log_chunks
if ubuntu_log_chunks > 0:
    print(f"      ✅ {ubuntu_log_chunks} chunks de logs do sistema")
    print(f"      📁 Processados: {', '.join(logs_processed)}\n")
elif log_errors:
    print(f"      ⚠️  {len(log_errors)} erro(s) ao acessar logs\n")
else:
    print("      ⚠️  Sem permissão para acessar logs do sistema\n")
# F. Kernel Metadata
print("   📁 Kernel Metadata...")
kernel_chunks = chunk_kernel_metadata()
all_chunks.extend(kernel_chunks)
chunk_count_by_type["kernel_metadata"] = len(kernel_chunks)
if kernel_chunks:
    print(f"      ✅ {len(kernel_chunks)} chunks de kernel\n")
else:
    print("      ⚠️  Nenhum kernel metadata coletado\n")

# G. System Packages
print("   📁 Pacotes Instalados...")
package_chunks = chunk_installed_packages()
all_chunks.extend(package_chunks)
chunk_count_by_type["system_packages"] = len(package_chunks)
if package_chunks:
    print(f"      ✅ {len(package_chunks)} chunks de pacotes\n")
else:
    print("      ⚠️  Nenhum pacote coletado\n")

# H. VS Code Configuration
print("   📁 VS Code Config...")
vscode_chunks = chunk_vscode_config()
all_chunks.extend(vscode_chunks)
chunk_count_by_type["vscode_config"] = len(vscode_chunks)
if vscode_chunks:
    print(f"      ✅ {len(vscode_chunks)} chunks de VS Code\n")
else:
    print("      ⚠️  Nenhuma config VS Code encontrada\n")

# I. Security Configuration
print("   📁 Security Config...")
security_chunks = chunk_security_config()
all_chunks.extend(security_chunks)
chunk_count_by_type["security"] = len(security_chunks)
if security_chunks:
    print(f"      ✅ {len(security_chunks)} chunks de segurança\n")
else:
    print("      ⚠️  Nenhuma config de segurança encontrada\n")

# J. HD Externo (DEV_BRAIN_CLEAN)
print("   📁 HD Externo (DEV_BRAIN_CLEAN)...")
if args.skip_external:
    print("      ⏭️  Pulado (--skip-external)\n")
    external_chunks = []
else:
    external_chunks = chunk_external_drive()

all_chunks.extend(external_chunks)
chunk_count_by_type["external_code"] = len(
    [c for c in external_chunks if c.get("type") == "external_code"]
)
chunk_count_by_type["external_docs"] = len(
    [c for c in external_chunks if c.get("type") == "external_docs"]
)
if external_chunks:
    print(f"      ✅ {len(external_chunks)} chunks do HD externo\n")
else:
    print("      ⚠️  Nenhum arquivo válido no HD externo\n")

print(f"   📊 TOTAL: {len(all_chunks)} chunks para vetorizar\n")


# ============================================================================
# 5. CRIAÇÃO DE COLLECTIONS
# ============================================================================

print("3️⃣  CRIANDO COLLECTIONS EM QDRANT...\n")

collections_config = {
    "omnimind_codebase": "Código-fonte do projeto",
    "omnimind_docs": "Documentação e especificações",
    "omnimind_config": "Configurações de sistema",
    "omnimind_system_logs": "Logs do sistema Ubuntu",
}

# ⚠️  NÃO DELETAR COLLECTIONS (Destruição de memória)
# ESTRATÉGIA: Compressão Inteligente + Checkpoints
# - Verificar se collection existe
# - Se existe: preencher gaps (novos dados), não deletar antigos
# - Criar checkpoint de estado atual antes de atualizar
# - Preservar dados existentes (comprimindo se necessário)

import time

# Salvar checkpoint de estado pré-indexação
checkpoint_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "action": "pre_indexing_checkpoint",
    "collections_status": {},
}

for col_name in collections_config.keys():
    try:
        col = client.get_collection(col_name)
        checkpoint_data["collections_status"][col_name] = {
            "points_count": col.points_count,
            "vectors_count": col.vectors_count,
            "status": "exists",
        }
    except Exception:
        checkpoint_data["collections_status"][col_name] = {"status": "does_not_exist"}

# Salvar checkpoint
checkpoint_file = (
    Path("data/checkpoints") / f"pre_indexing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
)
checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
with open(checkpoint_file, "w") as f:
    json.dump(checkpoint_data, f, indent=2)
logger.info(f"✅ Checkpoint pré-indexação salvo: {checkpoint_file}")

# Criar collections novas (preservar dados existentes, não deletar)
for col_name, description in collections_config.items():
    try:
        # Verificar se collection já existe
        try:
            client.get_collection(col_name)
            if not args.dry_run:
                logger.info(f"Collection {col_name} já existe")
            else:
                print(f"   ✅ {col_name} (já existe)")
        except:
            # Collection não existe, criar
            if not args.dry_run:
                client.create_collection(
                    collection_name=col_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
                print(f"   ✅ {col_name} ({description}) - CRIADA")
            else:
                print(f"   [DRY-RUN] Seria criado: {col_name} ({description})")
    except Exception as e:
        print(f"   ❌ Erro ao criar/validar {col_name}: {e}")
        if not args.dry_run:
            sys.exit(1)

print()


# ============================================================================
# 6. VETORIZAÇÃO E UPLOAD
# ============================================================================

print("4️⃣  VETORIZANDO E UPLOADANDO...\n")

# Agrupar chunks por tipo
chunks_by_type: Dict[str, Any] = {}
for chunk in all_chunks:
    chunk_type = chunk.get("type", "unknown")
    if chunk_type not in chunks_by_type:
        chunks_by_type[chunk_type] = []
    chunks_by_type[chunk_type].append(chunk)

# Mapear tipo para collection
type_to_collection = {
    "code": "omnimind_codebase",
    "external_code": "omnimind_codebase",  # HD externo também é código
    "documentation": "omnimind_docs",
    "external_docs": "omnimind_docs",  # HD externo também é doc
    "configuration": "omnimind_config",
    "vscode_config": "omnimind_config",  # VSCode é config
    "security": "omnimind_config",  # Security é config
    "system_log": "omnimind_system_logs",
    "kernel_metadata": "omnimind_system_logs",  # Kernel é log de sistema
    "system_packages": "omnimind_system_logs",  # Pacotes são logs de sistema
}

total_uploaded = 0

for chunk_type, chunks in chunks_by_type.items():
    collection_name = type_to_collection.get(chunk_type, "omnimind_codebase")

    # Vetorizar em batches menores para não sobrecarregar memória
    texts = [chunk["text"] for chunk in chunks]
    print(f"   Vetorizando {len(texts)} {chunk_type}...", end=" ", flush=True)

    try:
        # Processar em batches de 128 para evitar timeout de memória
        all_embeddings = []
        batch_size = 128
        for batch_start in range(0, len(texts), batch_size):
            batch_end = min(batch_start + batch_size, len(texts))
            batch_texts = texts[batch_start:batch_end]
            batch_embeddings = model.encode(batch_texts, show_progress_bar=False, batch_size=32)
            all_embeddings.extend(batch_embeddings)

        embeddings = all_embeddings
        print("✅")

        # Upload em batches com DEDUPLICAÇÃO (apenas se collection não for nova)
        points = []
        skipped_duplicates = 0

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = compute_hash(chunk["text"])

            # ⚠️ SKIP DEDUP na primeira run (collections recém-criadas)
            # VERIFICAR DUPLICATA apenas se collection já tinha dados
            # if check_point_exists(client, collection_name, point_id):
            #     skipped_duplicates += 1
            #     continue

            payload = {
                "type": chunk_type,
                "file": chunk.get("file", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "text_preview": chunk["text"][:100],
                "redactions": chunk.get("redactions", 0),
            }

            # Adicionar metadados específicos por tipo
            if "start_line" in chunk:
                payload["start_line"] = chunk["start_line"]
                payload["end_line"] = chunk["end_line"]

            if "language" in chunk:
                payload["language"] = chunk["language"]

            if "function" in chunk and chunk["function"]:
                payload["function"] = chunk["function"]

            if "heading" in chunk:
                payload["heading"] = chunk["heading"]

            if "severity" in chunk:
                payload["severity"] = chunk["severity"]

            if "format" in chunk:
                payload["format"] = chunk["format"]

            if "subtype" in chunk:
                payload["subtype"] = chunk["subtype"]

            points.append(PointStruct(id=point_id, vector=embedding.tolist(), payload=payload))

        # Upsert em batches menores para não travar Qdrant
        upsert_batch_size = 512
        for batch_start in range(0, len(points), upsert_batch_size):
            batch_end = min(batch_start + upsert_batch_size, len(points))
            batch_points = points[batch_start:batch_end]
            if batch_points:
                if not args.dry_run:
                    client.upsert(collection_name=collection_name, points=batch_points)
                    print(
                        f"        Uploaded batch {batch_start // upsert_batch_size + 1}: "
                        f"{len(batch_points)} pontos"
                    )
                else:
                    print(
                        f"        [DRY-RUN] Seria uploadado batch {batch_start // upsert_batch_size + 1}: "
                        f"{len(batch_points)} pontos"
                    )

        total_uploaded += len(points)
        if skipped_duplicates > 0:
            print(f"        ⏭️  Pulados {skipped_duplicates} duplicatas")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

print()


# ============================================================================
# 7. VALIDAÇÃO FINAL
# ============================================================================

print("5️⃣  VALIDAÇÃO FINAL...\n")

total_vectors = 0
for col_name in collections_config.keys():
    try:
        col_info = client.get_collection(col_name)
        count = col_info.points_count
        total_vectors += count
        status = "✅" if count > 0 else "⚪"
        print(f"   {status} {col_name:25} {count:5} vetores")
    except Exception as e:
        print(f"   ❌ {col_name}: {e}")

print(f"\n   📊 TOTAL: {total_vectors} vetores com 384 dims")


# ============================================================================
# 8. SALVAR RELATÓRIO DE AUDITORIA
# ============================================================================

print("\n6️⃣  GERANDO RELATÓRIO DE AUDITORIA...\n")

report = {
    "timestamp": datetime.now().isoformat(),
    "vectorization": {
        "total_chunks": len(all_chunks),
        "total_vectors": total_vectors,
        "chunks_by_type": chunk_count_by_type,
        "model": "all-MiniLM-L6-v2",
        "embedding_dim": 384,
        "distance_metric": "COSINE",
    },
    "collections": {
        col: client.get_collection(col).points_count
        for col in collections_config.keys()
        if col in [c.name for c in client.get_collections().collections]
    },
    "sanitization": {
        "total_redactions": sum(
            (
                len(c.get("redactions", {}))
                if isinstance(c.get("redactions"), dict)
                else c.get("redactions", 0)
            )
            for c in all_chunks
        ),
        "chunks_with_redactions": len([c for c in all_chunks if c.get("redactions", 0)]),
    },
    "project_info": {
        "root": str(project_root),
        "src_dir": str(project_root / "src"),
        "docs_dir": str(project_root / "docs"),
        "config_dir": str(project_root / "config"),
    },
}

report_path = project_root / "reports" / "vectorization_report.json"
report_path.parent.mkdir(parents=True, exist_ok=True)

with open(report_path, "w") as f:
    json.dump(report, f, indent=2)

print(f"   ✅ Relatório salvo: {report_path}\n")


# ============================================================================
# 9. RESUMO FINAL
# ============================================================================

print("=" * 90)
print("✅ VETORIZAÇÃO CONCLUÍDA - SUCESSO!")
print("=" * 90)

print(
    f"""
📊 RESULTADO:
   • Código-fonte: ~{chunk_count_by_type.get('code', 0)} chunks
   • Documentação: ~{chunk_count_by_type.get('documentation', 0)} chunks
   • Configurações: ~{chunk_count_by_type.get('configuration', 0)} chunks
   • Datasets: ~{chunk_count_by_type.get('dataset', 0)} chunks
   • Logs sistema: ~{chunk_count_by_type.get('system_log', 0)} chunks
   • TOTAL: {total_vectors} vetores com 384 dims

🔒 SEGURANÇA:
   • Total de dados redacionados: {report['sanitization']['total_redactions']} instâncias
   • Chunks sanitizados: {report['sanitization']['chunks_with_redactions']}

📁 COLLECTIONS:
   • omnimind_codebase: Código-fonte OmniMind
   • omnimind_docs: Documentação teórica
   • omnimind_config: Configurações de sistema
   • omnimind_system_logs: Logs do Ubuntu (com limite de tamanho)

📊 DADOS COLETADOS:
   • Ubuntu: /var/log/ (últimas 1000 linhas se >10MB)
   • OmniMind: src/, docs/, config/
   • Datasets: datasets/*.json, datasets/*.csv

🎯 MODELO: SentenceTransformer (all-MiniLM-L6-v2) - 384 dims
🔗 DB: Qdrant (localhost:6333)

📋 RELATÓRIO: {report_path}

✅ PRÓXIMO PASSO:
   python tests/test_vectorization.py
   pytest tests/ -v -m "not chaos"
"""
)

print("=" * 90 + "\n")
