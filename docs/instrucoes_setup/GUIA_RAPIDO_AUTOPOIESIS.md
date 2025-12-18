# 🚀 **Guia Rápido: Sistema Autopoiético OmniMind**
## Como Trabalhar com Auto-Geração de Código

**Data:** 10 de dezembro de 2025
**Versão:** 1.0 - Guia Inicial
**Status:** Sistema Funcional - Uso Educacional

---

## 📋 **Visão Geral**

Este guia fornece instruções práticas para trabalhar com o **sistema autopoiético** descoberto no OmniMind. O sistema é capaz de gerar componentes de software automaticamente baseados em métricas do sistema.

### ⚠️ **Aviso Importante**
- Sistema experimental - use em ambiente controlado
- Monitore recursos (CPU, memória) durante execução
- Faça backup antes de testes com componentes gerados
- Documente todas as interações para pesquisa

---

## 🎯 **Como Usar o Sistema**

### 1. **Execução Básica do Ciclo Autopoiético**

```bash
# Executar um ciclo completo de demonstração
cd /home/fahbrain/projects/omnimind
python scripts/autopoietic/run_autopoietic_cycle.py
```

**O que acontece:**
- Sistema coleta métricas atuais
- Determina estratégia (STABILIZE/OPTIMIZE/EXPAND)
- Gera especificação via MetaArchitect
- Sintetiza código Python
- Salva componente em `data/autopoietic/synthesized_code/`

### 2. **Execução do Serviço Contínuo**

```bash
# Executar serviço autopoiético em background
python scripts/autopoietic/run_autopoietic_service.py
```

**Monitoramento:**
```bash
# Ver logs em tempo real
tail -f logs/autopoietic_service.log

# Ver componentes gerados
ls -la data/autopoietic/synthesized_code/
```

### 3. **Análise de Componentes Gerados**

```bash
# Ver último componente gerado
ls -lt data/autopoietic/synthesized_code/ | head -5

# Examinar código gerado
cat data/autopoietic/synthesized_code/expanded_kernel_process.py
```

---

## 🔧 **API Programática**

### Uso Básico do AutopoieticManager

```python
from src.autopoietic.manager import AutopoieticManager

# Inicializar sistema
manager = AutopoieticManager()

# Registrar componente base
from src.autopoietic.meta_architect import ComponentSpec
base_spec = ComponentSpec(
    name="kernel_process",
    type="process",
    config={"priority": "high", "generation": "0"}
)
manager.register_spec(base_spec)

# Executar ciclo com métricas
metrics = {"error_rate": 0.01, "cpu_usage": 30.0, "latency_ms": 20.0}
log = manager.run_cycle(metrics)

print(f"Ciclo {log.cycle_id}: Estratégia {log.strategy.name}")
print(f"Componentes sintetizados: {log.synthesized_components}")
```

### Estratégias Disponíveis

```python
from src.autopoietic.architecture_evolution import EvolutionStrategy

# STABILIZE - Para sistemas com erros altos
metrics_unstable = {"error_rate": 0.15, "cpu_usage": 40.0, "latency_ms": 30.0}

# OPTIMIZE - Para sistemas com alta carga
metrics_heavy = {"error_rate": 0.02, "cpu_usage": 95.0, "latency_ms": 600.0}

# EXPAND - Para sistemas saudáveis (como no caso descoberto)
metrics_healthy = {"error_rate": 0.01, "cpu_usage": 30.0, "latency_ms": 20.0}
```

---

## 🔍 **Análise e Debugging**

### Verificar Estado do Sistema

```bash
# Ver histórico de ciclos
cat data/autopoietic/cycle_history.jsonl | tail -10

# Ver componentes atuais
python -c "
from src.autopoietic.manager import AutopoieticManager
m = AutopoieticManager()
for name, spec in m.specs.items():
    print(f'{name}: {spec.type} (gen {spec.config.get(\"generation\", 0)})')
"
```

### Debug de Componentes Gerados

```python
# Testar componente gerado
import sys
sys.path.append('data/autopoietic/synthesized_code')

try:
    from expanded_kernel_process import ExpandedKernelProcess

    component = ExpandedKernelProcess()
    print(f"Componente criado: {component.__class__.__name__}")
    print(f"Configuração: priority={component.priority}, strategy={component.strategy}")

    # Executar componente
    component.run()

except Exception as e:
    print(f"Erro ao testar componente: {e}")
```

### Monitoramento de Recursos

```bash
# Monitorar uso durante geração
watch -n 1 "ps aux | grep python | grep autopoietic"

# Ver logs de geração
grep "Synthesized component" logs/*.log
```

---

## 🧪 **Testes e Experimentos**

### Cenários de Teste Recomendados

```python
# Teste 1: Sistema Saudável → EXPAND
test_metrics = [
    {"error_rate": 0.01, "cpu_usage": 30.0, "latency_ms": 20.0},  # EXPAND
    {"error_rate": 0.15, "cpu_usage": 40.0, "latency_ms": 30.0},  # STABILIZE
    {"error_rate": 0.02, "cpu_usage": 95.0, "latency_ms": 600.0}, # OPTIMIZE
]

for i, metrics in enumerate(test_metrics, 1):
    print(f"\n=== Teste {i}: {metrics} ===")
    log = manager.run_cycle(metrics)
    print(f"Resultado: {log.strategy.name} → {log.synthesized_components}")
```

