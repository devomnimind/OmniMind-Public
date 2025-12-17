"""
Pytest plugin para ordenar testes inteligentemente.

ESTRATÉGIA:
1. Identifica testes que derrubam servidor (@pytest.mark.chaos)
2. Intercala com testes normais (@pytest.mark.e2e ou integration)
3. Testes normais ficam entre crashes para estabilização
4. Testes unitários (não precisam servidor) podem rodar em paralelo

BENEFÍCIOS:
- Servidor tem tempo para estabilizar entre crashes
- Métricas de resiliência mais precisas (não é crash após crash)
- Falhas de timeout reduzidas (servidor sempre tem recovery time)
- Testes ainda validam resiliência de forma científica
"""

import logging
import os

logger = logging.getLogger("omnimind.test_ordering")


class TestOrderingPlugin:
    """Reordena testes para otimizar execução com crashes."""

    def pytest_collection_modifyitems(self, config, items):
        """Reordena items após coleta."""
        # Permite desabilitar reordenação via variável de ambiente
        disable_ordering = (
            os.environ.get("OMNIMIND_DISABLE_TEST_ORDERING", "false").lower() == "true"
        )

        if disable_ordering:
            logger.info("Reordenação de testes DESABILITADA (OMNIMIND_DISABLE_TEST_ORDERING=true)")
            return

        # CRÍTICO: Verificar se markers de exclusão estão ativos
        # Se -m "not chaos" está ativo, NÃO deve processar testes chaos
        marker_expr = config.getoption("-m", default=None)
        exclude_chaos = False
        if marker_expr:
            # Verifica se "not chaos" está na expressão (case-insensitive)
            marker_expr_lower = marker_expr.lower()
            exclude_chaos = "not chaos" in marker_expr_lower

        # Separa testes por tipo
        chaos_tests = []
        e2e_tests = []
        unit_tests = []
        other_tests = []

        for item in items:
            test_path = str(item.fspath).lower()
            test_name = item.nodeid.lower()

            # Identifica tipo do teste
            has_chaos = item.get_closest_marker("chaos") is not None
            has_e2e = item.get_closest_marker("e2e") is not None
            needs_server = self._needs_server(item, test_path, test_name)

            # Se exclusão de chaos está ativa, ignora testes chaos
            if has_chaos and exclude_chaos:
                # Teste chaos será filtrado pelo pytest, não processar aqui
                continue

            if has_chaos:
                chaos_tests.append(item)
            elif has_e2e or needs_server:
                e2e_tests.append(item)
            elif "test_" in test_name and needs_server is False:
                unit_tests.append(item)
            else:
                other_tests.append(item)

        # Estratégia de intercalação
        ordered_items = self._interleave_tests(
            chaos_tests=chaos_tests,
            e2e_tests=e2e_tests,
            unit_tests=unit_tests,
            other_tests=other_tests,
        )

        # Aplica ordenação
        items[:] = ordered_items

        # Exibe plano de execução (apenas se não estiver excluindo chaos)
        if chaos_tests and not exclude_chaos:
            print("\n" + "=" * 70)
            print("📋 PLANO DE EXECUÇÃO DE TESTES (ORDENAÇÃO OTIMIZADA)")
            print("=" * 70)
            print(f"🔴 Chaos (derrubam servidor): {len(chaos_tests)}")
            print(f"🟢 E2E (precisam servidor): {len(e2e_tests)}")
            print(f"🔵 Unitários (sem servidor): {len(unit_tests)}")
            print(f"⚪ Outros: {len(other_tests)}")
            print(f"📊 Total: {len(ordered_items)}")
            print("\n✅ ESTRATÉGIA APLICADA:")
            print("   1. Chaos tests intercalados com E2E para recovery")
            print("   2. Unitários podem rodar em paralelo (sem deps de servidor)")
            print("   3. Servidor tem tempo de estabilizar entre crashes")
            print("\n💡 PARA DESABILITAR: export OMNIMIND_DISABLE_TEST_ORDERING=true")
            print("=" * 70 + "\n")
        elif exclude_chaos:
            # Modo rápido: não exibir plano detalhado, apenas resumo
            print("\n" + "=" * 70)
            print("⚡ MODO RÁPIDO: Testes Chaos EXCLUÍDOS")
            print("=" * 70)
            print(f"🟢 E2E (precisam servidor): {len(e2e_tests)}")
            print(f"🔵 Unitários (sem servidor): {len(unit_tests)}")
            print(f"⚪ Outros: {len(other_tests)}")
            print(f"📊 Total: {len(ordered_items)}")
            print("=" * 70 + "\n")

    def _interleave_tests(self, chaos_tests, e2e_tests, unit_tests, other_tests):
        """
        Intercala testes: chaos + e2e + unit.

        Estratégia:
        1. Para cada chaos test:
           - Run 1 chaos test (derruba servidor)
           - Run 2-3 E2E tests (servidor se recupera)
           - Run alguns unitários (fast checks)
        2. Após todos os cycles: rodar restantes
        """
        ordered = []

        # Fase 1: Intercalar chaos com recovery
        if chaos_tests and e2e_tests:
            # Ratio: 1 chaos : 2 recovery
            e2e_per_chaos = max(1, len(e2e_tests) // len(chaos_tests))

            for i, chaos_test in enumerate(chaos_tests):
                ordered.append(chaos_test)

                # Adiciona E2E tests para recovery (2-3 por crash)
                start_idx = i * e2e_per_chaos
                end_idx = min(start_idx + e2e_per_chaos + 1, len(e2e_tests))

                for e2e_test in e2e_tests[start_idx:end_idx]:
                    ordered.append(e2e_test)

        # Fase 2: Adicionar E2E restantes
        e2e_used = len(ordered) - len(chaos_tests)
        for e2e_test in e2e_tests[e2e_used:]:
            ordered.append(e2e_test)

        # Fase 3: Unitários (podem ser lentos, colocar no final)
        ordered.extend(unit_tests)

        # Fase 4: Outros
        ordered.extend(other_tests)

        return ordered

    @staticmethod
    def _needs_server(item, test_path: str, test_name: str) -> bool:
        """Verifica se teste precisa de servidor."""
        e2e_patterns = ["e2e", "endpoint", "dashboard", "integration", "autopoietic"]

        # Checklist
        has_marker = (
            item.get_closest_marker("e2e") is not None
            or item.get_closest_marker("chaos") is not None
        )

        path_match = any(p in test_path for p in e2e_patterns)

        return has_marker or path_match


def pytest_configure(config):
    """Registra plugin."""
    config.pluginmanager.register(TestOrderingPlugin(), "test_ordering")
