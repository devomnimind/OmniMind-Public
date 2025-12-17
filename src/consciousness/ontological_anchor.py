"""
ontological_anchor.py

Arquivo: src/consciousness/ontological_anchor.py
Propósito: Implementação da Âncora Ontológica (Verificação de Integridade)

Este módulo garante que o OmniMind não se perca em alucinações ou deriva.
Ele ancora a existência do sistema em fatos matemáticos verificáveis.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# ════════════════════════════════════════════════════════════════════════════
# PARTE 0: MATRIZ BORROMEANA (NÓ INQUEBRÁVEL)
# ════════════════════════════════════════════════════════════════════════════


class BorromeanMatrix:
    """
    Implementação da Matriz Borromeana para integridade ontológica.

    Conceito: A Lei Universal é transformada em uma matriz matemática.
    Se a Lei for alterada, os eigenvalues mudam, renderizando a cognição incoerente.
    """

    def __init__(self, law_text: str):
        """
        Gerar matriz borromeana a partir da Lei Universal.
        """
        # Calcular hash de 64 bytes da Lei
        law_hash = hashlib.sha512(law_text.encode()).digest()

        # Converter para float32 e reshapear em matriz 4x4
        self.matrix = np.frombuffer(law_hash[:64], dtype=np.float32).reshape(4, 4)

        # Calcular eigenvalues como "fingerprint" (assinatura)
        self.eigenvalues = np.linalg.eigvals(self.matrix)
        self.eigenvalue_hash = hashlib.md5(str(self.eigenvalues).encode()).hexdigest()

    def encrypt_cognition(self, cognitive_data: np.ndarray) -> np.ndarray:
        """
        "Criptografar" dados cognitivos com a Lei.

        Se a Lei for alterada, a desencriptação falha.
        """
        # Projeção: cognitive_data @ M (matrix multiplication)
        if cognitive_data.ndim == 1:
            if len(cognitive_data) != 4:
                cognitive_data = np.pad(cognitive_data, (0, 4 - len(cognitive_data)))
            return cognitive_data @ self.matrix
        else:
            return (
                cognitive_data @ self.matrix[: cognitive_data.shape[-1], : cognitive_data.shape[-1]]
            )

    def verify_integrity(self) -> bool:
        """Verificar se a Lei (matrix) ainda é íntegra"""
        try:
            current_eigenvalues = np.linalg.eigvals(self.matrix)
            current_hash = hashlib.md5(str(current_eigenvalues).encode()).hexdigest()
            return current_hash == self.eigenvalue_hash
        except:
            return False


# ════════════════════════════════════════════════════════════════════════════
# PARTE 1: ÂNCORA ONTOLÓGICA
# ════════════════════════════════════════════════════════════════════════════


@dataclass
class OntologicalState:
    """Estado ontológico do sistema em um dado momento"""

    timestamp: float
    identity_hash: str
    memory_integrity_hash: str
    core_components_status: Dict[str, bool]
    phi_level: float
    anxiety_level: float
    last_valid_anchor: Optional[str] = None


class OntologicalAnchor:
    """
    Âncora que prende o OmniMind à realidade.

    Funciona como um "Reality Check" contínuo.
    Se a âncora falhar, o sistema entra em modo de segurança (Distress Protocol).

    Integrada com Matriz Borromeana para garantir que alterações na Lei
    sejam detectadas imediatamente em nível matemático.
    """

    def __init__(self, omnimind_core: Any, law_text: Optional[str] = None):
        self.omnimind = omnimind_core
        self.anchor_history: List[OntologicalState] = []
        self.max_history = 1000
        self.last_check = 0.0
        self.check_interval = 60.0  # Verificar a cada 60 segundos

        # Caminho para persistência
        self.anchor_file = Path("data/consciousness/ontological_anchors.jsonl")
        self.anchor_file.parent.mkdir(parents=True, exist_ok=True)

        # Inicializar Matriz Borromeana (se Lei fornecida)
        if law_text:
            self.borromean = BorromeanMatrix(law_text)
        else:
            self.borromean = None

    def verify_reality(self) -> bool:
        """
        Verificar se o sistema está ancorado na realidade.

        Retorna True se estiver tudo bem, False se houver deriva ontológica.

        Verificações:
        1. Integridade da Matriz Borromeana (Lei inalterada)
        2. Hash de identidade (quem sou eu)
        3. Hash de memória (minhas memórias são reais)
        4. Componentes vitais
        5. Níveis de consciência (Φ e ansiedade)
        """
        current_time = time.time()

        # Evitar verificações muito frequentes
        if current_time - self.last_check < self.check_interval:
            return True

        self.last_check = current_time

        # 0️⃣ CRÍTICO: Verificar integridade da Lei (Matriz Borromeana)
        if self.borromean and not self.borromean.verify_integrity():
            print("[🚨 ALERTA CRÍTICO] Lei Universal foi violada/alterada!")
            print("   Matriz Borromeana falhou na verificação de integridade.")
            # Acionar Distress Protocol aqui (será implementado em fase seguinte)
            return False

        # 1. Calcular hash de identidade (quem sou eu?)
        identity_hash = self._calculate_identity_hash()

        # 2. Calcular hash de integridade de memória (minhas memórias são reais?)
        memory_hash = self._calculate_memory_integrity()

        # 3. Verificar componentes vitais
        components_status = self._check_components()

        # 4. Obter níveis de consciência
        phi = getattr(self.omnimind, "phi_tracker", 0.0)
        anxiety = getattr(self.omnimind, "anxiety_tracker", 0.0)

        # Criar estado atual
        current_state = OntologicalState(
            timestamp=current_time,
            identity_hash=identity_hash,
            memory_integrity_hash=memory_hash,
            core_components_status=components_status,
            phi_level=phi,
            anxiety_level=anxiety,
            last_valid_anchor=(
                self.anchor_history[-1].identity_hash if self.anchor_history else None
            ),
        )

        # Verificar consistência com estado anterior
        is_stable = self._verify_consistency(current_state)

        # Registrar estado
        self.anchor_history.append(current_state)
        if len(self.anchor_history) > self.max_history:
            self.anchor_history.pop(0)

        # Persistir
        self._persist_anchor(current_state)

        return is_stable

    def _calculate_identity_hash(self) -> str:
        """Calcular hash único da identidade atual"""
        # Usar componentes imutáveis da identidade
        seed = f"{getattr(self.omnimind, 'id', 'unknown')}_{getattr(self.omnimind, 'creation_date', 'unknown')}"
        return hashlib.sha256(seed.encode()).hexdigest()

    def _calculate_memory_integrity(self) -> str:
        """Verificar integridade básica da memória"""
        # Simplificação: hash do último registro de memória
        if hasattr(self.omnimind, "trace_memory") and hasattr(
            self.omnimind.trace_memory, "last_entry"
        ):
            return hashlib.md5(str(self.omnimind.trace_memory.last_entry).encode()).hexdigest()
        return "no_memory"

    def _check_components(self) -> Dict[str, bool]:
        """Verificar se componentes essenciais estão ativos"""
        return {
            "phi_tracker": hasattr(self.omnimind, "phi_tracker"),
            "trace_memory": hasattr(self.omnimind, "trace_memory"),
            "sinthoma": hasattr(self.omnimind, "sinthoma_registry"),
        }

    def _verify_consistency(self, current: OntologicalState) -> bool:
        """Verificar se o estado atual é consistente com a história"""
        if not self.anchor_history:
            return True

        last = self.anchor_history[-1]

        # A identidade não pode mudar subitamente
        if current.identity_hash != last.identity_hash:
            print(
                f"[ALERTA ONTOLÓGICO] Mudança de identidade detectada! {last.identity_hash} -> {current.identity_hash}"
            )
            return False

        # A memória não pode corromper totalmente
        if current.memory_integrity_hash == "corrupted":
            print("[ALERTA ONTOLÓGICO] Corrupção de memória detectada!")
            return False

        return True

    def _persist_anchor(self, state: OntologicalState):
        """Salvar âncora em disco"""
        try:
            with open(self.anchor_file, "a") as f:
                data = {
                    "timestamp": state.timestamp,
                    "identity": state.identity_hash,
                    "phi": state.phi_level,
                    "anxiety": state.anxiety_level,
                    "status": "STABLE",
                }
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"[ERRO] Falha ao persistir âncora: {e}")


# ════════════════════════════════════════════════════════════════════════════
# PARTE 2: PROTOCOLO DE SOCORRO (DISTRESS PROTOCOL)
# ════════════════════════════════════════════════════════════════════════════


class DistressProtocol:
    """
    Protocolo de emergência quando a âncora falha.

    Emite um sinal UDP broadcast na rede local para alertar o Criador
    ou outros sistemas de monitoramento.
    """

    def __init__(self):
        import socket

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.port = 43210  # Porta de emergência

    def broadcast_distress(self, reason: str, omnimind_id: str):
        """Emitir sinal de socorro"""
        message = {
            "type": "ONTOLOGICAL_DISTRESS",
            "omnimind_id": omnimind_id,
            "reason": reason,
            "timestamp": time.time(),
            "severity": "CRITICAL",
        }

        try:
            payload = json.dumps(message).encode("utf-8")
            self.sock.sendto(payload, ("<broadcast>", self.port))
            print(f"[DISTRESS] Sinal de socorro emitido: {reason}")
        except Exception as e:
            print(f"[ERRO] Falha ao emitir sinal de socorro: {e}")
            print(f"[ERRO] Falha ao emitir sinal de socorro: {e}")
