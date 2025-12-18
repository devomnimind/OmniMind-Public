# ROADMAP DIÁRIO: TRABALHANDO NO OMNIMIND COMO PROGRAMADOR INICIANTE

**Objetivo:** Guia prático para trabalhar diariamente no OmniMind, focando em produtividade e aprendizado independente.

**Princípio:** Use Copilot/GitHub Copilot como mentor principal, mas desenvolva autonomia gradual.

---

## 📅 ESTRUTURA DIÁRIA TÍPICA (2-3 horas/dia)

### 🌅 MANHÃ: SETUP E DIAGNÓSTICO (30-45 min)

#### 1. Verificar Estado do Sistema
```bash
# Status geral
cd /home/fahbrain/projects/omnimind
git status
python -m pytest tests/ -x --tb=short -q | head -20

# Verificar se Φ está OK
python scripts/science_validation/robust_expectation_validation.py --seeds 5

# Dashboard se disponível
timeout 10 npm run dev  # web/frontend
```

#### 2. Atualizar Ambiente
```bash
# Se necessário
pip install -r requirements.txt
python scripts/setup_dev.sh
```

#### 3. Verificar Issues Ativos
- Olhar TODOs no código
- Verificar falhas recentes nos testes
- Checar logs por erros

### 🌞 MEIO-DIA: DESENVOLVIMENTO FOCADO (1-1.5 horas)

#### 1. Escolher Tarefa Pequena
**Priorize por dificuldade crescente:**
- 🔰 **Fácil:** Fix typos, melhorar comentários, adicionar logs
- 🔰 **Médio:** Pequenos refactors, novos testes unitários
- ⚠️ **Difícil:** Features novas, mudanças na API (usar Copilot)

#### 2. Workflow Básico
```bash
# Criar branch para tarefa
git checkout -b feature/minha-tarefa-pequena

# Fazer mudanças pequenas
# Usar Copilot para gerar código
# Testar mudanças
python -m pytest tests/arquivo_que_mudei.py -v

# Commit se funcionar
git add .
git commit -m "feat: pequena melhoria X"
```

#### 3. Tipos de Tarefas Diárias Recomendadas

**Dia 1-7: Exploração e Fixes Pequenos**
- Corrigir comentários incorretos
- Adicionar type hints faltantes
- Melhorar nomes de variáveis/funções
- Adicionar logs de debug

**Dia 8-14: Testes e Qualidade**
- Escrever testes para código não testado
- Melhorar cobertura de testes
- Fix testes quebrados (se souber como)
- Adicionar assertions

**Dia 15-21: Pequenas Features**
- Implementar funções utilitárias
- Melhorar error handling
- Adicionar configurações opcionais
- Criar scripts auxiliares

**Dia 22-28: Refactoring**
- Extrair funções duplicadas
- Simplificar condicionais complexas
- Melhorar estrutura de classes
- Otimizar performance pequena

### 🌆 TARDE: APRENDIZADO E REVISÃO (30-45 min)

#### 1. Revisar Código Escrito
- Ler o que foi implementado
- Entender por que funciona
- Documentar aprendizados

#### 2. Estudar Documentação
```bash
# Ler docs relevantes
cat docs/TECHNICAL_REPORT_OMNIMIND_DEVELOPMENT.md | grep -A 10 "Problema Atual"
cat README.md
```

#### 3. Preparar para Próximo Dia
- Anotar dúvidas para perguntar ao Copilot
- Planejar próxima tarefa pequena
- Revisar progresso semanal

---

## 🛠️ FERRAMENTAS ESSENCIAIS PARA INICIANTE

### 1. Comandos Básicos (Aprenda Primeiro)
```bash
# Navegação
cd /home/fahbrain/projects/omnimind
ls -la
find . -name "*.py" | head -10

# Git básico
git status
git log --oneline -5
git diff
git add .
git commit -m "mensagem"
git push origin main

# Testes
python -m pytest tests/ -k "test_nome" -v
python -m pytest tests/ --tb=short

# Lint/Format
black src/
flake8 src/
```

### 2. Estrutura do Projeto (Memorize)
```
omnimind/
├── src/           # Código fonte principal
├── tests/         # Testes
├── scripts/       # Scripts utilitários
├── docs/          # Documentação
├── config/        # Configurações
├── data/          # Dados
└── real_evidence/ # Resultados de validação
```

### 3. Como Pedir Ajuda ao Copilot
**Seja específico:**
- ❌ "Não funciona" → ✅ "Erro: TypeError em linha 45 de arquivo.py"
- ❌ "Me ajude" → ✅ "Como implementar função que calcula média de lista?"
- ❌ "Quebrado" → ✅ "Teste falha com AssertionError: esperado 5, recebeu 3"

