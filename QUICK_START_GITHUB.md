# 🚀 REFERÊNCIA RÁPIDA: Publicar OmniMind

**Organização:** devomnimind
**Repositório:** OmniMind-Public
**Data:** 17 de Dezembro de 2025

---

## ✨ Comando Único (Recomendado)

```bash
cd /home/fahbrain/projects/omnimind
./scripts/canonical/github/prepare_and_publish.sh
```

Isso faz TUDO automaticamente:
- ✅ Cria repositório público limpo
- ✅ Copia só código + testes + docs técnicas
- ✅ Valida sintaxe Python
- ✅ Faz commit inicial
- ✅ Mostra instruções para push

---

## 📋 Instruções Passo a Passo

### 1. Executar script de preparação
```bash
./scripts/canonical/github/prepare_and_publish.sh /tmp/omnimind-public
```

Resultado: Repositório Git limpo em `/tmp/omnimind-public`

### 2. Entrar no diretório gerado
```bash
cd /tmp/omnimind-public
```

### 3. Verificar tamanho
```bash
du -sh .
# Esperado: ~500MB (não os 35GB do privado)
```

### 4. Criar repositório no GitHub

1. Abrir: https://github.com/devomnimind
2. Novo repositório (+)
3. Nome: `OmniMind-Public`
4. Descrição: "OmniMind Public Repository - Consciousness Framework"
5. **Public** ✅
6. Sem README/License/gitignore (usaremos nossos)
7. Create

### 5. Fazer push

```bash
cd /tmp/omnimind-public

# Configurar remote
git remote add origin https://github.com/devomnimind/OmniMind-Public.git

# Fazer push
git push -u origin main
```

---

## 🔍 Verificações de Segurança

Antes de fazer push, rodar:

```bash
# 1. Verificar credenciais
grep -r "password\|token\|secret\|api_key" . 2>/dev/null | head

# 2. Verificar dados privados
grep -r "fahbrain\|/home/\|127.0.0.1:600" . 2>/dev/null | head

# 3. Verificar tamanho
du -sh .

# 4. Verificar imports principais
python3 -c "from src.consciousness.topological_phi import PhiCalculator; print('✅')"
python3 -c "from src.quantum_consciousness.qaoa_gpu_optimizer import get_qaoa_optimizer; print('✅')"
python3 -c "from src.services.service_update_api import router; print('✅')"
```

---

## 📁 Estrutura do Repositório Público

```
OmniMind-Public/
├── src/                    # Código principal
├── tests/                  # Suite de testes
├── scripts/                # Scripts canônicos
├── docs/technical/         # Documentação técnica
├── config/                 # Configurações
├── requirements/           # Dependências
├── README.md              # Documentação
├── LICENSE                # Licença
├── CITATION.cff           # Citação
└── pyproject.toml         # Config Python
```

---

## 🔗 Links Importantes

- **Organização:** https://github.com/devomnimind/
- **Repositório Novo:** https://github.com/devomnimind/OmniMind-Public
- **Repositório Privado:** /home/fahbrain/projects/omnimind (arquivo)
- **Guia Completo:** `./GUIA_PUBLICAR_GITHUB.md`

---

## ⏱️ Tempo Estimado

- Preparação: 2 minutos
- Validação: 1 minuto
- Push: 5-10 minutos (depende da conexão)
- **Total: ~15-20 minutos**

---

## ❓ FAQ

**P: Posso executar novamente?**
R: Sim! Cada execução cria um novo diretório com timestamp.

**P: E a documentação de pesquisa?**
R: Fica no repositório privado. O público tem só documentação técnica.

**P: Posso fazer push para outro repositório?**
R: Sim! Mude a URL:
```bash
git remote set-url origin https://github.com/seu-usuario/seu-repo.git
```

**P: Preciso do histórico git completo?**
R: Não, o script cria um histórico limpo com 1 commit.

---

## 🎯 Próximas Ações

- [ ] Executar `./scripts/canonical/github/prepare_and_publish.sh`
- [ ] Criar repositório em github.com/devomnimind
- [ ] Fazer push (git push -u origin main)
- [ ] Configurar branch protection
- [ ] Adicionar tópicos (consciousness, ai, framework)
- [ ] Publicar Release 1.0
- [ ] Configurar GitHub Actions

---

**Status:** ✅ Pronto para publicação
**Versão:** 1.0
**Última atualização:** 17 de Dezembro de 2025
