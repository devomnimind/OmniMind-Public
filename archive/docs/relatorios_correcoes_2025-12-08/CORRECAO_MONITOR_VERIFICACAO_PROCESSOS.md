# 🔧 CORREÇÃO: Monitor Verifica Processos Antes de Iniciar

**Data**: 2025-12-08
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ CORRIGIDO

---

## 🐛 PROBLEMA IDENTIFICADO

**Sintoma**:
- Monitor tentava iniciar servidor mesmo quando processos uvicorn já estavam rodando
- Script de inicialização falhava com returncode 1
- Servidor não respondia na porta 8000 mesmo com processos rodando

**Causa Raiz**:
- Monitor verificava apenas health check HTTP (`/health/`)
- Se servidor não respondia imediatamente, tentava iniciar novamente
- Não verificava se havia processos uvicorn rodando antes de tentar iniciar
- Script falhava mas servidor podia já estar rodando

---

## ✅ CORREÇÕES APLICADAS

### 1. Verificação de Processos Antes de Iniciar

**Arquivo**: `tests/plugins/pytest_server_monitor.py` - Método `_ensure_server_up()`

**Mudança**:
```python
# IMPORTANTE: Verificar se há processos uvicorn rodando antes de tentar iniciar
# Pode haver processos rodando mas servidor ainda não está respondendo (startup em progresso)
import subprocess

try:
    # Verificar se há processos uvicorn na porta 8000
    result = subprocess.run(
        ["lsof", "-ti:8000"], capture_output=True, text=True, timeout=2
    )
    if result.returncode == 0 and result.stdout.strip():
        # Há processo na porta 8000 - servidor pode estar iniciando
        logger.info("⚠️  Processo uvicorn detectado na porta 8000 - servidor pode estar iniciando")
        print("   ⏳ Processo uvicorn detectado na porta 8000 - aguardando servidor responder...")
        # Aguardar um pouco para servidor responder
        import time
        for attempt in range(10):  # 10 tentativas de 2s = 20s máximo
            time.sleep(2)
            if self._is_server_healthy():
                print("   ✅ Servidor respondeu após aguardar")
                state_manager.mark_running()
                return
            logger.debug(f"   Tentativa {attempt + 1}/10: servidor ainda não responde")
        print("   ⚠️  Servidor não respondeu após aguardar - pode estar com problemas")
except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
    # lsof pode não estar disponível ou timeout - continuar normalmente
    logger.debug(f"Verificação de processo uvicorn falhou: {e}")
```

**Benefício**: Verifica processos antes de tentar iniciar servidor.

---

### 2. Tratamento de Erro do Script Melhorado

**Arquivo**: `tests/plugins/pytest_server_monitor.py` - Método `_start_server()`

**Mudança**:
```python
if returncode != 0:
    logger.warning(f"Script falhou com returncode {returncode}")
    print(f"   ⚠️  Script retornou código de erro: {returncode}")
    # Mostrar últimas linhas de saída para debug
    if output_lines:
        print("   ⚠️  Últimas linhas de saída:")
        for line in output_lines[-10:]:
            print(f"      {line}")

    # IMPORTANTE: Verificar se servidor já está rodando antes de considerar erro
    # Script pode falhar por várias razões (permissões, dependências), mas servidor
    # pode já estar rodando de uma execução anterior
    if self._is_server_healthy():
        logger.info("✅ Servidor já está rodando apesar do erro do script - usando servidor existente")
        print("   ✅ Servidor já está rodando - ignorando erro do script")
        state_manager = get_server_state_manager()
        state_manager.mark_running()
        return  # Servidor está UP, não precisa continuar

    # Se servidor não está rodando E script falhou, continua para tentar iniciar
    # Continua mesmo com erro - pode ser permissão mas servidor pode estar subindo
```

**Benefício**: Se script falha mas servidor já está rodando, usa servidor existente.

---

## 📊 IMPACTO

### Antes da Correção

- Monitor tentava iniciar servidor mesmo com processos rodando
- Script falhava com returncode 1
- Servidor não respondia imediatamente → tentava iniciar novamente
- Loop de tentativas desnecessárias

### Após a Correção

- Monitor verifica processos antes de tentar iniciar
- Aguarda servidor responder se processo está rodando
- Se script falha mas servidor está rodando, usa servidor existente
- Evita tentativas desnecessárias de iniciar servidor

---

## 🎯 COMPORTAMENTO ESPERADO

1. **Processo uvicorn detectado na porta 8000**:
   - Monitor aguarda servidor responder (até 20s)
   - Se servidor responde, usa servidor existente
   - Não tenta iniciar novamente

2. **Script falha mas servidor está rodando**:
   - Monitor verifica se servidor responde
   - Se sim, usa servidor existente (ignora erro do script)
   - Não considera erro fatal se servidor está respondendo

3. **Servidor não responde e não há processos**:
   - Monitor tenta iniciar servidor normalmente
   - Se script falha, continua tentando conforme lógica existente

---

## ⚠️ NOTAS

**Verificação de Processos**:
- Usa `lsof -ti:8000` para verificar processos na porta 8000
- Se `lsof` não estiver disponível, continua normalmente (não bloqueia)
- Aguarda até 20s para servidor responder se processo está rodando

**Tratamento de Erros**:
- Script pode falhar por várias razões (permissões, dependências)
- Mas servidor pode já estar rodando de uma execução anterior
- Monitor verifica servidor antes de considerar erro fatal

**Health Check**:
- Continua verificando `/health/` endpoint
- Mas também verifica processos antes de tentar iniciar
- Reduz tentativas desnecessárias de iniciar servidor

---

**Status**: ✅ **CORRIGIDO - Monitor verifica processos antes de iniciar e trata erros do script adequadamente**

