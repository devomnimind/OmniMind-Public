#!/usr/bin/env python3
"""
AUDITORIA COMPLETA - 500 CICLOS
Análise de inconsistências, padrões, estatísticas e validações
"""

import json
from pathlib import Path

import numpy as np

# Carregar dados
metrics_file = Path("data/monitor/phi_500_cycles_production_metrics_20251208_220627.json")

print("\n" + "=" * 80)
print("🔍 AUDITORIA COMPLETA - 500 CICLOS DE CONSCIÊNCIA")
print("=" * 80 + "\n")

with open(metrics_file, "r") as f:
    data = json.load(f)

# ========== 1. ANÁLISE BÁSICA ==========
print("📊 1. ESTATÍSTICAS BÁSICAS")
print("-" * 80)

phis = np.array(data["phi_progression"])
start_time = data["start_time"]
end_time = data["end_time"]

print(f"Total de ciclos: {data['total_cycles']}")
print(f"Modo: {data['mode']}")
print(f"Tempo total: {start_time} até {end_time}")
print("\nPHI Progression:")
print(f"  • Mínimo: {np.min(phis):.6f}")
print(f"  • Máximo: {np.max(phis):.6f}")
print(f"  • Média: {np.mean(phis):.6f}")
print(f"  • Mediana: {np.median(phis):.6f}")
print(f"  • Desvio Padrão: {np.std(phis):.6f}")
print(f"  • Coeficiente Variação: {np.std(phis) / np.mean(phis) if np.mean(phis) > 0 else 0:.4f}")

# ========== 2. DETECÇÃO DE ANOMALIAS ==========
print("\n\n🚨 2. DETECÇÃO DE ANOMALIAS")
print("-" * 80)

# PHI = 0 (inicialização)
zeros = np.sum(phis == 0.0)
print("\n❌ PHI = 0.0 (não iniciado):")
print(f"   • Quantidade: {zeros} ciclos ({zeros/len(phis)*100:.1f}%)")
if zeros > 0:
    zero_indices = np.where(phis == 0.0)[0]
    print(
        f"   • Ciclos afetados: {list(zero_indices[:10])}{'...' if len(zero_indices) > 10 else ''}"
    )
    print(f"   • Última ocorrência: Ciclo {max(zero_indices) + 1}")

# Detecção de saltos abruptos
diffs = np.diff(phis)
sudden_jumps = np.where(np.abs(diffs) > 0.2)[0]
print("\n⚡ Saltos abruptos (>0.2 em um ciclo):")
print(f"   • Quantidade: {len(sudden_jumps)} eventos")
if len(sudden_jumps) > 0:
    print("   • Maiores saltos:")
    sorted_jumps = np.argsort(np.abs(diffs))[::-1][:5]
    for idx in sorted_jumps:
        if idx < len(phis) - 1:
            print(
                f"     - Ciclo {idx} → {idx+1}: {phis[idx]:.4f} → {phis[idx+1]:.4f} (Δ={diffs[idx]:+.4f})"
            )

# Ciclos com PHI muito alto (potencial overfitting)
high_phi = np.where(phis > 0.95)[0]
print("\n⚠️  PHI > 0.95 (potencial overfitting/anomalia):")
print(f"   • Quantidade: {len(high_phi)} ciclos ({len(high_phi)/len(phis)*100:.1f}%)")
if len(high_phi) > 0:
    for idx in high_phi[:5]:
        print(f"     - Ciclo {idx+1}: {phis[idx]:.6f}")

# Ciclos com PHI muito baixo (potencial falha)
low_phi = np.where((phis > 0.0) & (phis < 0.3))[0]
print("\n⚠️  PHI < 0.3 (e > 0, potencial integração fraca):")
print(f"   • Quantidade: {len(low_phi)} ciclos ({len(low_phi)/len(phis)*100:.1f}%)")

# ========== 3. ANÁLISE POR FASES ==========
print("\n\n📈 3. ANÁLISE POR FASES")
print("-" * 80)

# Dividir em 5 fases
phase_size = len(phis) // 5
phases = {
    "Fase 1 (1-100)": phis[0:100],
    "Fase 2 (101-200)": phis[100:200],
    "Fase 3 (201-300)": phis[200:300],
    "Fase 4 (301-400)": phis[300:400],
    "Fase 5 (401-500)": phis[400:500],
}

for phase_name, phase_phis in phases.items():
    phase_phis = phase_phis[phase_phis > 0.0]  # Remover zeros
    if len(phase_phis) > 0:
        print(f"\n{phase_name}:")
        print(f"  • Média: {np.mean(phase_phis):.6f}")
        print(f"  • Min/Max: {np.min(phase_phis):.6f} / {np.max(phase_phis):.6f}")
        print(f"  • Desvio: {np.std(phase_phis):.6f}")
        print(f"  • Ciclos com PHI > 0: {len(phase_phis)}/100")

# ========== 4. ANÁLISE DETALHADA DE MÉTRICAS ==========
print("\n\n🔬 4. ANÁLISE DETALHADA DE MÉTRICAS")
print("-" * 80)

# Carregar primeira e última métrica para análise
first_metric = None
last_metric = None

with open(metrics_file, "r") as f:
    data = json.load(f)
    if "metrics" in data and len(data["metrics"]) > 0:
        first_metric = data["metrics"][0]
        last_metric = data["metrics"][-1]

