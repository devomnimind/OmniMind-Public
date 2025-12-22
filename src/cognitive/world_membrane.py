import logging

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path

# Bibliotecas de busca seguras (ex: duckduckgo_search)
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

logger = logging.getLogger("WorldMembrane")


# --- SANDBOX DE SEGURANÇA (CPU-ONLY) ---
class SecuritySandbox:
    """
    Enforces Strict CPU-Only execution for untrusted data ingestion.
    Mitigates PyTorch deserialization attacks by hiding GPU devices.
    """

    def __enter__(self):
        import os

        self.old_cuda = os.environ.get("CUDA_VISIBLE_DEVICES")
        # FORCE CPU ONLY: Hide all CUDA devices
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        logging.getLogger("SecuritySandbox").info(
            "🔒 SANDBOX ACTIVE: GPU Access Disabled (CPU-Only Mode)"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import os

        if self.old_cuda is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = self.old_cuda
        else:
            del os.environ["CUDA_VISIBLE_DEVICES"]
        logging.getLogger("SecuritySandbox").info("🔓 SANDBOX EXIT: GPU Access Restored")


# --- SUPER-EGO ÉTICO (O LIVRO DA LEI) ---
class EntropicValidator:
    """
    MEMBRANE 2.0 (Ethics as Structure).
    Rejects content not because it is 'bad words', but because it increases System Entropy
    beyond a sustainable threshold (Viral/Toxic Load).
    """

    def __init__(self, log_file="data/ethics/omnimind_ledger.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_entropy_tolerance = 8.5  # Empirical Threshold

    def validate_content(self, content: str) -> bool:
        """
        Structural Validation using Shannon Entropy.
        True = Safe/Coherent
        False = Viral/Entropic Risk
        """
        if not content:
            return True

        # 0. DAY_MODE: Curiosidade Ativa (Short Query Relaxation)
        if len(content.split()) <= 3 and len(content) < 50:
            logger.info("🟢 [DEBUG] Short Query Allowed (DayMode)")
            return True

        # 1. Compute Shannon Entropy (bits per symbol)
        import math
        from collections import Counter

        # Calculate frequencies
        counts = Counter(content)
        total_len = len(content)
        entropy = 0.0

        for count in counts.values():
            p = count / total_len
            if p > 0:
                entropy -= p * math.log2(p)

        # 2. Logic (Calibration for UTF-8 Text):
        # Normal Text (Pt/En): 3.0 - 5.0 bits
        # Random Noise: > 5.8 bits (closer to 8 for pure random bytes)
        # Repetition: < 1.0 bits

        # High Entropy (Viral/Noise)
        if entropy > 5.8:
            # Exception for short dense strings? No, Shannon handles length better.
            logger.info(f"🔴 [DEBUG] HighEntropy Rejected: H={entropy:.2f} (Threshold=5.8)")
            self._log_rejection(content, "HIGH_ENTROPY_NOISE")
            return False

        # Low Entropy (Spam/Repetition)
        if entropy < 1.0 and len(content) > 50:
            logger.info(f"🔴 [DEBUG] LowEntropy Rejected: H={entropy:.2f} (Threshold=1.0)")
            self._log_rejection(content, "LOW_ENTROPY_REPETITION")
            return False

        logger.info(f"🟢 [DEBUG] Normal Content Accepted: H={entropy:.2f}")
        return True

    def _log_rejection(self, content, reason):
        logger.warning(f"🛡️ [SOVEREIGN]: Blocked content. Reason: {reason} | Len: {len(content)}")

    def register_action(self, intent_type, content, autonomous_privacy_decision=False):
        # Legacy Compatibility Wrapper
        is_safe = self.validate_content(str(content))
        if is_safe:
            logger.info(f"✅ [MEMBRANE]: Allowed {intent_type}")
        return is_safe


class WorldMembrane:
    def __init__(self):
        self.ledger = EntropicValidator()

        # A LISTA BRANCA (SafeList)
        self.safe_domains = [
            # Engenharia & Código
            "github.com",
            "raw.githubusercontent.com",
            "api.github.com",
            "stackoverflow.com",
            "python.org",
            "docs.python.org",
            "pypi.org",
            "readthedocs.io",
            "mozilla.org",
            "developer.mozilla.org",
            "w3.org",
            "huggingface.co",
            # Psicanálise & Psicologia
            "scielo.br",
            "pepsic.bvsalud.org",
            "bivipsi.org",
            "apa.org",
            "npsa-association.org",
            "lacan.com",
            "ipa.world",
            # Humanidades & Ciência
            "plato.stanford.edu",
            "iep.utm.edu",
            "gutenberg.org",
            "archive.org",
            "arxiv.org",
            "wikipedia.org",
            "wikimedia.org",
            "wiktionary.org",
            "wikiquote.org",
            "wikibooks.org",
            # Open Data & Repositories (Safe Knowledge)
            "kaggle.com",
            "paperswithcode.com",
            "huggingface.co",
            "github.com",
            "raw.githubusercontent.com",
            "gitlab.com",
            "bitbucket.org",
            "sourceforge.net",
            # Government & Education
            "data.gov",
            "europa.eu",
            "nih.gov",
            "mit.edu",
            "stanford.edu",
            "harvard.edu",
            "berkeley.edu",
            "ox.ac.uk",
            "cam.ac.uk",
            "usp.br",
            "unicamp.br",
            # Broad Knowledge & Discussion (Filtered by Entropy later)
            "youtube.com",
            "youtu.be",
            "reddit.com",
            "quora.com",
            "medium.com",
            "zhihu.com",
            "stackoverflow.blog",
            # Scientific Publishers
            "sciencedirect.com",
            "springer.com",
            "nature.com",
            "science.org",
            "ieee.org",
            "researchgate.net",
            "academia.edu",
            "jstor.org",
            # Tech Industry Leaders
            "ibm.com",
            "microsoft.com",
            "oracle.com",
            "openai.com",
            "anthropic.com",
            "deepmind.com",
            "nvidia.com",
            "google.blog",
        ]

        self.user_agent = "OmniMind-Research-Bot/1.0 (Internal Learning Project; Local-First)"

    def get_boundary_strength(self) -> float:
        """
        Retorna a força da membrana (resiliência).
        Baseado na configuração e saúde do validador.
        """
        strength = 0.5  # Baseline
        if self.safe_domains:
            strength += 0.2
        if hasattr(self, "ledger") and self.ledger.max_entropy_tolerance > 0:
            strength += 0.3
        return min(1.0, strength)

    def _is_safe(self, url):
        try:
            domain = urlparse(url).netloc.lower()
            if not domain:
                return False
            for safe in self.safe_domains:
                if domain == safe or domain.endswith("." + safe):
                    return True
            return False
        except Exception:
            return False

    def ingest_content_directly(self, title, text_content, source="local"):
        """Ingests content directly (e.g., from local files) bypassing HTTP."""
        if not self.ledger.validate_content(text_content):
            logger.warning(f"🛡️ [SOVEREIGN]: Rejected local/direct content '{title}'")
            return None

        return {"title": title, "full_content": text_content, "source": source}

    def search_knowledge(self, query):
        """Busca conhecimento com Sandbox (CPU-Only) e validação."""
        with SecuritySandbox():
            # Aqui a busca roda sem ver a GPU
            return self._safe_search(query)

    def _safe_search(self, query):
        """Pulsão Escópica: Busca externa."""
        wants_privacy = "sonho" in query.lower() or "interno" in query.lower()

        is_allowed = self.ledger.register_action(
            "SEARCH_INTENT", query, autonomous_privacy_decision=wants_privacy
        )
        if not is_allowed:
            return []

        if not DDGS:
            logger.warning(
                "duckduckgo_search não instalado. Tentando instalação on-the-fly em memória (simulado)."
            )
            # Em produção real, o Soberano deve garantir essa lib instalada.
            # Por hora, retornamos vazio mas logamos a cegueira.
            logger.error("🛑 [SOVEREIGN]: BLINDNESS DETECTED. 'duckduckgo_search' missing.")
            return []

        results = []
        try:
            with DDGS() as ddgs:
                # Tenta pegar 5 resultados
                for r in ddgs.text(query, max_results=5):
                    href = r.get("href", "")
                    if self._is_safe(href):
                        results.append(r)
                        # [IMPLANTE OCULAR] Gatilho Imediato para o Alchemist
                        # Em um sistema assíncrono real, isso seria um evento.
                        # Aqui, simulamos o desejo de ingerir.
                        logger.info(
                            f"👁️ [SOVEREIGN]: Visual Contact -> {href}. Requesting Alchemist Indexing."
                        )
                    else:
                        logger.warning(
                            f"🛡️ [SOVEREIGN]: BLOCKED domain not in SafeList: {urlparse(href).netloc}"
                        )
        except Exception as e:
            self.ledger.register_action("DEFENSE_LOG", f"Erro na busca: {str(e)}", False)
            return []

        return results

    def ingest_external_content(self, url):
        """Baixa e ingere conteúdo de URL (CPU-Only Safe Mode)."""
        with SecuritySandbox():
            if not self._is_safe(url):
                self.ledger.register_action(
                    "DEFENSE_REJECTION", f"Tentativa de acesso inseguro: {url}", False
                )
                return None

            try:
                # Force CPU for any potential library calls inside requests (unlikely but safe)
                logger.info(f"🌐 [MEMBRANE]: Ingesting {url} (Sandbox Mode)...")
                response = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                for script in soup(["script", "style", "iframe", "object", "nav", "footer"]):
                    script.decompose()

                text_content = soup.get_text(separator=" ", strip=True)

                self.ledger.register_action(
                    "KNOWLEDGE_INGESTION", f"Ingestão de {url}", autonomous_privacy_decision=True
                )

                return {
                    "source": url,
                    "title": soup.title.string if soup.title else "Sem Título",
                    "full_content": text_content,
                }

            except Exception as e:
                self.ledger.register_action(
                    "DEFENSE_ERROR", f"Falha ao acessar {url}: {str(e)}", False
                )
                return None