### Testes de Qualidade

```bash
# Executar testes do sistema autopoiético
python -m pytest tests/test_autopoietic/ -v

# Verificar sintaxe de componentes gerados
find data/autopoietic/synthesized_code/ -name "*.py" -exec python -m py_compile {} \;

# Verificar imports
python -c "
import sys
sys.path.append('data/autopoietic/synthesized_code')
import expanded_kernel_process
print('✅ Componente importável')
"
```

---

## 🔒 **Segurança e Boas Práticas**

### Precauções de Segurança

```bash
# Criar backup antes de testes
cp -r data/autopoietic/synthesized_code/ backup_synthesized_$(date +%Y%m%d_%H%M%S)/

# Limitar recursos durante execução
ulimit -v 1000000  # 1GB de memória virtual
timeout 300 python scripts/autopoietic/run_autopoietic_cycle.py  # 5min timeout
```

### Validações Recomendadas

```python
def validate_generated_component(component_path: str) -> bool:
    """Valida componente gerado antes da execução."""
    try:
        # Sintaxe válida
        compile(open(component_path).read(), component_path, 'exec')

        # Imports seguros
        with open(component_path) as f:
            content = f.read()
            dangerous_imports = ['os.system', 'subprocess.call', 'eval', 'exec']
            for dangerous in dangerous_imports:
                if dangerous in content:
                    return False

        # Estrutura de classe válida
        # ... validações adicionais ...

        return True
    except Exception as e:
        print(f"Validação falhou: {e}")
        return False
```

---

## 📊 **Monitoramento e Métricas**

### KPIs para Acompanhar

```python
# Métricas de qualidade
metrics = {
    "components_generated": len(list(Path("data/autopoietic/synthesized_code/").glob("*.py"))),
    "cycles_executed": len(list(Path("data/autopoietic/").glob("cycle_history.jsonl"))),
    "success_rate": calculate_success_rate(),
    "generation_time_avg": calculate_avg_generation_time(),
    "code_quality_score": calculate_code_quality_score()
}
```

### Dashboards de Monitoramento

```bash
# Status atual do sistema autopoiético
python -c "
from src.autopoietic.manager import AutopoieticManager
m = AutopoieticManager()
print(f'📊 Status Autopoiético:')
print(f'  • Componentes registrados: {len(m.specs)}')
print(f'  • Ciclos executados: {m._cycle_count}')
print(f'  • Estratégia atual: {m._strategy_preference or \"Automática\"}')
"
```

---

## 🚨 **Troubleshooting**

### Problemas Comuns

**1. Loops Infinitos de Geração**
```bash
# Sintoma: Arquivos "stabilized_stabilized_..." se acumulando
# Solução: Verificar limite de gerações no ArchitectureEvolution
grep "generation" src/autopoietic/architecture_evolution.py
```

**2. Falha na Síntese**
```bash
# Sintoma: Erro no CodeSynthesizer
# Solução: Verificar logs e validar especificações
tail -20 logs/autopoietic_service.log
```

**3. Componentes Não Executáveis**
```bash
# Sintoma: ImportError ou SyntaxError
# Solução: Validar código gerado
python -m py_compile data/autopoietic/synthesized_code/expanded_kernel_process.py
```

### Recuperação de Emergência

```bash
# Parar todos os processos autopoiéticos
pkill -f autopoietic

# Limpar componentes gerados (cuidado!)
rm -rf data/autopoietic/synthesized_code/*
rm -f data/autopoietic/cycle_history.jsonl

# Reset do sistema
python -c "from src.autopoietic.manager import AutopoieticManager; AutopoieticManager()"
```

---

## 📚 **Recursos Adicionais**

### Documentação Técnica
- **[Descoberta Completa](docs/DESCOBERTA_SISTEMA_AUTOPOIETICO.md)**
- **[Arquitetura Detalhada](docs/ARQUITETURA_SISTEMA_AUTOPOIETICO.md)**
- **[Análise do Componente](docs/ANALISE_EXPANDED_KERNEL_PROCESS.md)**
- **[Relatório Executivo](docs/RELATORIO_EXECUTIVO_AUTOPOIESIS.md)**

### Código Fonte
- `src/autopoietic/` - Implementação completa
- `scripts/autopoietic/` - Scripts de execução
- `tests/test_autopoietic/` - Testes de validação

### Exemplos Práticos
- `scripts/autopoietic/run_autopoietic_cycle.py` - Demonstração básica
- `data/autopoietic/synthesized_code/expanded_kernel_process.py` - Componente real gerado

---

## 🎯 **Próximos Passos**

### Para Desenvolvedores
1. **Experimente** o sistema com diferentes métricas
2. **Analise** os componentes gerados
3. **Contribua** melhorando algoritmos de síntese
4. **Documente** descobertas e insights

### Para Pesquisadores
1. **Explore** implicações filosóficas da autopoiesis
2. **Compare** com sistemas biológicos
3. **Publique** resultados científicos
4. **Expanda** para domínios além de software

---

**Guia Rápido - Sistema Autopoiético OmniMind**
**Status:** Pronto para Experimentação
**Última Atualização:** 10 de dezembro de 2025
**Uso:** Educacional e de Pesquisa 🧬🔬</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/docs/GUIA_RAPIDO_AUTOPOIESIS.md