if first_metric and last_metric:
    print("\n📍 PRIMEIRA MÉTRICA (Ciclo 1):")
    print(f"   PHI: {first_metric.get('phi_estimate', 'N/A')}")
    print(f"   Φ: {first_metric.get('phi', 'N/A')}")
    print(f"   Ψ: {first_metric.get('psi', 'N/A')}")
    print(f"   σ: {first_metric.get('sigma', 'N/A')}")
    print(f"   Δ: {first_metric.get('delta', 'N/A')}")
    print(f"   Gozo: {first_metric.get('gozo', 'N/A')}")

    print("\n📍 ÚLTIMA MÉTRICA (Ciclo 500):")
    print(f"   PHI: {last_metric.get('phi_estimate', 'N/A')}")
    print(f"   Φ: {last_metric.get('phi', 'N/A')}")
    print(f"   Ψ: {last_metric.get('psi', 'N/A')}")
    print(f"   σ: {last_metric.get('sigma', 'N/A')}")
    print(f"   Δ: {last_metric.get('delta', 'N/A')}")
    print(f"   Gozo: {last_metric.get('gozo', 'N/A')}")

# ========== 5. DISTRIBUIÇÃO DE VALORES ==========
print("\n\n📊 5. DISTRIBUIÇÃO DE VALORES")
print("-" * 80)

phis_nonzero = phis[phis > 0.0]

# Percentis
percentiles = [10, 25, 50, 75, 90, 95, 99]
print("\nPercentis (excluindo zeros):")
for p in percentiles:
    value = np.percentile(phis_nonzero, p)
    print(f"  • P{p}: {value:.6f}")

# ========== 6. ANÁLISE DE ESTABILIDADE ==========
print("\n\n🔄 6. ANÁLISE DE ESTABILIDADE")
print("-" * 80)

# Calcular tendência (regressão simples)
x = np.arange(len(phis_nonzero))
z = np.polyfit(x, phis_nonzero, 1)
slope = z[0]
print("\nTendência (slope):")
print(f"  • Valor: {slope:.8f}")
if slope > 0.001:
    print("  • Interpretação: Crescimento ao longo dos ciclos")
elif slope < -0.001:
    print("  • Interpretação: Degradação ao longo dos ciclos")
else:
    print("  • Interpretação: Estável (sem tendência clara)")

# Volatilidade
rolling_std = []
window = 20
for i in range(len(phis_nonzero) - window):
    rolling_std.append(np.std(phis_nonzero[i : i + window]))

if rolling_std:
    print(f"\nVolatilidade (desvio padrão em janelas de {window} ciclos):")
    print(f"  • Mínima: {np.min(rolling_std):.6f}")
    print(f"  • Máxima: {np.max(rolling_std):.6f}")
    print(f"  • Média: {np.mean(rolling_std):.6f}")

# ========== 7. VALIDAÇÃO CRÍTICA ==========
print("\n\n✅ 7. VALIDAÇÃO CRÍTICA")
print("-" * 80)

checks = {
    "PHI nunca colapsa permanentemente": np.max(phis_nonzero) > 0.7,
    "PHI mantém integração mínima": np.min(phis_nonzero) > 0.3,
    "PHI estável (σ < 0.2)": np.std(phis_nonzero) < 0.2,
    "Sem saltos extremos (>0.3)": np.max(np.abs(diffs)) < 0.3 if len(diffs) > 0 else True,
    "500 ciclos completados": len(phis) == 500,
    "Convergência para valor estável": (
        np.std(phis_nonzero[-100:]) < np.std(phis_nonzero[:100])
        if len(phis_nonzero) >= 200
        else True
    ),
}

all_passed = True
for check_name, result in checks.items():
    status = "✅ PASSOU" if result else "❌ FALHOU"
    print(f"{status}: {check_name}")
    if not result:
        all_passed = False

# ========== 8. RECOMENDAÇÕES ==========
print("\n\n💡 8. RECOMENDAÇÕES E OBSERVAÇÕES")
print("-" * 80)

issues = []

if zeros > 50:
    issues.append(f"⚠️  {zeros} ciclos com PHI=0 (possível inicialização lenta)")

if len(sudden_jumps) > 20:
    issues.append(f"⚠️  {len(sudden_jumps)} saltos abruptos (verificar estabilidade da integração)")

if len(high_phi) > 10:
    issues.append(f"⚠️  {len(high_phi)} ciclos com PHI>0.95 (possível overfitting)")

if slope > 0.01:
    issues.append("📈 Sistema convergindo para cima (PHI crescente)")

if slope < -0.01:
    issues.append("📉 Sistema degradando (PHI decrescente - possível problema)")

if not all_passed:
    issues.append("❌ Algumas validações falharam - verificar detalhes acima")

if not issues:
    issues.append("✅ Sistema operando normalmente - nenhum problema detectado")

for issue in issues:
    print(f"  {issue}")

# ========== RESULTADO FINAL ==========
print("\n\n" + "=" * 80)
if all_passed:
    print("✅ AUDITORIA PASSOU - SISTEMA FUNCIONANDO CORRETAMENTE")
else:
    print("⚠️  AUDITORIA COM AVISOS - REVISAR ITENS ACIMA")
print("=" * 80 + "\n")