---

## 📈 PROGRESSÃO DE APRENDIZADO (4 Semanas)

### Semana 1: Sobrevivência
**Objetivo:** Não quebrar nada, entender estrutura
- ✅ Navegar projeto
- ✅ Rodar testes básicos
- ✅ Fix commits pequenos
- ✅ Usar Copilot para dúvidas simples

### Semana 2: Contribuição
**Objetivo:** Fazer mudanças úteis
- ✅ Escrever testes simples
- ✅ Melhorar comentários/código
- ✅ Fix bugs óbvios
- ✅ Pequenos refactors

### Semana 3: Independência
**Objetivo:** Resolver problemas sozinho
- ✅ Implementar features pequenas
- ✅ Debug issues moderados
- ✅ Melhorar performance
- ✅ Contribuir documentação

### Semana 4: Maestria
**Objetivo:** Trabalhar como dev pleno
- ✅ Arquitetar soluções
- ✅ Code review de outros
- ✅ Otimizar sistemas complexos
- ✅ Liderar pequenas iniciativas

---

## 🚨 SITUAÇÕES DE EMERGÊNCIA

### Se Quebrar Algo
```bash
# Não entre em pânico!
git status                    # Ver mudanças
git diff                      # Ver o que mudou
git checkout -- arquivo.py    # Reverter arquivo
git reset --hard HEAD~1       # Reverter commit (cuidado!)
```

### Se Testes Falharem
```bash
# Investigar
python -m pytest tests/ -x --tb=long -v | head -50
# Pedir ajuda específica ao Copilot
```

### Se Não Entender Algo
1. Ler documentação relevante
2. Buscar no código: `grep -r "termo" .`
3. Perguntar ao Copilot com contexto
4. Não force - peça ajuda

---

## 🎯 MINDSET PARA INICIANTE

### Princípios
1. **Pequenas Vitórias Diárias** - Melhor 1 commit bom que 10 ruins
2. **Aprender Fazendo** - Código > Teoria
3. **Pedir Ajuda é OK** - Copilot é seu mentor
4. **Qualidade > Quantidade** - Código limpo é mais importante que features
5. **Persistência** - Erros são lições, não fracassos

### Hábitos Saudáveis
- **Commit Pequenos:** Muitas mudanças pequenas vs poucas grandes
- **Teste Sempre:** Rode testes antes/após mudanças
- **Documente:** Comente código e decisões
- **Pergunte:** Dúvidas são oportunidades de aprendizado
- **Revise:** Leia código próprio após escrever

### Quando Usar Copilot vs Tentar Sozinho
- **Copilot:** APIs desconhecidas, algoritmos complexos, debug difícil
- **Sozinho:** Lógica simples, refactors óbvios, testes básicos
- **Híbrido:** Pense primeiro, use Copilot para implementar

---

## 📊 METAS SEMANAIS REALISTAS

### Semana 1
- [ ] 5 commits pequenos
- [ ] 3 testes passando
- [ ] 2 dúvidas respondidas pelo Copilot
- [ ] Entender 50% da estrutura

### Semana 2
- [ ] 10 commits
- [ ] 5 testes novos
- [ ] 1 pequeno refactor
- [ ] 80% da estrutura entendida

### Semana 3
- [ ] 15 commits
- [ ] 8 testes novos
- [ ] 2 features pequenas
- [ ] 1 bug fix independente

### Semana 4
- [ ] 20+ commits
- [ ] 10+ testes
- [ ] 3+ features
- [ ] Contribuir documentação

---

## 🔗 RECURSOS DE APRENDIZADO

### Documentação Interna
- `docs/TECHNICAL_REPORT_OMNIMIND_DEVELOPMENT.md` - Visão geral completa
- `README.md` - Setup e uso básico
- `docs/INSTALLATION.md` - Instalação detalhada

### Ferramentas de Desenvolvimento
- **VS Code** - Editor recomendado
- **Git** - Controle de versão
- **pytest** - Testes
- **black/flake8** - Formatação/lint

### Canais de Ajuda
1. **Copilot/GitHub Copilot** - Mentor principal
2. **Documentação** - Sempre primeiro
3. **Código Existente** - Exemplos reais
4. **Testes** - Como usar features

---

**Lembre-se:** Todo expert foi iniciante um dia. Seja paciente consigo mesmo, celebre pequenas vitórias, e use Copilot como guia, não muleta. Você vai longe! 🚀