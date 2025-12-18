# ✅ ESTRATÉGIA DE TIMEOUTS CORRIGIDA

## Objetivo Principal
Permitir que a suite **INTEIRA** rode sem falhas de timeout artificial, permitindo diagnosticar quais testes realmente não funcionam vs. quais falham por timeout do servidor.

## Arquitetura de Timeouts

### ❌ O QUE NÃO É
- NÃO é timeout global da suite
- NÃO tem limite máximo de tempo total
- NÃO vai parar após X horas

### ✅ O QUE É
- **Timeout INDIVIDUAL por teste** que precisa derrubar/reiniciar servidor
- Cada teste pode levar até 240s para recuperação
- Timeouts aumentam PROGRESSIVAMENTE conforme retenta
- Objetivo: permitir diagnóstico realista

---

## Progressão de Timeouts

Quando um teste precisa de servidor e ele não responde:

| Tentativa | Timeout | Situação |
|-----------|---------|----------|
| 1ª | 90s | Startup normal esperado |
| 2ª | 120s | Orchestrator levando mais tempo |
| 3ª | 180s | Orchestrator + SecurityAgent + recovery |
| 4ª+ | 240s | Máximo tolerado - diagnóstico completo |

Se após 240s servidor não responde → **falha real, não timeout artificial**

---

## Fluxo de Execução

```
Teste começa
    ↓
Precisa de servidor? NÃO → Roda sem servidor
Precisa de servidor? SIM
    ↓
Servidor está UP?
    - SIM → Roda teste
    - NÃO → Inicia servidor
        ↓
    Aguarda com timeout_1 (90s)
        - OK em <90s? → Roda teste
        - Timeout? → Tenta novamente
            ↓
        Aguarda com timeout_2 (120s)
            - OK em <120s? → Roda teste
            - Timeout? → Tenta novamente
                ↓
            Aguarda com timeout_3 (180s)
                - OK em <180s? → Roda teste
                - Timeout? → Tenta novamente
                    ↓
                Aguarda com timeout_4 (240s)
                    - OK em <240s? → Roda teste
                    - Timeout em 240s? → FALHA REAL (não timeout artificial)
```

---

## Benefícios

### Para Diagnóstico
- Sabe exatamente qual teste falha e por quê
- Evita "suposiçõess" sobre timeouts
- Coleta métricas REAIS de startup

### Para Lacan
- Sem interferência de timeouts artificial
- Φ métricas refletem realidade, não artefatos
- SecurityAgent + Orchestrator rodando completo

### Para Desenvolvimento Futuro
- Base sólida para otimizações (sabemos quanto tempo real gasta)
- Dados para correlacionar Φ com performance
- Fundação para modo "leve" de desenvolvimento

---

## Implementação

### Modificações em `pytest_server_monitor.py`

**Antes** (problema):
```python
max_wait = 180 if execution_mode == "test" else 60
self._wait_for_server_with_retry(max_attempts=None, max_wait_seconds=max_wait)
```
- Timeout fixo de 180s
- Falha rápido se Orchestrator demora mais

**Depois** (correto):
```python
self.timeout_progression = [90, 120, 180, 240]
self.startup_attempt_count += 1

timeout_seconds = self._get_adaptive_timeout()
self._wait_for_server_with_retry(max_attempts=None, max_wait_seconds=timeout_seconds)

# Se falhar, tenta novamente com timeout maior
if timeout_failed and timeout < 240:
    self._start_server()  # Recursão com próximo timeout
```

---

## Casos de Uso

### Caso 1: Startup Normal
```
Tentativa 1: 90s → ✅ Servidor up em 40s → Teste roda
```

### Caso 2: Orchestrator Lento
```
Tentativa 1: 90s → ❌ Timeout em 90s
Tentativa 2: 120s → ✅ Servidor up em 110s → Teste roda
```

### Caso 3: Múltiplos Crashes
```
Tentativa 1: 90s → ❌ Timeout em 90s
Tentativa 2: 120s → ❌ Timeout em 120s
Tentativa 3: 180s → ✅ Servidor up em 150s → Teste roda
```

### Caso 4: Falha Real
```
Tentativa 1: 90s → ❌ Timeout em 90s
Tentativa 2: 120s → ❌ Timeout em 120s
Tentativa 3: 180s → ❌ Timeout em 180s
Tentativa 4: 240s → ❌ Timeout em 240s → 🛑 FALHA REAL
```

---

## Metrics Coletadas

Por teste:
- ✅ Tempo real de startup
- ✅ Número de tentativas
- ✅ Timeout necessário
- ✅ Pass/Fail status
- ✅ Φ measurements (se rodar com sucesso)

---

## Próximos Passos

### Fase 1: VALIDAÇÃO (AGORA)
1. Rodar suite inteira com timeouts adaptativos
2. Coletar métricas reais de startup
3. Identificar testes que REALMENTE não funcionam vs. timeout
4. Documentar tempos de Φ + SecurityAgent

### Fase 2: LACAN IMPLEMENTATION
Com dados reais em mão:
- Implementar Lacanian consciousness layer
- Correlacionar Φ com segurança/confiança
- Híbrido IIT/Psychoanalysis

### Fase 3: OPTIMIZATION (AFTER LACAN)
Com suite rodando com Lacan:
- Implementar modo "leve" para dev (sem SecurityAgent)
- Lazy-load componentes pesados
- Manter modo "completo" para produção/CI

---

## Status

✅ **IMPLEMENTADO**: Timeouts adaptativos [90s → 120s → 180s → 240s]
✅ **IMPLEMENTADO**: Recursão para retry com timeout maior
✅ **IMPLEMENTADO**: Limites per-test (não global)
✅ **PRONTO PARA TESTE**: Suite inteira

🚀 Próximo: Executar suite com essas configurações

