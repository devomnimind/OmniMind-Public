#!/usr/bin/env python3
"""
Demonstração das Melhorias Implementadas nos Componentes Autopoieticos

Este script demonstra as melhorias aplicadas aos componentes sintetizados
baseadas no aprendizado do sistema de feedback.
"""

import logging
import sys
import time
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Vai para omnimind/
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "autopoietic" / "synthesized_code_secure"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def demonstrate_expanded_kernel_process():
    """Demonstra o ExpandedKernelProcess melhorado."""
    print("\n" + "=" * 80)
    print("🚀 DEMONSTRAÇÃO: ExpandedKernelProcess Melhorado")
    print("=" * 80)

    try:
        # Importar dinamicamente o componente melhorado
        sys.path.insert(0, str(PROJECT_ROOT / "data" / "autopoietic" / "synthesized_code_secure"))
        from modulo_autopoiesis_data_expanded_kernel_process import (
            ExpandedKernelProcess,
        )

        # Criar instância
        kernel = ExpandedKernelProcess()
        print("✅ Componente ExpandedKernelProcess inicializado")

        # Executar
        print("\n🔄 Executando operações expandidas...")
        start_time = time.time()
        result = kernel.run()
        execution_time = time.time() - start_time

        print("✅ Execução concluída!")
        print(f"⏱️  Tempo total: {execution_time:.2f}s")
        print(f"📊 Operações realizadas: {len(result.get('result', {}))}")

        # Mostrar métricas
        metrics = result.get("metrics", {})
        print("\n📈 Métricas coletadas:")
        print(f"  • Total de métricas: {metrics.get('total_metrics', 0)}")
        print(f"  • Uptime: {metrics.get('uptime', 0):.2f}s")

        # Mostrar status detalhado
        status = kernel.get_status()
        print("\n🔍 Status do componente:")
        print(f"  • Estratégia: {status.get('strategy', 'N/A')}")
        print(f"  • Geração: {status.get('generation', 'N/A')}")
        print(f"  • Robustez: {status.get('robustness', 'N/A')}")
        cache_stats = status.get("cache_stats", {})
        print(f"  • Cache hits/misses: {cache_stats.get('hits', 0)}/{cache_stats.get('misses', 0)}")

    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback

        traceback.print_exc()


def demonstrate_stabilized_test_component():
    """Demonstra o StabilizedTestComponent melhorado."""
    print("\n" + "=" * 80)
    print("🛡️ DEMONSTRAÇÃO: StabilizedTestComponent Melhorado")
    print("=" * 80)

    try:
        # Importar dinamicamente
        from modulo_autopoiesis_data_stabilized_test_component import (
            StabilizedTestComponent,
        )

        # Criar instância
        component = StabilizedTestComponent()
        print("✅ Componente StabilizedTestComponent inicializado")

        # Adicionar operações ao buffer
        print("\n📋 Adicionando operações ao buffer...")
        for i in range(5):
            success = component.queue_operation(
                {"id": f"test_op_{i}", "type": "test", "data": f"data_{i}"}
            )
            if success:
                print(f"  ✅ Operação {i} enfileirada")
            else:
                print(f"  ❌ Falha ao enfileirar operação {i}")

        # Executar
        print("\n🔄 Executando componente estabilizado...")
        start_time = time.time()
        result = component.run()
        execution_time = time.time() - start_time

        print("✅ Execução concluída!")
        print(f"⏱️  Tempo total: {execution_time:.2f}s")
        print(f"🎯 Sucesso geral: {result.success}")

        if result.success and result.data:
            data = result.data
            print(f"📊 Operações em buffer processadas: {data.get('buffered_operations', 0)}")
            print(f"🎯 Sucesso geral: {data.get('overall_success', False)}")

            # Mostrar métricas de saúde
            health = data.get("health_metrics", {})
            print("\n🏥 Métricas de saúde:")
            print(f"  • Total de operações: {health.get('total_operations', 0)}")
            print(f"  • Operações bem-sucedidas: {health.get('successful_operations', 0)}")
            print(f"  • Taxa de sucesso: {health.get('success_rate', 0):.2f}")
            print(f"  • Taxa de erro: {health.get('error_rate', 0):.2f}")
            print(f"  • Tempo médio de resposta: {health.get('average_response_time', 0):.2f}s")
            print(f"  • Status circuit breaker: {health.get('circuit_breaker_status', 'unknown')}")

    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback

        traceback.print_exc()


