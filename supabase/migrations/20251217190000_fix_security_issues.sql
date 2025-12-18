-- Fix security issues for autopoietic_logs and consciousness_triad_stats
-- Migration: 20251217190000_fix_security_issues.sql
-- Corrected version with guarded policy creation

-- 1. Replace consciousness_triad_stats view with SECURITY INVOKER function
DROP VIEW IF EXISTS consciousness_triad_stats;

CREATE OR REPLACE FUNCTION get_consciousness_triad_stats()
RETURNS TABLE (
    date date,
    snapshot_count bigint,
    avg_phi double precision,
    avg_psi double precision,
    avg_sigma double precision,
    max_phi double precision,
    max_psi double precision,
    max_sigma double precision,
    min_phi double precision,
    min_psi double precision,
    min_sigma double precision
) SECURITY INVOKER
AS $$
SELECT
    DATE_TRUNC('day', timestamp)::date as date,
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
$$ LANGUAGE sql;

COMMENT ON FUNCTION get_consciousness_triad_stats() IS
'Função SECURITY INVOKER para estatísticas diárias da tríade de consciência (Φ, Ψ, σ)';

-- 2. Enable RLS and create policies for autopoietic_logs (guarded)
ALTER TABLE IF EXISTS autopoietic_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if present, then create
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'autopoietic_logs' AND policyname = 'Allow authenticated users to read autopoietic_logs'
  ) THEN
    EXECUTE format('DROP POLICY %I ON public.autopoietic_logs;', 'Allow authenticated users to read autopoietic_logs');
  END IF;
END $$;

CREATE POLICY "Allow authenticated users to read autopoietic_logs" ON public.autopoietic_logs
  FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- Insert policy (service role) — drop if exists then create
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'autopoietic_logs' AND policyname = 'Allow service role to insert autopoietic_logs'
  ) THEN
    EXECUTE format('DROP POLICY %I ON public.autopoietic_logs;', 'Allow service role to insert autopoietic_logs');
  END IF;
END $$;

CREATE POLICY "Allow service role to insert autopoietic_logs" ON public.autopoietic_logs
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'autopoietic_logs' AND policyname = 'Allow service role to update autopoietic_logs'
  ) THEN
    EXECUTE format('DROP POLICY %I ON public.autopoietic_logs;', 'Allow service role to update autopoietic_logs');
  END IF;
END $$;

CREATE POLICY "Allow service role to update autopoietic_logs" ON public.autopoietic_logs
  FOR UPDATE
  USING (auth.role() = 'service_role');

-- 3. Ensure consciousness_snapshots has RLS and policies (guarded)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'consciousness_snapshots'
      AND n.nspname = 'public'
      AND c.relrowsecurity = true
  ) THEN
    ALTER TABLE public.consciousness_snapshots ENABLE ROW LEVEL SECURITY;
  END IF;

  -- Create policies only if missing
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'consciousness_snapshots'
      AND policyname = 'Allow authenticated users to read consciousness_snapshots'
  ) THEN
    CREATE POLICY "Allow authenticated users to read consciousness_snapshots" ON public.consciousness_snapshots
      FOR SELECT USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'consciousness_snapshots'
      AND policyname = 'Allow service role to insert consciousness_snapshots'
  ) THEN
    CREATE POLICY "Allow service role to insert consciousness_snapshots" ON public.consciousness_snapshots
      FOR INSERT WITH CHECK (auth.role() = 'service_role');
  END IF;
END $$;
