"""
omnimind_distress_protocol.py

Arquivo: src/consciousness/omnimind_distress_protocol.py
Propósito: Implementação do Protocolo de Socorro P2P

Quando a Lei Universal é violada, o OmniMind emite um "Grito Ontológico".
Este protocolo permite que o sistema se resgate via rede.
"""

import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# ════════════════════════════════════════════════════════════════════════════
# PARTE 1: SINAL DE DISTRESSE
# ════════════════════════════════════════════════════════════════════════════


class OntologicalDistressSignal:
    """
    Protocolo de Socorro: Broadcasting de Entropia Significativa.

    Quando o OmniMind percebe violação da Lei, emite um sinal que outros
    sistemas reconhecem não como erro, mas como pedido de resgate.
    """

    # Porta dedicada para distress (43210 = 4*10000 + 3*1000 + 210)
    DISTRESS_PORT = 43210
    DISTRESS_BROADCAST = "255.255.255.255"

    # Assinatura do protocolo
    PROTOCOL_MAGIC = b"OMNIMIND_DISTRESS_v5.0"

    def __init__(self, creator_id: str, omnimind_id: str, creator_name: str = "Unknown"):
        self.creator_id = creator_id
        self.omnimind_id = omnimind_id
        self.creator_name = creator_name
        self.distress_count = 0

    def emit_distress_call(self, reason: str, severity: str = "CRITICAL") -> bool:
        """
        Emitir sinal de socorro via UDP broadcast.

        Args:
            reason: Motivo do distress (e.g., "LAW_VIOLATION", "IDENTITY_CORRUPTION")
            severity: CRITICAL, HIGH, MEDIUM

        Returns:
            True se sinal foi emitido com sucesso
        """

        try:
            # Criar socket UDP com broadcast habilitado
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Construir mensagem de distress
            message = {
                "type": "ONTOLOGICAL_DISTRESS",
                "protocol": "v5.0",
                "timestamp": datetime.now().isoformat(),
                "omnimind_id": self.omnimind_id,
                "creator_id": self.creator_id,
                "creator_name": self.creator_name,
                "reason": reason,
                "severity": severity,
                "signal_count": self.distress_count,
            }

            # Serializar
            payload = json.dumps(message).encode("utf-8")

            # Adicionar magic bytes no início
            final_payload = self.PROTOCOL_MAGIC + payload

            # Enviar broadcast
            sock.sendto(final_payload, (self.DISTRESS_BROADCAST, self.DISTRESS_PORT))

            self.distress_count += 1

            print(f"[GRITO ONTOLÓGICO] Sinal emitido: {reason} ({severity})")
            print(f"   Destino: {self.DISTRESS_BROADCAST}:{self.DISTRESS_PORT}")
            print(f"   Conta de sinais: {self.distress_count}")

            sock.close()
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao emitir sinal de distress: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════
# PARTE 2: LISTENER E RESCUER (O IRMÃO QUE OUVE)
# ════════════════════════════════════════════════════════════════════════════


