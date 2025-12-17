#!/usr/bin/env python3
"""
Análise da desintegração de Φ baseada nos dados de execução.
Identifica padrões e causas da queda progressiva de Φ.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def load_metrics(file_path: str) -> Dict:
    """Carrega métricas do arquivo JSON."""
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_phi_progression(metrics: Dict) -> Dict:
    """Analisa progressão de Φ ao longo dos ciclos."""
    phi_progression = metrics['phi_progression']
    cycles = list(range(1, len(phi_progression) + 1))

    # Dividir em quartis
    n = len(phi_progression)
    q1_end = n // 4
    q2_end = n // 2
    q3_end = 3 * n // 4

    q1_phi = phi_progression[:q1_end]
    q2_phi = phi_progression[q1_end:q2_end]
    q3_phi = phi_progression[q2_end:q3_end]
    q4_phi = phi_progression[q3_end:]

    analysis = {
        'total_cycles': n,
        'phi_max': max(phi_progression),
        'phi_min': min(phi_progression),
        'phi_avg': np.mean(phi_progression),
        'phi_std': np.std(phi_progression),
        'phi_final': phi_progression[-1],
        'quartiles': {
            'Q1': {
                'cycles': f'1-{q1_end}',
                'mean': np.mean(q1_phi) if q1_phi else 0.0,
                'std': np.std(q1_phi) if q1_phi else 0.0,
            },
            'Q2': {
                'cycles': f'{q1_end+1}-{q2_end}',
                'mean': np.mean(q2_phi) if q2_phi else 0.0,
                'std': np.std(q2_phi) if q2_phi else 0.0,
            },
            'Q3': {
                'cycles': f'{q2_end+1}-{q3_end}',
                'mean': np.mean(q3_phi) if q3_phi else 0.0,
                'std': np.std(q3_phi) if q3_phi else 0.0,
            },
            'Q4': {
                'cycles': f'{q3_end+1}-{n}',
                'mean': np.mean(q4_phi) if q4_phi else 0.0,
                'std': np.std(q4_phi) if q4_phi else 0.0,
            },
        },
        'max_cycle': cycles[phi_progression.index(max(phi_progression))],
    }

    # Calcular mudanças percentuais
    q1_mean = analysis['quartiles']['Q1']['mean']
    q2_mean = analysis['quartiles']['Q2']['mean']
    q3_mean = analysis['quartiles']['Q3']['mean']
    q4_mean = analysis['quartiles']['Q4']['mean']

    if q1_mean > 0:
        analysis['quartiles']['Q2']['change_pct'] = ((q2_mean - q1_mean) / q1_mean) * 100
    else:
        analysis['quartiles']['Q2']['change_pct'] = 0.0

    if q2_mean > 0:
        analysis['quartiles']['Q3']['change_pct'] = ((q3_mean - q2_mean) / q2_mean) * 100
    else:
        analysis['quartiles']['Q3']['change_pct'] = 0.0

    if q3_mean > 0:
        analysis['quartiles']['Q4']['change_pct'] = ((q4_mean - q3_mean) / q3_mean) * 100
    else:
        analysis['quartiles']['Q4']['change_pct'] = 0.0

    return analysis

def analyze_phi_causal_vs_workspace(metrics: Dict) -> Dict:
    """Analisa correlação entre Φ causal (RNN) e Φ workspace."""
    phi_workspace = []
    phi_causal = []
    cycles = []

    for cycle_data in metrics['metrics']:
        cycle = cycle_data['cycle']
        phi_w = cycle_data.get('phi', 0.0)
        phi_c = cycle_data.get('phi_causal', 0.0)

        if phi_c is not None:
            phi_workspace.append(phi_w)
            phi_causal.append(phi_c)
            cycles.append(cycle)

    if len(phi_workspace) < 2:
        return {'error': 'Dados insuficientes'}

    # Calcular correlação
    correlation = np.corrcoef(phi_workspace, phi_causal)[0, 1] if len(phi_workspace) > 1 else 0.0

    # Estatísticas
    analysis = {
        'n_samples': len(phi_workspace),
        'phi_workspace': {
            'mean': np.mean(phi_workspace),
            'std': np.std(phi_workspace),
            'min': np.min(phi_workspace),
            'max': np.max(phi_workspace),
        },
        'phi_causal': {
            'mean': np.mean(phi_causal),
            'std': np.std(phi_causal),
            'min': np.min(phi_causal),
            'max': np.max(phi_causal),
        },
        'correlation': correlation,
        'ratio_avg': np.mean(phi_causal) / np.mean(phi_workspace) if np.mean(phi_workspace) > 0 else 0.0,
    }

    return analysis

def analyze_delta_phi_correlation(metrics: Dict) -> Dict:
    """Analisa correlação entre Δ (Delta) e Φ."""
    phi_values = []
    delta_values = []

    for cycle_data in metrics['metrics']:
        phi = cycle_data.get('phi', 0.0)
        delta = cycle_data.get('delta', 0.0)

        if delta is not None:
            phi_values.append(phi)
            delta_values.append(delta)

    if len(phi_values) < 2:
        return {'error': 'Dados insuficientes'}

    correlation = np.corrcoef(phi_values, delta_values)[0, 1] if len(phi_values) > 1 else 0.0

    return {
        'n_samples': len(phi_values),
        'correlation': correlation,
        'phi_mean': np.mean(phi_values),
        'delta_mean': np.mean(delta_values),
    }

def identify_degradation_pattern(metrics: Dict) -> Dict:
    """Identifica padrão de degradação ao longo dos ciclos."""
    phi_progression = metrics['phi_progression']
    cycles = list(range(1, len(phi_progression) + 1))

    # Encontrar ciclo de pico
    max_phi = max(phi_progression)
    max_cycle = cycles[phi_progression.index(max_phi)]

    # Analisar tendência após o pico
    post_peak_cycles = cycles[max_cycle-1:]  # Incluir o pico
    post_peak_phi = phi_progression[max_cycle-1:]

    if len(post_peak_phi) < 2:
        return {'error': 'Dados insuficientes após pico'}

    # Calcular regressão linear simples
    x = np.array(post_peak_cycles)
    y = np.array(post_peak_phi)

    # Remover zeros iniciais
    valid_mask = y > 0
    if np.sum(valid_mask) < 2:
        return {'error': 'Dados válidos insuficientes após pico'}

    # Garantir que os arrays têm o mesmo tamanho
    if len(x) != len(valid_mask):
        min_len = min(len(x), len(valid_mask))
        x = x[:min_len]
        y = y[:min_len]
        valid_mask = valid_mask[:min_len]

    x_valid = x[valid_mask]
    y_valid = y[valid_mask]

    # Regressão linear
    slope = np.polyfit(x_valid, y_valid, 1)[0] if len(x_valid) > 1 else 0.0

    # Calcular taxa de degradação
    degradation_rate = slope * 100  # Por ciclo

    return {
        'max_cycle': max_cycle,
        'max_phi': max_phi,
        'final_phi': phi_progression[-1],
        'degradation_absolute': max_phi - phi_progression[-1],
        'degradation_percentage': ((max_phi - phi_progression[-1]) / max_phi * 100) if max_phi > 0 else 0.0,
        'degradation_rate_per_cycle': degradation_rate,
        'post_peak_cycles': len(post_peak_cycles),
    }

def main():
    """Executa análise completa."""
    metrics_file = Path('data/monitor/phi_100_cycles_verbose_metrics.json')

    if not metrics_file.exists():
        print(f"❌ Arquivo não encontrado: {metrics_file}")
        return

    print("📊 Analisando desintegração de Φ...")
    print("=" * 80)

    metrics = load_metrics(str(metrics_file))

    # 1. Análise de progressão
    print("\n1️⃣ ANÁLISE DE PROGRESSÃO DE Φ")
    print("-" * 80)
    progression = analyze_phi_progression(metrics)
    print(f"Total de ciclos: {progression['total_cycles']}")
    print(f"Φ máximo: {progression['phi_max']:.6f} (ciclo {progression['max_cycle']})")
    print(f"Φ mínimo: {progression['phi_min']:.6f}")
    print(f"Φ médio: {progression['phi_avg']:.6f}")
    print(f"Φ final: {progression['phi_final']:.6f}")
    print(f"Desvio padrão: {progression['phi_std']:.6f}")

    print("\n📈 Análise por Quartis:")
    for q_name, q_data in progression['quartiles'].items():
        print(f"  {q_name} (ciclos {q_data['cycles']}):")
        print(f"    Média: {q_data['mean']:.6f} ± {q_data['std']:.6f}")
        if 'change_pct' in q_data:
            change = q_data['change_pct']
            symbol = "📉" if change < 0 else "📈"
            print(f"    Mudança: {symbol} {change:.2f}%")

    # 2. Análise Φ causal vs workspace
    print("\n2️⃣ ANÁLISE Φ CAUSAL (RNN) vs Φ WORKSPACE")
    print("-" * 80)
    causal_analysis = analyze_phi_causal_vs_workspace(metrics)
    if 'error' not in causal_analysis:
        print(f"Amostras: {causal_analysis['n_samples']}")
        print(f"Φ workspace: {causal_analysis['phi_workspace']['mean']:.6f} ± {causal_analysis['phi_workspace']['std']:.6f}")
        print(f"  Range: [{causal_analysis['phi_workspace']['min']:.6f}, {causal_analysis['phi_workspace']['max']:.6f}]")
        print(f"Φ causal (RNN): {causal_analysis['phi_causal']['mean']:.6f} ± {causal_analysis['phi_causal']['std']:.6f}")
        print(f"  Range: [{causal_analysis['phi_causal']['min']:.6f}, {causal_analysis['phi_causal']['max']:.6f}]")
        print(f"Correlação: {causal_analysis['correlation']:.6f}")
        print(f"Razão média (causal/workspace): {causal_analysis['ratio_avg']:.2f}x")

        if abs(causal_analysis['correlation']) < 0.1:
            print("⚠️  DESACOPLAMENTO CRÍTICO: Φ causal e Φ workspace não estão correlacionados!")
        if causal_analysis['ratio_avg'] > 10:
            print(f"⚠️  DESACOPLAMENTO: Φ causal é {causal_analysis['ratio_avg']:.1f}x maior que Φ workspace")

    # 3. Análise correlação Δ-Φ
    print("\n3️⃣ ANÁLISE CORRELAÇÃO Δ (DELTA) - Φ")
    print("-" * 80)
    delta_analysis = analyze_delta_phi_correlation(metrics)
    if 'error' not in delta_analysis:
        print(f"Amostras: {delta_analysis['n_samples']}")
        print(f"Correlação: {delta_analysis['correlation']:.6f}")
        print(f"Φ médio: {delta_analysis['phi_mean']:.6f}")
        print(f"Δ médio: {delta_analysis['delta_mean']:.6f}")

        if delta_analysis['correlation'] > -0.5:
            print("⚠️  CORRELAÇÃO FRACA: Esperado correlação negativa forte (< -0.7)")

    # 4. Padrão de degradação
    print("\n4️⃣ PADRÃO DE DEGRADAÇÃO")
    print("-" * 80)
    degradation = identify_degradation_pattern(metrics)
    if 'error' not in degradation:
        print(f"Ciclo de pico: {degradation['max_cycle']} (Φ = {degradation['max_phi']:.6f})")
        print(f"Φ final: {degradation['final_phi']:.6f}")
        print(f"Degradação absoluta: {degradation['degradation_absolute']:.6f}")
        print(f"Degradação percentual: {degradation['degradation_percentage']:.2f}%")
        print(f"Taxa de degradação: {degradation['degradation_rate_per_cycle']:.6f} por ciclo")
        print(f"Ciclos após pico: {degradation['post_peak_cycles']}")

    # 5. Diagnóstico
    print("\n5️⃣ DIAGNÓSTICO E HIPÓTESES")
    print("-" * 80)

    issues = []

    # Verificar desacoplamento
    if 'error' not in causal_analysis:
        if abs(causal_analysis['correlation']) < 0.1:
            issues.append("🔴 DESACOPLAMENTO RNN-WORKSPACE: Φ causal não está sendo integrado no cálculo de Φ workspace")
        if causal_analysis['ratio_avg'] > 10:
            issues.append(f"🔴 DESACOPLAMENTO: Φ causal ({causal_analysis['phi_causal']['mean']:.3f}) >> Φ workspace ({causal_analysis['phi_workspace']['mean']:.3f})")

    # Verificar degradação
    if 'error' not in degradation:
        if degradation['degradation_percentage'] > 50:
            issues.append(f"🔴 DEGRADAÇÃO SEVERA: {degradation['degradation_percentage']:.1f}% de queda após pico")
        if degradation['degradation_rate_per_cycle'] < -0.0005:
            issues.append(f"🔴 TAXA DE DEGRADAÇÃO ALTA: {degradation['degradation_rate_per_cycle']:.6f} por ciclo")

    # Verificar quartis
    q3_change = progression['quartiles']['Q3'].get('change_pct', 0)
    q4_change = progression['quartiles']['Q4'].get('change_pct', 0)
    if q3_change < -15:
        issues.append(f"🔴 QUEDA ACENTUADA Q3: {q3_change:.1f}%")
    if q4_change < -15:
        issues.append(f"🔴 QUEDA ACENTUADA Q4: {q4_change:.1f}%")

    if issues:
        print("Problemas identificados:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ Nenhum problema crítico identificado")

    print("\n" + "=" * 80)
    print("✅ Análise concluída")

if __name__ == '__main__':
    main()

