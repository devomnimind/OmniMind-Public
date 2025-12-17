#!/bin/bash
set -e

echo "🚀 === Iniciando backup de dados em nuvem ===" 

# Timestamp para backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/omnimind_cloud_backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📦 1. Exportando Qdrant..."
docker exec qdrant qdrant-cli backup list \
  || echo "⚠️  Qdrant snapshots não disponíveis via CLI"

echo "📊 2. Exportando PostgreSQL..."
sudo -u postgres pg_dump -F c > "$BACKUP_DIR/omnimind_postgres_$TIMESTAMP.dump" \
  && echo "✅ PostgreSQL exportado: $(du -h $BACKUP_DIR/omnimind_postgres_$TIMESTAMP.dump | cut -f1)"

echo "💾 3. Exportando Redis..."
redis-cli BGSAVE \
  && redis-cli LASTSAVE \
  && cp /var/lib/redis/dump.rdb "$BACKUP_DIR/omnimind_redis_$TIMESTAMP.rdb" \
  && echo "✅ Redis backup criado: $(du -h $BACKUP_DIR/omnimind_redis_$TIMESTAMP.rdb | cut -f1)"

echo "📁 4. Copiando Qdrant snapshots..."
cp -r /home/fahbrain/projects/omnimind/deploy/data/qdrant_backup* "$BACKUP_DIR/" 2>/dev/null \
  && echo "✅ Snapshots copiados"

echo ""
echo "📤 === OPÇÕES PARA SINCRONIZAÇÃO EM NUVEM ==="
echo ""
echo "1️⃣  SUPABASE (Recomendado para PostgreSQL):"
echo "   export SUPABASE_URL='https://xxxxx.supabase.co'"
echo "   export SUPABASE_KEY='eyJxxx...'"
echo "   # Você pode usar: psql postgresql://postgres.xxxxx:password@db.xxxxx.supabase.co:5432/postgres"
echo ""
echo "2️⃣  AWS S3 (Para dados vetorizados):"
echo "   aws s3 cp $BACKUP_DIR s3://seu-bucket/omnimind-backups/$TIMESTAMP/ --recursive"
echo ""
echo "3️⃣  Google Cloud Storage:"
echo "   gsutil -m cp -r $BACKUP_DIR gs://seu-bucket/omnimind-backups/$TIMESTAMP/"
echo ""
echo "4️⃣  Azure Blob Storage:"
echo "   az storage blob upload-batch -d container -s $BACKUP_DIR --account-name account"
echo ""
echo "5️⃣  Qdrant Cloud (para embeddings):"
echo "   # Via interface web: https://cloud.qdrant.io/"
echo ""

echo ""
echo "✅ Arquivos de backup prontos em: $BACKUP_DIR"
echo "📊 Tamanho total: $(du -sh $BACKUP_DIR | cut -f1)"
echo ""
echo "⚠️  IMPORTANTE: Configure as variáveis de ambiente para sincronização:"
echo "   - SUPABASE_URL e SUPABASE_KEY para PostgreSQL"
echo "   - AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY para S3"
echo "   - Ou use sua plataforma de nuvem preferida"

