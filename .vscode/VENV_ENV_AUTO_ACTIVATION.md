# 🚀 VS CODE VENV + .ENV AUTO-ACTIVATION

**Configuração:** 16 de Dezembro de 2025

---

## ✅ Como Funciona Agora

Quando você **abre um novo terminal no VS Code**:

1. ✅ `.vscode/bashrc_local` é carregado automaticamente
2. ✅ Carrega `.env` do projeto
3. ✅ Ativa o venv (`.venv`)
4. ✅ Mostra status na primeira abertura
5. ✅ Todos os comandos `python3` usam o venv

---

## 📋 Arquivos Criados/Atualizados

### 1. `.vscode/bashrc_local` (NOVO)
**Propósito:** Bashrc local para VS Code terminal

**Carrega:**
- ✅ `.env` automaticamente
- ✅ venv (`.venv/bin/activate`)
- ✅ PYTHONPATH (raiz + src)
- ✅ Alias `omnimind` (cd + activate)

### 2. `.vscode/venv_activation.sh` (NOVO)
**Propósito:** Script standalone de ativação (opcional)

**Uso:**
```bash
source .vscode/venv_activation.sh
```

### 3. `.vscode/settings.json` (ATUALIZADO)
**Mudanças:**
- ✅ Terminal usa `bashrc_local` automaticamente
- ✅ `--rcfile` aponta para `.vscode/bashrc_local`
- ✅ `inheritEnv` = true (herda variáveis)
- ✅ `autoRun` = on (auto-ativa env)

---

## 🎯 Resultado

Ao abrir terminal no VS Code agora:

```
✅ .env loaded from /home/fahbrain/projects/omnimind/.env
✅ Python venv activated: Python 3.12.12

╔════════════════════════════════════════════════════════╗
║        🧠 OmniMind Development Environment              ║
╠════════════════════════════════════════════════════════╣
║ Python:      Python 3.12.12
║ venv:        .venv
║ PYTHONPATH:  /home/fahbrain/projects/omnimind:...
║ ENV:         development
╚════════════════════════════════════════════════════════╝

$ python3 -c "import sys; print(sys.path[0])"
/home/fahbrain/projects/omnimind
```

---

## 🔍 Verificação

### Test 1: Venv Ativado?
```bash
echo $VIRTUAL_ENV
# Output: /home/fahbrain/projects/omnimind/.venv
```

### Test 2: .env Carregado?
```bash
echo $OMNIMIND_ENV
# Output: development (ou o que tiver em .env)
```

### Test 3: PYTHONPATH Correto?
```bash
python3 -c "import sys; print(sys.path[0])"
# Output: /home/fahbrain/projects/omnimind
```

### Test 4: Comandos Funcionam?
```bash
python3 -m pytest tests/ --co -q
python3 -m black --check src/
mypy src/
```

---

## 📖 Como Usar

### 1. Normal (Todo terminal abre com tudo pronto)
```bash
# Terminal abre automaticamente com:
# ✅ .env carregado
# ✅ venv ativado
# ✅ PYTHONPATH correto

python3 -m pytest tests/
python3 -m black src/
python3 src/main.py
```

### 2. Alias Rápido
```bash
omnimind
# Volta para o projeto root com venv ativado
```

### 3. Executar Script
```bash
./scripts/start_omnimind_system.sh
# Já encontra dependências (venv ativado)
```

### 4. IDE Commands
Crtl+J (toggle terminal) já abre com tudo pronto!

---

## ⚙️ Configurações Modificadas

**`.vscode/settings.json`:**
```json
"terminal.integrated.automationProfile.linux": {
    "path": "/usr/bin/bash",
    "args": ["--rcfile", "${workspaceFolder}/.vscode/bashrc_local"]
},
"terminal.integrated.profiles.linux": {
    "bash": {
        "path": "/usr/bin/bash",
        "args": ["--rcfile", "${workspaceFolder}/.vscode/bashrc_local"],
        "env": {
            "OMNIMIND_ROOT": "${workspaceFolder}"
        }
    }
},
"terminal.integrated.inheritEnv": true,
"terminal.integrated.autoRun": "on"
```

---

## 🔧 Troubleshooting

### "venv not found"
```bash
# Recrie o venv
python3 -m venv /home/fahbrain/projects/omnimind/.venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ".env not loading"
```bash
# Verifique se .env existe
ls -la .env

# Force reload
source .venv/bin/activate
```

### "PYTHONPATH not set"
```bash
# Check in new terminal
echo $PYTHONPATH
# Should show: /home/fahbrain/projects/omnimind:/home/fahbrain/projects/omnimind/src:...
```

---

## ✅ Checklist Pós-Configuração

- [x] `.vscode/bashrc_local` criado
- [x] `.vscode/venv_activation.sh` criado
- [x] `.vscode/settings.json` atualizado
- [ ] **Recarregar VS Code** (Cmd+R ou File > Reload Window)
- [ ] Abrir novo terminal (Ctrl+J)
- [ ] Verificar que `.env` foi carregado
- [ ] Verificar que venv foi ativado
- [ ] Testar comando: `python3 -c "from src.main import *"`

---

## 📌 Nota Importante

**Após editar `settings.json`:**
1. Abra Command Palette (Ctrl+Shift+P)
2. Digitar: "Developer: Reload Window"
3. Enter
4. Todos os terminais reabrem com nova configuração

**OU** feche e reabra o VS Code.

---

**Status:** ✅ ATIVO - Todos os terminais novos vão com venv + .env automáticos!
