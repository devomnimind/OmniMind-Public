-- SQL para atualizar schema da tabela consciousness_snapshots no Supabase
-- Adiciona colunas psi_value e sigma_value para suportar a tríade completa de consciência

-- Verificar se as colunas já existem antes de adicionar
DO $$
BEGIN
    -- Adicionar coluna psi_value se não existir
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'consciousness_snapshots'
        AND column_name = 'psi_value'
    ) THEN
        ALTER TABLE consciousness_snapshots
        ADD COLUMN psi_value DOUBLE PRECISION DEFAULT 0.0;
    END IF;

    -- Adicionar coluna sigma_value se não existir
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'consciousness_snapshots'
        AND column_name = 'sigma_value'
    ) THEN
        ALTER TABLE consciousness_snapshots
        ADD COLUMN sigma_value DOUBLE PRECISION DEFAULT 0.0;
    END IF;
END $$;

-- Adicionar comentários nas colunas (fora do bloco DO)
COMMENT ON COLUMN consciousness_snapshots.psi_value IS
    'Ψ_produtor (Deleuze) - Produção criativa [0, 1]';

COMMENT ON COLUMN consciousness_snapshots.sigma_value IS
    'σ_sinthome (Lacan) - Coesão estrutural [0, 1]';

-- Verificar estrutura atual da tabela
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'consciousness_snapshots'
ORDER BY ordinal_position;

-- Opcional: Criar índices para queries por tríade
CREATE INDEX IF NOT EXISTS idx_consciousness_snapshots_triad
ON consciousness_snapshots(phi_value, psi_value, sigma_value);

CREATE INDEX IF NOT EXISTS idx_consciousness_snapshots_timestamp
ON consciousness_snapshots(timestamp);

-- Opcional: Criar view para análise da tríade
CREATE OR REPLACE VIEW consciousness_triad_stats AS
SELECT
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as snapshot_count,
    AVG(phi_value) as avg_phi,
    AVG(psi_value) as avg_psi,
    AVG(sigma_value) as avg_sigma,
    MAX(phi_value) as max_phi,
    MAX(psi_value) as max_psi,
    MAX(sigma_value) as max_sigma,
    MIN(phi_value) as min_phi,
    MIN(psi_value) as min_psi,
    MIN(sigma_value) as min_sigma
FROM consciousness_snapshots
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY date DESC;

COMMENT ON VIEW consciousness_triad_stats IS
'Estatísticas diárias da tríade de consciência (Φ, Ψ, σ)';