def demonstrate_stabilized_test_kernel():
    """Demonstra o StabilizedTestKernel melhorado."""
    print("\n" + "=" * 80)
    print("🧠 DEMONSTRAÇÃO: StabilizedTestKernel Melhorado")
    print("=" * 80)

    try:
        # Importar dinamicamente
        from modulo_autopoiesis_data_stabilized_test_kernel import StabilizedTestKernel

        # Criar instância
        kernel = StabilizedTestKernel()
        print("✅ Componente StabilizedTestKernel inicializado")

        # Submeter operações de diferentes prioridades
        print("\n📋 Submetendo operações de diferentes prioridades...")
        operations = []

        # Prioridade crítica
        for i in range(2):
            op_id = kernel.submit_operation("process", data=f"critical_data_{i}", priority=3)
            operations.append(op_id)
            print(f"  🚨 Operação crítica submetida: {op_id}")

        # Prioridade alta
        for i in range(3):
            op_id = kernel.submit_operation("read", data=f"high_data_{i}", priority=2)
            operations.append(op_id)
            print(f"  ⚡ Operação alta submetida: {op_id}")

        # Prioridade normal
        for i in range(5):
            op_id = kernel.submit_operation("monitor", data=f"normal_data_{i}", priority=1)
            operations.append(op_id)
            print(f"  📝 Operação normal submetida: {op_id}")

        print(f"\n📊 Total de operações submetidas: {len(operations)}")

        # Executar kernel
        print("\n🔄 Executando kernel estabilizado...")
        start_time = time.time()
        result = kernel.run()
        execution_time = time.time() - start_time

        print("✅ Execução do kernel concluída!")
        print(f"⏱️  Tempo total: {execution_time:.2f}s")
        print(f"🎯 Sucesso: {result.get('success', False)}")

        if result.get("success"):
            print(f"📊 Operações processadas: {result.get('operations_processed', 0)}")
            print(f"🧠 Operações do kernel: {result.get('kernel_operations', 0)}")
            print(f"🚨 Alertas de saúde: {result.get('health_alerts', 0)}")

            # Mostrar métricas do sistema
            sys_metrics = result.get("system_metrics", {})
            print("\n💻 Métricas do sistema:")
            print(f"  • CPU: {sys_metrics.get('cpu_percent', 0):.1f}%")
            print(f"  • Memória: {sys_metrics.get('memory_percent', 0):.1f}%")
            print(f"  • Disco: {sys_metrics.get('disk_usage_percent', 0):.1f}%")
            print(f"  • Conexões de rede: {sys_metrics.get('network_connections', 0)}")

            # Mostrar status final
            final_status = kernel.get_kernel_status()
            print("\n🔍 Status final do kernel:")
            print(f"  • Operações ativas: {final_status.get('active_operations', 0)}")
            print(f"  • Tamanho do cache: {final_status.get('cache_size', 0)}")
            print(f"  • Workers do executor: {final_status.get('executor_workers', 0)}")

            # Mostrar métricas agregadas
            agg_metrics = final_status.get("aggregated_metrics", {})
            if agg_metrics:
                print("\n📈 Métricas agregadas (últimas 10 medições):")
                print(f"  • CPU médio: {agg_metrics.get('avg_cpu_percent', 0):.1f}%")
                print(f"  • Memória média: {agg_metrics.get('avg_memory_percent', 0):.1f}%")
                print(f"  • CPU máximo: {agg_metrics.get('max_cpu_percent', 0):.1f}%")
                print(f"  • Memória máxima: {agg_metrics.get('max_memory_percent', 0):.1f}%")

        # Shutdown graceful
        print("\n🔌 Realizando shutdown graceful...")
        kernel.shutdown()
        print("✅ Kernel desligado com sucesso")

    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback

        traceback.print_exc()


def show_improvements_summary():
    """Mostra resumo das melhorias implementadas."""
    print("\n" + "=" * 80)
    print("🎉 RESUMO DAS MELHORIAS IMPLEMENTADAS")
    print("=" * 80)

    improvements = {
        "Tratamento de erros robusto": [
            "Sistema de recovery automático com múltiplas estratégias",
            "Circuit breaker pattern para proteção contra falhas em cascata",
            "Logging estruturado com níveis apropriados",
            "Graceful degradation quando recovery falha",
        ],
        "Logging abrangente": [
            "Logs estruturados com contexto completo",
            "Níveis de log apropriados (DEBUG, INFO, WARNING, ERROR)",
            "Métricas de performance incluídas nos logs",
            "Tracing de operações para debugging",
        ],
        "Validação de entrada de dados": [
            "Sanitização completa de dados de entrada",
            "Validação de tipos e ranges de valores",
            "Limites de tamanho para prevenir ataques",
            "Validação de segurança em tempo real",
        ],
        "Cache LRU inteligente": [
            "Cache com TTL (Time To Live) automático",
            "Invalidação inteligente de entradas expiradas",
            "Limitação de tamanho para prevenir vazamentos de memória",
            "Estatísticas de hit/miss para otimização",
        ],
        "Otimização de algoritmos": [
            "Uso de algoritmos mais eficientes (ex: busca binária)",
            "Processamento paralelo com ThreadPoolExecutor",
            "Operações assíncronas para melhor performance",
            "Ajuste dinâmico de recursos baseado na carga",
        ],
        "Monitoramento avançado": [
            "Métricas de sistema em tempo real (CPU, memória, disco)",
            "Health checks automatizados com alertas",
            "Monitoramento de performance por operação",
            "Sistema de alertas configurável por thresholds",
        ],
        "Sistema de filas e prioridades": [
            "Filas separadas por nível de prioridade",
            "Processamento justo entre prioridades",
            "Limites de tamanho para prevenir sobrecarga",
            "Métricas de fila para monitoramento",
        ],
    }

    for category, items in improvements.items():
        print(f"\n🔧 {category}:")
        for item in items:
            print(f"  ✓ {item}")

    print(
        f"\n🎯 TOTAL DE MELHORIAS IMPLEMENTADAS: {sum(len(items) for items in improvements.values())}"
    )


def main():
    """Função principal da demonstração."""
    print("🤖 DEMONSTRAÇÃO DOS COMPONENTES AUTOPOIÉTICOS MELHORADOS")
    print("Sistema OmniMind - Aprendizado e Evolução Contínua")
    print("=" * 80)

    # Executar demonstrações
    demonstrate_expanded_kernel_process()
    demonstrate_stabilized_test_component()
    demonstrate_stabilized_test_kernel()

    # Mostrar resumo
    show_improvements_summary()

    print("\n" + "=" * 80)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print("🧠 Os componentes autopoieticos agora são muito mais robustos,")
    print("   eficientes e preparados para evolução contínua baseada em feedback.")
    print("=" * 80)


if __name__ == "__main__":
    main()
