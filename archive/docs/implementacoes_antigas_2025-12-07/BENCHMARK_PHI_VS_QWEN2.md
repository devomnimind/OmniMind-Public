# Benchmark Phi vs Qwen2 - Resultados Preliminares

## Status: ⏳ Em Progresso (Testes rodando)

Os testes estão executando simultaneamente e chamando LLM, o que afeta as medições.
Benchmark será refeito após conclusão dos testes.

## Dados Coletados (Com interferência dos testes)

### Phi (1.6GB - mais leve)
- ✅ Instalado com sucesso
- Simple ("2+2"): **73.67s** (muito lento - provável interferência)
- Medium (quantum): **19.86s**
- Complex (função): **183.07s**
- **Média**: 3.86 tokens/sec

### Qwen2 (4.4GB - já estava)
- ❌ Retornou 404 durante teste (provável fila de espera)
- Dados não coletados

## Próximas Etapas

1. Aguardar conclusão dos testes (`./scripts/run_tests_fast.sh`)
2. Aguardar Ollama ficar livre (sem requisições pendentes)
3. Reexecutar benchmark limpo: `python scripts/benchmark_llm_models.py`
4. Comparar resultados reais
5. Decidir qual modelo usar para otimizar testes

## Script de Benchmark

Criado: `/home/fahbrain/projects/omnimind/scripts/benchmark_llm_models.py`

Uso quando testes terminarem:
```bash
python scripts/benchmark_llm_models.py
```

Medições:
- Latência por prompt
- Tokens/segundo
- Tamanho de resposta
- Comparação de speed
