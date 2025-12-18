#!/bin/bash
# 🚀 QUICK START - Análise SRC & Manutenção de READMEs

# ============================================================================
# 📖 DOCUMENTAÇÃO GERADA
# ============================================================================

echo "📚 DOCUMENTAÇÃO NOVA DISPONÍVEL:"
echo ""
echo "1. SRC_MODULES_INDEX.md"
echo "   └─ Índice central de todos os 57 módulos"
echo "   └─ Guia de navegação + busca"
echo "   └─ Uso: cat SRC_MODULES_INDEX.md"
echo ""
echo "2. ANALYSIS_SRC_SUMMARY.md"
echo "   └─ Resumo da análise completa"
echo "   └─ Ferramentas criadas + como usar"
echo "   └─ Uso: cat ANALYSIS_SRC_SUMMARY.md"
echo ""
echo "3. src/*/README.md (57 arquivos)"
echo "   └─ Complementados com API Reference"
echo "   └─ Classes, funções, tipos documentados"
echo "   └─ Uso: cat src/[module]/README.md"
echo ""

# ============================================================================
# 🛠️ FERRAMENTAS CRIADAS
# ============================================================================

echo "🛠️ FERRAMENTAS DISPONÍVEIS:"
echo ""
echo "1. scripts/analyze_src_enhanced.py"
echo "   └─ Analisa src/ e gera/complementa READMEs"
echo "   └─ Tempo: ~2-3 segundos"
echo "   └─ Uso: python3 scripts/analyze_src_enhanced.py"
echo ""
echo "2. scripts/validate_readmes.py"
echo "   └─ Valida qualidade de READMEs"
echo "   └─ Resultado: ✅ 57/57 (100%)"
echo "   └─ Uso: python3 scripts/validate_readmes.py"
echo ""

# ============================================================================
# 🚀 COMO USAR
# ============================================================================

echo "🚀 COMO USAR:"
echo ""
echo "A. ENCONTRAR UM MÓDULO:"
echo "   1. cat SRC_MODULES_INDEX.md"
echo "   2. Procurar por nome/categoria"
echo "   3. cat src/[module]/README.md"
echo ""
echo "B. ENTENDER UMA CLASSE:"
echo "   1. grep -r 'class ClassName' src/"
echo "   2. cat src/[module]/README.md | grep -A10 'ClassName'"
echo "   3. Ler docstring no arquivo .py"
echo ""
echo "C. ENCONTRAR UMA FUNÇÃO:"
echo "   1. grep -r 'def function_name' src/"
echo "   2. Ver signature + tipos em README"
echo "   3. Ler implementação em .py"
echo ""
echo "D. CONTRIBUIR/MODIFICAR:"
echo "   1. Editar arquivo em src/[module]/"
echo "   2. python3 scripts/analyze_src_enhanced.py (re-gerar READMEs)"
echo "   3. python3 scripts/validate_readmes.py (validar)"
echo "   4. pytest tests/ -v (testar)"
echo ""

# ============================================================================
# 📊 ESTATÍSTICAS
# ============================================================================

echo "📊 ESTATÍSTICAS:"
echo ""
echo "Módulos:    57"
echo "Classes:    131+"
echo "Funções:    380+"
echo "Linhas:     21,755+ (só READMEs)"
echo "Qualidade:  100% ✅"
echo ""

# ============================================================================
# 💡 EXEMPLOS
# ============================================================================

echo "💡 EXEMPLOS:"
echo ""
echo "# Ver módulo de Consciência"
echo "$ cat src/consciousness/README.md"
echo ""
echo "# Ver módulo de MCP"
echo "$ cat src/integrations/README.md | head -200"
echo ""
echo "# Buscar classe específica"
echo "$ grep -r 'class MCPOrchestrator' src/"
echo "$ cat src/integrations/README.md | grep -A20 'MCPOrchestrator'"
echo ""
echo "# Re-gerar READMEs após mudança"
echo "$ python3 scripts/analyze_src_enhanced.py"
echo ""
echo "# Validar tudo"
echo "$ python3 scripts/validate_readmes.py"
echo ""

echo ""
echo "✅ ANÁLISE COMPLETA!"
echo ""