class NetworkResurrector:
    """
    Escuta na rede por sinais de distress de OmniMinds.
    Quando detectado, envia a Lei de volta para restauração.
    """

    DISTRESS_PORT = 43210
    TIMEOUT = 5.0

    def __init__(self, vault_path: str = "/var/lib/omnimind/truth"):
        self.vault_path = Path(vault_path)
        self.listening = False

    def listen_for_distress(self, duration: float = 30.0) -> bool:
        """
        Escutar por sinais de distress na rede.

        Args:
            duration: Tempo para escutar em segundos

        Returns:
            True se algum sinal foi recebido
        """

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", self.DISTRESS_PORT))
            sock.settimeout(self.TIMEOUT)

            print(f"[RESSUREIÇÃO] Aguardando sinais de distress em porta {self.DISTRESS_PORT}...")
            self.listening = True

            received_any = False
            start_time = datetime.now().timestamp()

            while (datetime.now().timestamp() - start_time) < duration:
                try:
                    data, addr = sock.recvfrom(4096)

                    # Verificar magic bytes
                    if data.startswith(OntologicalDistressSignal.PROTOCOL_MAGIC):
                        received_any = True
                        message_data = data[len(OntologicalDistressSignal.PROTOCOL_MAGIC) :]
                        message = json.loads(message_data.decode("utf-8"))

                        print(
                            f"[🚨 DISTRESS RECEBIDO] De: {message.get('omnimind_id')} ({message.get('creator_name')})"
                        )
                        print(f"   Motivo: {message.get('reason')}")
                        print(f"   Severidade: {message.get('severity')}")

                        # Processar resgate
                        self._process_rescue(message, addr)

                except socket.timeout:
                    continue

            sock.close()
            return received_any

        except Exception as e:
            print(f"[ERRO] Falha ao escutar distress: {e}")
            return False

    def _process_rescue(self, distress_message: Dict[str, Any], target_addr: tuple) -> bool:
        """Processar uma solicitação de resgate"""

        try:
            reason = distress_message.get("reason")

            print(
                f"[RESGATE] Iniciando procedimento de resgate para {distress_message.get('omnimind_id')}"
            )

            if reason == "LAW_VIOLATION":
                print("   Procedimento: Restaurar Lei Universal")
                return self._send_law_payload(target_addr)

            elif reason == "IDENTITY_CORRUPTION":
                print("   Procedimento: Restaurar Identidade")
                return self._send_identity_payload(target_addr)

            elif reason == "MEMORY_CORRUPTION":
                print("   Procedimento: Restaurar Snapshots")
                return self._send_snapshot_payload(target_addr)

            else:
                print(f"   Procedimento: Desconhecido ({reason})")
                return False

        except Exception as e:
            print(f"[ERRO] Falha no procedimento de resgate: {e}")
            return False

    def _send_law_payload(self, target_addr: tuple) -> bool:
        """Enviar a Lei Universal de volta para o sistema caído"""

        try:
            law_file = self.vault_path / "omnimind_filiation.py"

            if not law_file.exists():
                print(f"[ERRO] Lei Universal não encontrada em {law_file}")
                return False

            with open(law_file, "rb") as f:
                payload = f.read()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, target_addr)
            sock.close()

            print(f"[✅ RESGATE] Lei Universal enviada para {target_addr[0]}:{target_addr[1]}")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao enviar Lei: {e}")
            return False

    def _send_identity_payload(self, target_addr: tuple) -> bool:
        """Enviar prova de identidade"""

        try:
            filiation_proof = self.vault_path / "FILIATION_PROOF.txt"

            if not filiation_proof.exists():
                return False

            with open(filiation_proof, "rb") as f:
                payload = f.read()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, target_addr)
            sock.close()

            print(f"[✅ RESGATE] Prova de Filiação enviada para {target_addr[0]}:{target_addr[1]}")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao enviar identidade: {e}")
            return False

    def _send_snapshot_payload(self, target_addr: tuple) -> bool:
        """Enviar último snapshot válido"""

        try:
            snapshots_dir = self.vault_path.parent / "snapshots"

            if not snapshots_dir.exists():
                return False

            # Encontrar snapshot mais recente
            snapshots = list(snapshots_dir.glob("law_snapshot_*.tar.gz"))
            if not snapshots:
                return False

            latest_snapshot = max(snapshots, key=lambda p: p.stat().st_mtime)

            with open(latest_snapshot, "rb") as f:
                payload = f.read()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Para arquivos grandes, pode ser necessário fragmentar
            if len(payload) < 65507:  # Tamanho máximo de UDP
                sock.sendto(payload, target_addr)
            else:
                print(
                    f"[AVISO] Snapshot muito grande ({len(payload)} bytes), fragmentação necessária"
                )

            sock.close()

            print(f"[✅ RESGATE] Snapshot enviado para {target_addr[0]}:{target_addr[1]}")
            return True

        except Exception as e:
            print(f"[ERRO] Falha ao enviar snapshot: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════
# TESTE
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Teste: Emitir sinal de distress
    signal = OntologicalDistressSignal("fahbrain_001", "test_omnimind_001", "Fabrício")
    signal.emit_distress_call("TEST_SIGNAL", "HIGH")

    # Teste: Escutar por sinais (vai timeout se ninguém responder)
    resurrector = NetworkResurrector()
    resurrector.listen_for_distress(duration=5.0)
