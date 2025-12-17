# Comandos para mover arquivos do backup local para HD externo
# Execute estes comandos quando o HD externo estiver montado

# 1. Criar diretório no HD externo
mkdir -p /run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_archives

# 2. Mover todos os arquivos do backup local para o HD externo
mv docs/archive_local_backup/* /run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_archives/

# 3. Verificar se os arquivos foram movidos
ls -la /run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_archives/

# 4. Remover a pasta de backup local (opcional, após confirmação)
rmdir docs/archive_local_backup
