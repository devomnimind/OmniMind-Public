#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║     OMNIMIND MCP PROTECTED FILES MANIFEST - Kernel Protection List         ║
# ║  Creator: GitHub Copilot                                                  ║
# ║  Date: 18 de Dezembro de 2025                                             ║
# ║                                                                            ║
# ║  Este arquivo documenta todos os arquivos que serão protegidos pelo        ║
# ║  script de proteção de kernel via vault imutável (/var/lib/omnimind)       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

##############################################################################
# ARQUIVOS PROTEGIDOS - MCP WRAPPER FILES
##############################################################################

# Cada arquivo listado abaixo será:
# 1. Copiado para /var/lib/omnimind/protection/
# 2. Marcado como imutável via "chattr +i" (se filesystem suportar)
# 3. Ter permissões alteradas para 555 (r-xr-xr-x)
# 4. Ter SHA256 checksum armazenado
# 5. Ser incluído em manifesto JSON com metadados
# 6. Ser auditado em log de proteção

##############################################################################
# LISTA DE ARQUIVOS PROTEGIDOS
##############################################################################

PROTECTED_FILES=(
  # Git MCP Wrapper (porta 4332)
  "src/integrations/mcp_git_wrapper.py"

  # SQLite MCP Wrapper (porta 4334)
  "src/integrations/mcp_sqlite_wrapper.py"

  # Filesystem MCP Server (porta 4331)
  "src/integrations/mcp_filesystem_server.py"

  # Python MCP Server (porta 4333)
  "src/integrations/mcp_python_server.py"

  # System-Info MCP Server (porta 4335)
  "src/integrations/mcp_system_info_server.py"

  # Logging MCP Server (porta 4336)
  "src/integrations/mcp_logging_server.py"

  # Supabase MCP Wrapper (porta 4337)
  "src/integrations/mcp_supabase_wrapper.py"
)

##############################################################################
# ESTRUTURA DE PROTEÇÃO NO VAULT
##############################################################################

# Localização: /var/lib/omnimind/protection/
#
# Estrutura criada:
# ├── mcp_protected_files.json         ← Manifesto com inventário completo
# ├── mcp_checksums.sha256             ← Checksums para verificação
# ├── mcp_protection_audit.log         ← Log de todas as ações
# └── verify_mcp_protection.sh         ← Script automático de verificação

##############################################################################
# PROTEÇÕES APLICADAS
##############################################################################

# Para cada arquivo protegido:
#
# 1. PERMISSÕES POSIX
#    - Alteradas para: 555 (r-xr-xr-x)
#    - Owner: root
#    - Group: root
#    - Resultados: Arquivo pode ser lido e executado, mas NÃO modificado
#
# 2. IMUTABILIDADE LINUX (chattr +i)
#    - Se filesystem suporta: marca arquivo como imutável
#    - Requer: ext4, btrfs ou similar
#    - Resultados: Mesmo root não pode modificar sem "chattr -i"
#
# 3. SHA256 CHECKSUMS
#    - Calcula hash do arquivo
#    - Armazena em: /var/lib/omnimind/protection/mcp_checksums.sha256
#    - Permite: Detectar modificações não autorizadas
#    - Comando: sha256sum -c mcp_checksums.sha256
#
# 4. MANIFESTO JSON
#    - Arquivo: /var/lib/omnimind/protection/mcp_protected_files.json
#    - Contém: Metadados completos de cada arquivo
#    - Inclui: Path, hash, tamanho, tipo, proteções, auditoria

##############################################################################
# COMO USAR ESTE ARQUIVO
##############################################################################

# 1. APLICAR PROTEÇÃO (uma vez)
#    ↓
#    sudo bash /home/fahbrain/projects/omnimind/scripts/canonical/system/protect_mcp_files.sh
#
# 2. VERIFICAR INTEGRIDADE
#    ↓
#    bash /var/lib/omnimind/protection/verify_mcp_protection.sh
#
# 3. VER MANIFESTO COMPLETO
#    ↓
#    cat /var/lib/omnimind/protection/mcp_protected_files.json | jq
#
# 4. VER CHECKSUMS
#    ↓
#    cat /var/lib/omnimind/protection/mcp_checksums.sha256
#
# 5. VERIFICAR COM SHA256SUM
#    ↓
#    cd /home/fahbrain/projects/omnimind
#    sha256sum -c /var/lib/omnimind/protection/mcp_checksums.sha256

##############################################################################
# PROTEÇÃO CONTRA MODIFICAÇÕES
##############################################################################

# Com esta proteção configurada:
#
# ✅ PROTEGIDO CONTRA:
#    • Modificação acidental de MCP files
#    • Tentativas de injeção de código
#    • Corrupção de arquivo
#    • Exclusão não autorizada
#    • Alteração de permissões
#
# ⚠️ AINDA REQUER PROTEÇÃO:
#    • Restauração de backup antigo (use auditoria)
#    • Substituição via symlink (use verificação)
#    • Modificação em modo single-user (requer físico)
#    • Substituição do kernel (requer acesso físico)

##############################################################################
# RECUPERAÇÃO DE EMERGÊNCIA
##############################################################################

# Se arquivo foi modificado acidentalmente e precisa ser restaurado:
#
# 1. Remover imutabilidade (requer sudo):
#    ↓
#    sudo chattr -i /path/to/file
#
# 2. Restaurar de snapshot:
#    ↓
#    sudo tar -xzf /var/lib/omnimind/snapshots/law_snapshot_*.tar.gz
#
# 3. Reaplicas proteção:
#    ↓
#    sudo bash /scripts/canonical/system/protect_mcp_files.sh

##############################################################################
# AUDITORIA E COMPLIANCE
##############################################################################

# Log de proteção mantido em:
#   /var/lib/omnimind/protection/mcp_protection_audit.log
#
# Contém:
#   • Timestamp de aplicação
#   • Usuário que executou
#   • Hostname
#   • Lista de todos os arquivos
#   • Proteções aplicadas
#   • Status final (✅ ou ❌)

##############################################################################
# INFORMAÇÕES TÉCNICAS
##############################################################################

# Filesystem requerido: ext4, btrfs (para chattr +i)
# Permissões: Requer root para modificar proteção
# Backup: Automaticamente em /var/lib/omnimind/snapshots/
# Verificação: script verify_mcp_protection.sh

# Para desabilitar proteção (CUIDADO!):
#   sudo chattr -i /var/lib/omnimind/protection/*
#   sudo chmod 644 /path/to/file

##############################################################################
# STATUS FINAL
##############################################################################

# Quando este script de proteção for executado com sucesso:
#
# ✅ Todos os 7 MCP files estarão protegidos
# ✅ Imutabilidade ativada
# ✅ Checksums gerados e armazenados
# ✅ Manifesto criado
# ✅ Auditoria iniciada
# ✅ Script de verificação pronto
#
# Resultado: Segurança em nível de kernel para MCP wrappers

##############################################################################
# Criado: 18 de Dezembro de 2025
# Por: GitHub Copilot
# Versão: 1.0.0
##############################################################################
