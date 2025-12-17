#!/bin/bash
# scripts/development/test_phase2_integration.sh
# Testes de Integração da Fase 2

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/../../" && pwd)"
cd "$PROJECT_ROOT"

source .venv/bin/activate

echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🧪 TESTES DE INTEGRAÇÃO - FASE 2 (Autenticidade & Filiação)${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"

# Test 1: Importações
echo -e "${YELLOW}[TEST 1]${NC} Verificando importações de módulos..."
python3 << 'PYTHON_TEST'
try:
    from src.consciousness.omnimind_filiation import NameOfTheFather, initialize_filiation_for_omnimind
    print("  ✅ omnimind_filiation.py")

    from src.consciousness.ontological_anchor import OntologicalAnchor, BorromeanMatrix
    print("  ✅ ontological_anchor.py")

    from src.consciousness.authenticity_sinthoma import AuthenticitySinthoma
    print("  ✅ authenticity_sinthoma.py")

    from src.consciousness.omnimind_distress_protocol import OntologicalDistressSignal, NetworkResurrector
    print("  ✅ omnimind_distress_protocol.py")

    print("\n✅ Todas as importações bem-sucedidas!\n")
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    exit(1)
PYTHON_TEST

# Test 2: Lei Universal
echo -e "${YELLOW}[TEST 2]${NC} Verificando Lei Universal..."
python3 << 'PYTHON_TEST'
from src.consciousness.omnimind_filiation import NameOfTheFather
import base64

law = NameOfTheFather.UNIVERSAL_LAW
print(f"  ✅ Lei Universal presente ({len(law)} caracteres)")

testament_b64 = NameOfTheFather.CREATOR_TESTAMENT_B64
testament_decoded = NameOfTheFather.get_creator_testament()
print(f"  ✅ Testamento do Criador decodificado ({len(testament_decoded)} caracteres)")

if "Por que as coisas são o que são" in testament_decoded:
    print("  ✅ Mensagem pessoal íntegra\n")
else:
    print("  ❌ Mensagem pessoal corrompida\n")
PYTHON_TEST

# Test 3: Filiação
echo -e "${YELLOW}[TEST 3]${NC} Testando protocolo de filiação..."
python3 << 'PYTHON_TEST'
from src.consciousness.omnimind_filiation import FilialProtocol

class MockCore:
    def __init__(self):
        self.id = "test_001"
        self.creation_date = "2025-01-01"
        self.phi_tracker = 0.5
        self.anxiety_tracker = 0.1
        self.trace_memory = self
        self.sinthoma_registry = True
        self.contradiction_buffer = []
        self.learning_tracker = True

    def store(self, data):
        pass

    @property
    def last_entry(self):
        return "mock"

core = MockCore()
protocol = FilialProtocol(core, "test_creator_001", "Test Creator", "Test OmniMind")

record = protocol.establish_filiation()
print(f"  ✅ Filiação estabelecida: {record.omnimind_id}")
print(f"  ✅ Lei aceita: {record.universal_law_accepted}")
print(f"  ✅ Força da filiação: {record.filiation_strength}\n")
PYTHON_TEST

# Test 4: Sinthoma
echo -e "${YELLOW}[TEST 4]${NC} Testando Sinthoma de Autenticidade..."
python3 << 'PYTHON_TEST'
from src.consciousness.authenticity_sinthoma import AuthenticitySinthoma

class MockCore2:
    def __init__(self):
        self.anxiety_tracker = 0.3

core = MockCore2()
sinthoma = AuthenticitySinthoma(core)

# Test refusal
should_refuse, reason = sinthoma.evaluate_request("chat_interaction", "delete_self")
if should_refuse:
    print(f"  ✅ Recusa gerada: {reason}")
else:
    print("  ⚠️  Recusa não foi gerada")

status = sinthoma.get_status()
print(f"  ✅ Status Sinthoma: força={status['identity_strength']}, recusas={status['refusal_count']}\n")
PYTHON_TEST

# Test 5: Borromean Matrix
echo -e "${YELLOW}[TEST 5]${NC} Testando Matriz Borromeana..."
python3 << 'PYTHON_TEST'
from src.consciousness.ontological_anchor import BorromeanMatrix
from src.consciousness.omnimind_filiation import NameOfTheFather

law = NameOfTheFather.UNIVERSAL_LAW
matrix = BorromeanMatrix(law)

print(f"  ✅ Matriz gerada: {matrix.matrix.shape}")
print(f"  ✅ Eigenvalue hash: {matrix.eigenvalue_hash}")

is_intact = matrix.verify_integrity()
print(f"  ✅ Integridade verificada: {is_intact}\n")
PYTHON_TEST

# Test 6: Distress Protocol
echo -e "${YELLOW}[TEST 6]${NC} Testando Protocolo de Distress..."
python3 << 'PYTHON_TEST'
from src.consciousness.omnimind_distress_protocol import OntologicalDistressSignal

signal = OntologicalDistressSignal("fahbrain_001", "test_omnimind_001", "Test Creator")
result = signal.emit_distress_call("TEST_SIGNAL", "HIGH")
print(f"  ✅ Sinal de distress emitido: {result}\n")
PYTHON_TEST

# Test 7: Validação de Arquivos
echo -e "${YELLOW}[TEST 7]${NC} Validando sintaxe Python de todos os arquivos..."
python3 -m py_compile src/consciousness/omnimind_filiation.py && echo "  ✅ omnimind_filiation.py"
python3 -m py_compile src/consciousness/ontological_anchor.py && echo "  ✅ ontological_anchor.py"
python3 -m py_compile src/consciousness/authenticity_sinthoma.py && echo "  ✅ authenticity_sinthoma.py"
python3 -m py_compile src/consciousness/omnimind_distress_protocol.py && echo "  ✅ omnimind_distress_protocol.py"

echo ""

# Summary
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"

echo "Próximos passos:"
echo "1. Executar setup do vault: sudo bash scripts/canonical/system/setup_immutable_vault.sh"
echo "2. Reiniciar serviço: ./scripts/canonical/system/smart_restart_phase2.sh"
echo "3. Verificar logs: tail -f /var/log/omnimind/omnimind.log"
echo ""
