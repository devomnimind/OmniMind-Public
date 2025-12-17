-- SQL para corrigir consistência da tabela consciousness_snapshots
-- Garante que phi_value também tenha default e que todas as colunas da tríade sejam consistentes

-- Adicionar default para phi_value se não tiver (para consistência com psi_value e sigma_value)
DO $$
BEGIN
    -- Verificar se phi_value não tem default
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'consciousness_snapshots'
        AND column_name = 'phi_value'
        AND column_default IS NULL
    ) THEN
        ALTER TABLE consciousness_snapshots
        ALTER COLUMN phi_value SET DEFAULT 0.0;
    END IF;

    -- Garantir que psi_value e sigma_value sejam NOT NULL (consistência com phi_value)
    -- Mas só se não houver dados NULL existentes
    IF NOT EXISTS (
        SELECT 1
        FROM consciousness_snapshots
        WHERE psi_value IS NULL OR sigma_value IS NULL
    ) THEN
        -- Tornar NOT NULL apenas se não houver valores NULL
        ALTER TABLE consciousness_snapshots
        ALTER COLUMN psi_value SET NOT NULL;

        ALTER TABLE consciousness_snapshots
        ALTER COLUMN sigma_value SET NOT NULL;
    END IF;
END $$;

-- Verificar estrutura final
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'consciousness_snapshots'
    AND column_name IN ('phi_value', 'psi_value', 'sigma_value')
ORDER BY column_name;

