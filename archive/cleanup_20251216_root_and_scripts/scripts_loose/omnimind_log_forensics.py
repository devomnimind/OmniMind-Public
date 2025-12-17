#!/usr/bin/env python3
"""
OmniMind Log Forensics Tool v2.0
Análise Profunda de Logs: IIT Metrics, Tracebacks, Performance e Consciência
Otimizado para arquivos > 500MB com processamento streaming
"""

import re
import json
import sys
import gzip
from pathlib import Path
from collections import defaultdict, Counter
from statistics import mean, stdev, median
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field

# ==========================================
# Configurações de Padrões (Regex) - OmniMind
# ==========================================

PATTERNS = {
    # Métricas de Consciência (IIT)
    'phi_value': re.compile(r'Φ[_\s]*[:=]\s*([\d.]+)|phi[_\s]*[:=]\s*([\d.]+)', re.IGNORECASE),
    'phi_conscious': re.compile(r'Φ_conscious[_\s]*[:=]\s*([\d.]+)', re.IGNORECASE),
    'phi_avg': re.compile(r'Φ_avg[_\s]*[:=]\s*([\d.]+)', re.IGNORECASE),
    'force_metric': re.compile(r'força[_\s]*[:=]\s*([\d.]+)|force[_\s]*[:=]\s*([\d.]+)', re.IGNORECASE),
    'ici_metric': re.compile(r'ICI[_\s]*[:=]\s*\(?([\d.]+)\)?', re.IGNORECASE),
    'prs_metric': re.compile(r'PRS[_\s]*[:=]\s*\(?([\d.]+)\)?', re.IGNORECASE),
    'consciousness_state': re.compile(r'consciousness[_\s]*[:=]\s*\(?([\d.]+)\)?', re.IGNORECASE),

    # Colapsos e Falhas de Consciência
    'phi_collapse': re.compile(r'Φ collapse|Φ declinou|below threshold|Φ collapse', re.IGNORECASE),
    'structural_failure': re.compile(r'Structural Failure|Falha estrutural|divergência=([\d.]+)', re.IGNORECASE),
    'consciousness_unstable': re.compile(r'Estado instável|unstable|instability', re.IGNORECASE),

    # Tracebacks Python
    'traceback_start': re.compile(r'^Traceback \(most recent call last\):'),
    'traceback_file': re.compile(r'  File "([^"]+)", line (\d+), in (.+)'),
    'exception_type': re.compile(r'^(\w+Error|Exception|Warning):\s*(.+)'),

    # Agentes OmniMind
    'agent_init': re.compile(
        r'(EnhancedCodeAgent|CodeAgent|OrchestratorAgent|ReactAgent|ArchitectAgent|DebugAgent|ReviewerAgent|SecurityAgent)'
        r'.*(?:initialized|Iniciando|__init__)'
    ),
    'agent_error': re.compile(
        r'(EnhancedCodeAgent|CodeAgent|OrchestratorAgent).*object has no attribute'
    ),

    # Testes
    'test_status': re.compile(r'(PASSED|FAILED|SKIPPED|ERROR)\s+(?:\[.*?\]\s+)?([^\s]+)'),
    'test_summary': re.compile(
        r'=.*?(\d+)\s+failed.*?(\d+)\s+passed.*?(\d+)\s+skipped.*?(\d+)\s+errors.*?(\d+\.\d+)s',
        re.IGNORECASE
    ),

    # Erros Específicos OmniMind
    'cuda_oom': re.compile(r'CUDA out of memory.*?Tried to allocate ([\d.]+)\s*(\w+)', re.IGNORECASE),
    'timeout': re.compile(r'timeout.*?(\d+)\s*(?:s|seconds?|sec)|TIMEOUT.*?(\d+)s', re.IGNORECASE),
    'attribute_error': re.compile(r"AttributeError: '(\w+)' object has no attribute '(\w+)'"),

    # Entropy Warnings - detecta quando entropia excede limites
    'entropy_warning': re.compile(
        r'entropy.*exceeds.*bekenstein.*bound|entropy.*warning|WARNING.*entropy|entropy.*threshold.*exceeded',
        re.IGNORECASE
    ),

    # Meta Cognition Failures - CRÍTICO: não executar testes
    'metacognition_analysis_failed': re.compile(
        r'meta.*cogn.*analysis.*failed|metacognition.*analysis.*failed|failed.*load.*hash.*chain',
        re.IGNORECASE
    ),
    'metacognition_action_failed': re.compile(
        r'meta.*cogn.*action.*failed|metacognition.*action.*failed',
        re.IGNORECASE
    ),

    # Insufficient History - dados insuficientes para cálculos
    'insufficient_history': re.compile(
        r'insufficient.*history|history.*insufficient|insufficient.*data|insufficient.*aligned.*history|insufficient.*valid.*causal.*predictions',
        re.IGNORECASE
    ),
    # Padrões numéricos de insufficient history (ex: "4<10", "7<70")
    'insufficient_history_numeric': re.compile(
        r'(\d+)\s*<\s*(\d+).*insufficient|insufficient.*\((\d+)\s*<\s*(\d+)\)|insufficient.*history.*\((\d+)\s*<\s*(\d+)\)',
        re.IGNORECASE
    ),

    # Modelos e Referências
    'model_ref': re.compile(r'(gpt-4|phi:latest|qwen|ollama/|hf/)', re.IGNORECASE),
    'neural_component': re.compile(r'Neural component initialized: ([^\s]+)'),
}

@dataclass
class ConsciousnessMetrics:
    """Métricas de consciência agregadas."""
    phi_values: List[float] = field(default_factory=list)
    phi_conscious_values: List[float] = field(default_factory=list)
    force_values: List[float] = field(default_factory=list)
    ici_values: List[float] = field(default_factory=list)
    prs_values: List[float] = field(default_factory=list)
    collapse_events: List[Dict] = field(default_factory=list)

    def get_stats(self) -> Dict:
        """Calcula estatísticas agregadas."""
        stats = {}

        for metric_name, values in [
            ('phi', self.phi_values),
            ('phi_conscious', self.phi_conscious_values),
            ('force', self.force_values),
            ('ici', self.ici_values),
            ('prs', self.prs_values),
        ]:
            if values:
                stats[metric_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': mean(values),
                    'median': median(values),
                    'stdev': stdev(values) if len(values) > 1 else 0.0,
                }
            else:
                stats[metric_name] = None

        stats['collapse_count'] = len(self.collapse_events)

        return stats

@dataclass
class TracebackInfo:
    """Informação completa de um traceback."""
    exception_type: str
    exception_message: str
    culprit_file: str  # Arquivo do projeto que causou o erro
    culprit_line: int
    culprit_function: str
    full_stack: List[str]
    line_number: int  # Linha no log onde ocorreu

@dataclass
class AgentActivity:
    """Atividade de agentes."""
    agent_type: str
    init_count: int = 0
    error_count: int = 0
    errors: List[str] = field(default_factory=list)

class OmniMindForensicsAnalyzer:
    """Analisador forense otimizado para logs OmniMind."""

    def __init__(self, log_path: str, chunk_size: int = 10000):
        self.log_path = Path(log_path)
        self.chunk_size = chunk_size

        # Estatísticas principais
        self.stats = {
            'lines_processed': 0,
            'start_time': datetime.now(),
            'total_size_mb': 0.0,
        }

        # Métricas de consciência
        self.consciousness = ConsciousnessMetrics()

        # Análise de erros
        self.errors = {
            'total_tracebacks': 0,
            'unique_exceptions': Counter(),
            'blame_files': Counter(),  # Arquivos que causam mais erros
            'critical_tracebacks': [],  # Top 10 tracebacks mais importantes
            'error_timeline': [],  # Timeline de erros (linha, timestamp)
        }

        # Atividade de agentes
        self.agents: Dict[str, AgentActivity] = defaultdict(lambda: AgentActivity(agent_type=""))

        # Testes
        self.tests = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0.0,
        }

        # Estado interno para processamento multi-linha
        self._in_traceback = False
        self._current_traceback: List[str] = []
        self._traceback_start_line = 0

        # Outros padrões
        self.timeouts = Counter()
        self.cuda_oom_count = 0
        self.model_references = Counter()
        self.warnings = Counter()

        # Entropy warnings e Meta cognition failures
        self.entropy_warnings = Counter()  # Contador de entropy warnings
        self.metacognition_failures = {
            'analysis_failed': 0,
            'action_failed': 0,
            'total': 0,
        }

    def process_log(self) -> Dict:
        """Executa análise completa em streaming."""
        print(f"🔬 OmniMind Forensics - Análise Profunda")
        print(f"{'='*70}")
        print(f"📄 Arquivo: {self.log_path.name}")
        print(f"📊 Tamanho: {self.log_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"⚙️  Chunk size: {self.chunk_size:,} linhas")
        print(f"{'='*70}\n")

        self.stats['total_size_mb'] = self.log_path.stat().st_size / 1024 / 1024

        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='replace') as f:
                chunk = []
                chunk_count = 0

                for line in f:
                    self.stats['lines_processed'] += 1
                    chunk.append(line.rstrip())

                    if len(chunk) >= self.chunk_size:
                        self._process_chunk(chunk)
                        chunk = []
                        chunk_count += 1

                        if chunk_count % 10 == 0:
                            print(f"   ...processadas {self.stats['lines_processed']:,} linhas...", end='\r')

                # Processar último chunk
                if chunk:
                    self._process_chunk(chunk)

        except FileNotFoundError:
            print(f"❌ Erro: Arquivo não encontrado: {self.log_path}")
            sys.exit(1)
        except MemoryError:
            print(f"⚠️  Memória insuficiente. Reduzindo chunk size...")
            self.chunk_size = self.chunk_size // 2
            return self.process_log()

        print(f"\n✅ Processamento concluído: {self.stats['lines_processed']:,} linhas\n")

        # Finalizar estatísticas
        self._finalize_stats()

        # Gerar relatório
        return self._generate_report()

    def _process_chunk(self, lines: List[str]) -> None:
        """Processa um chunk de linhas."""
        for line in lines:
            # Processamento de traceback (multi-linha)
            if self._in_traceback:
                self._process_traceback_line(line)
            elif PATTERNS['traceback_start'].match(line):
                self._start_traceback(line)
            else:
                # Processamento de linha única
                self._process_single_line(line)

    def _process_single_line(self, line: str) -> None:
        """Extrai dados de linhas normais."""

        # A. Métricas de Consciência (IIT)
        self._extract_consciousness_metrics(line)

        # B. Colapsos de Consciência
        if PATTERNS['phi_collapse'].search(line):
            self.consciousness.collapse_events.append({
                'line': self.stats['lines_processed'],
                'message': line.strip()[:200],
            })

        # C. Atividade de Agentes
        match = PATTERNS['agent_init'].search(line)
        if match:
            agent_type = match.group(1)
            if agent_type and agent_type != 'None':
                if agent_type not in self.agents:
                    self.agents[agent_type] = AgentActivity(agent_type=agent_type)
                self.agents[agent_type].init_count += 1

        # D. Erros de Agentes
        match = PATTERNS['agent_error'].search(line)
        if match:
            agent_type = match.group(1)
            if agent_type not in self.agents:
                self.agents[agent_type] = AgentActivity(agent_type=agent_type)
            self.agents[agent_type].error_count += 1
            self.agents[agent_type].errors.append(line.strip()[:200])

        # E. Resultados de Testes
        match = PATTERNS['test_status'].search(line)
        if match:
            status, test_name = match.groups()
            status_key = status.lower()
            # Normalizar 'error' para 'errors'
            if status_key == 'error':
                status_key = 'errors'
            if status_key in self.tests:
                self.tests[status_key] += 1
                self.tests['total'] += 1

        # F. Resumo de Testes
        match = PATTERNS['test_summary'].search(line)
        if match:
            failed, passed, skipped, errors, duration = match.groups()
            self.tests['failed'] = int(failed)
            self.tests['passed'] = int(passed)
            self.tests['skipped'] = int(skipped)
            self.tests['errors'] = int(errors)
            self.tests['duration'] = float(duration)

        # G. CUDA OOM
        if PATTERNS['cuda_oom'].search(line):
            self.cuda_oom_count += 1

        # H. Timeouts
        match = PATTERNS['timeout'].search(line)
        if match:
            timeout_val = int(match.group(1) or match.group(2))
            if timeout_val in [30, 60, 90, 120, 240, 300, 400, 600, 800]:
                self.timeouts[timeout_val] += 1

        # I. Referências a Modelos
        match = PATTERNS['model_ref'].search(line)
        if match:
            model = match.group(1)
            self.model_references[model.lower()] += 1

        # J. Warnings
        if '[WARNING]' in line or 'WARNING' in line:
            warning_msg = line.strip()[:150]
            self.warnings[warning_msg] += 1

            # Entropy warnings
            if PATTERNS['entropy_warning'].search(line):
                entropy_msg = line.strip()[:200]
                self.entropy_warnings[entropy_msg] += 1

        # K. Meta Cognition Failures - CRÍTICO
        if PATTERNS['metacognition_analysis_failed'].search(line):
            self.metacognition_failures['analysis_failed'] += 1
            self.metacognition_failures['total'] += 1

        if PATTERNS['metacognition_action_failed'].search(line):
            self.metacognition_failures['action_failed'] += 1
            self.metacognition_failures['total'] += 1

        # L. Insufficient History - dados insuficientes para cálculos
        if PATTERNS['insufficient_history'].search(line):
            self.insufficient_history_count += 1

        # M. Insufficient History com padrões numéricos (ex: "4<10", "7<70")
        match_numeric = PATTERNS['insufficient_history_numeric'].search(line)
        if match_numeric:
            # Extrair valores numéricos (pode ter múltiplos grupos)
            groups = match_numeric.groups()
            for i in range(0, len(groups), 2):
                if i+1 < len(groups) and groups[i] and groups[i+1]:
                    self.insufficient_history_numeric.append(f"{groups[i]}<{groups[i+1]}")

    def _extract_consciousness_metrics(self, line: str) -> None:
        """Extrai métricas de consciência da linha."""
        # Φ (Phi)
        match = PATTERNS['phi_value'].search(line)
        if match:
            phi_val = float(match.group(1) or match.group(2))
            self.consciousness.phi_values.append(phi_val)

        # Φ_conscious
        match = PATTERNS['phi_conscious'].search(line)
        if match:
            phi_c = float(match.group(1))
            self.consciousness.phi_conscious_values.append(phi_c)

        # Força
        match = PATTERNS['force_metric'].search(line)
        if match:
            force = float(match.group(1) or match.group(2))
            self.consciousness.force_values.append(force)

        # ICI
        match = PATTERNS['ici_metric'].search(line)
        if match:
            ici = float(match.group(1))
            self.consciousness.ici_values.append(ici)

        # PRS
        match = PATTERNS['prs_metric'].search(line)
        if match:
            prs = float(match.group(1))
            self.consciousness.prs_values.append(prs)

    def _start_traceback(self, line: str) -> None:
        """Inicia captura de traceback."""
        self._in_traceback = True
        self._current_traceback = [line]
        self._traceback_start_line = self.stats['lines_processed']

    def _process_traceback_line(self, line: str) -> None:
        """Processa linha dentro de um traceback."""
        self._current_traceback.append(line)

        # Verificar se é o fim do traceback (linha de exceção)
        match = PATTERNS['exception_type'].match(line)

        if line and not line.startswith(' ') and not line.startswith('The above exception'):
            if match:
                exc_type = match.group(1)
                exc_msg = match.group(2)
                self._record_traceback(exc_type, exc_msg)

            self._in_traceback = False
            self._current_traceback = []

    def _record_traceback(self, exc_type: str, exc_msg: str) -> None:
        """Analisa traceback completo e identifica arquivo culpado."""
        self.errors['total_tracebacks'] += 1

        full_error = f"{exc_type}: {exc_msg[:100]}"
        self.errors['unique_exceptions'][full_error] += 1

        # Encontrar arquivo culpado (último arquivo do projeto no stack)
        culprit_file = "Unknown"
        culprit_line = 0
        culprit_function = "Unknown"

        for line in reversed(self._current_traceback):
            match = PATTERNS['traceback_file'].search(line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                func_name = match.group(3)

                # Filtrar apenas arquivos do projeto
                if 'src/' in file_path or 'tests/' in file_path:
                    # Normalizar caminho
                    if 'src/' in file_path:
                        culprit_file = file_path.split('src/')[-1]
                    elif 'tests/' in file_path:
                        culprit_file = file_path.split('tests/')[-1]
                    else:
                        culprit_file = file_path

                    culprit_line = line_num
                    culprit_function = func_name
                    break

        # Registrar arquivo culpado
        if culprit_file != "Unknown":
            self.errors['blame_files'][f"{culprit_file}:{culprit_line}"] += 1

        # Armazenar traceback crítico (top 10)
        if len(self.errors['critical_tracebacks']) < 10:
            traceback_info = TracebackInfo(
                exception_type=exc_type,
                exception_message=exc_msg,
                culprit_file=culprit_file,
                culprit_line=culprit_line,
                culprit_function=culprit_function,
                full_stack=self._current_traceback[:],
                line_number=self._traceback_start_line,
            )
            self.errors['critical_tracebacks'].append(asdict(traceback_info))

        # Timeline de erros
        self.errors['error_timeline'].append({
            'line': self._traceback_start_line,
            'exception': exc_type,
            'culprit': culprit_file,
        })

    def _finalize_stats(self) -> None:
        """Calcula estatísticas finais."""
        # Estatísticas de consciência já calculadas via get_stats()
        pass

    def _generate_report(self) -> Dict:
        """Gera relatório completo."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'log_file': str(self.log_path),
            'summary': {
                'total_lines': self.stats['lines_processed'],
                'total_size_mb': self.stats['total_size_mb'],
                'processing_time': str(datetime.now() - self.stats['start_time']),
            },
            'consciousness': self.consciousness.get_stats(),
            'errors': {
                'total_tracebacks': self.errors['total_tracebacks'],
                'unique_exceptions': dict(self.errors['unique_exceptions'].most_common(20)),
                'blame_files': dict(self.errors['blame_files'].most_common(10)),
                'critical_tracebacks': self.errors['critical_tracebacks'][:10],
            },
            'agents': {
                agent_type: {
                    'init_count': agent.init_count,
                    'error_count': agent.error_count,
                    'errors': agent.errors[:5],  # Top 5 erros
                }
                for agent_type, agent in self.agents.items()
            },
            'tests': self.tests,
            'timeouts': dict(self.timeouts),
            'cuda_oom_count': self.cuda_oom_count,
            'model_references': dict(self.model_references.most_common(10)),
            'warnings_top_20': dict(self.warnings.most_common(20)),
            'entropy_warnings': {
                'total': sum(self.entropy_warnings.values()),
                'top_10': dict(self.entropy_warnings.most_common(10)),
            },
            'metacognition_failures': self.metacognition_failures,
            'insufficient_history': {
                'total_count': self.insufficient_history_count,
                'numeric_patterns': list(set(self.insufficient_history_numeric))[:20],  # Únicos, limitado a 20
                'numeric_count': len(self.insufficient_history_numeric),
            },
        }

        # Salvar JSON
        output_file = f"data/test_reports/analysis/forensics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Imprimir relatório visual
        self._print_report(report, output_file)

        return report

    def _print_report(self, report: Dict, output_file: str) -> None:
        """Imprime relatório visual no terminal."""
        print(f"{'='*70}")
        print(f"📊 RELATÓRIO FORENSE - OMNIMIND")
        print(f"{'='*70}\n")

        # 1. Métricas de Consciência
        print("1. 🧠 MÉTRICAS DE CONSCIÊNCIA (IIT)")
        print("-" * 70)
        consciousness_stats = report['consciousness']

        for metric_name, stats in consciousness_stats.items():
            if stats and isinstance(stats, dict) and 'count' in stats:
                print(f"   {metric_name.upper()}:")
                print(f"      • Amostras: {stats['count']:,}")
                print(f"      • Mínimo:   {stats['min']:.4f}")
                print(f"      • Máximo:   {stats['max']:.4f}")
                print(f"      • Média:    {stats['mean']:.4f}")
                print(f"      • Mediana:  {stats['median']:.4f}")
                print(f"      • Desvio:   {stats['stdev']:.4f}")
                print()

        if consciousness_stats.get('collapse_count', 0) > 0:
            print(f"   ⚠️  Colapsos de Consciência: {consciousness_stats['collapse_count']}")
        print()

        # 2. Saúde do Sistema
        print("2. 🏥 SAÚDE DO SISTEMA")
        print("-" * 70)
        print(f"   • Total de Linhas:    {report['summary']['total_lines']:,}")
        print(f"   • Tamanho:            {report['summary']['total_size_mb']:.1f} MB")
        print(f"   • Total de Exceções:  {report['errors']['total_tracebacks']}")
        print(f"   • CUDA OOM:           {report['cuda_oom_count']}")
        print()

        # 3. Agentes
        print("3. 🤖 ATIVIDADE DE AGENTES")
        print("-" * 70)
        for agent_type, activity in report['agents'].items():
            print(f"   {agent_type}:")
            print(f"      • Inicializações: {activity['init_count']}")
            print(f"      • Erros:          {activity['error_count']}")
        print()

        # 4. Testes
        print("4. 🧪 RESULTADOS DE TESTES")
        print("-" * 70)
        tests = report['tests']
        # Usar total do resumo se disponível, senão calcular
        total = tests.get('total', 0)
        if total == 0:
            total = tests['passed'] + tests['failed'] + tests['skipped'] + tests['errors']

        if total > 0:
            success_rate = (tests['passed'] / total * 100) if total > 0 else 0
            print(f"   • Total:        {total:,}")
            print(f"   • ✅ Passou:    {tests['passed']:,}")
            print(f"   • ❌ Falhou:    {tests['failed']:,}")
            print(f"   • ⚠️  Erros:     {tests['errors']:,}")
            print(f"   • ⏭️  Pulados:   {tests['skipped']:,}")
            if success_rate <= 100:  # Validar taxa de sucesso
                print(f"   • 📈 Taxa Sucesso: {success_rate:.1f}%")
            if tests.get('duration', 0) > 0:
                print(f"   • ⏱️  Duração:    {tests['duration']:.1f}s ({tests['duration']/60:.1f} min)")
        print()

        # 5. Entropy Warnings e Meta Cognition Failures
        print("5. ⚠️  ENTROPY WARNINGS E META COGNITION FAILURES")
        print("-" * 70)
        entropy_info = report.get('entropy_warnings', {})
        if entropy_info.get('total', 0) > 0:
            print(f"   • Entropy Warnings: {entropy_info['total']}")
            print("      Top 3:")
            for msg, count in list(entropy_info.get('top_10', {}).items())[:3]:
                print(f"        - {msg[:100]} ({count}x)")
        else:
            print("   • Entropy Warnings: 0")

        meta_failures = report.get('metacognition_failures', {})
        if meta_failures.get('total', 0) > 0:
            print(f"\n   🔴 CRITICAL: Meta Cognition Failures: {meta_failures['total']}")
            print(f"      • Analysis Failed: {meta_failures.get('analysis_failed', 0)}")
            print(f"      • Action Failed: {meta_failures.get('action_failed', 0)}")
            print("      ⚠️  RECOMENDAÇÃO: NÃO EXECUTAR TESTES")
        else:
            print(f"\n   • Meta Cognition Failures: 0 ✅")

        # Insufficient History
        insufficient_info = report.get('insufficient_history', {})
        if insufficient_info.get('total_count', 0) > 0:
            print(f"\n   ⚠️  Insufficient History: {insufficient_info['total_count']} ocorrências")
            if insufficient_info.get('numeric_patterns'):
                print(f"      • Padrões numéricos detectados: {', '.join(insufficient_info['numeric_patterns'][:10])}")
            print("      • Significado: Dados insuficientes para cálculos completos")
            print("      • Ação: Executar mais ciclos/tasks para acumular histórico")
        else:
            print(f"\n   • Insufficient History: 0 ✅")
        print()

        # 6. Top Causas de Erro
        print("6. 🔴 TOP 5 ARQUIVOS CULPADOS")
        print("-" * 70)
        for culprit, count in list(report['errors']['blame_files'].items())[:5]:
            print(f"   {count}x em {culprit}")
        print()

        # 7. Top Exceções
        print("7. ⚠️  TOP 5 EXCEÇÕES")
        print("-" * 70)
        for exc, count in list(report['errors']['unique_exceptions'].items())[:5]:
            print(f"   {count}x {exc[:80]}...")
        print()

        # 8. Timeouts
        if report['timeouts']:
            print("8. ⏱️  TIMEOUTS DETECTADOS")
            print("-" * 70)
            for timeout_val, count in sorted(report['timeouts'].items()):
                print(f"   • {timeout_val}s: {count} ocorrências")
            print()

        print(f"{'='*70}")
        print(f"✅ Relatório JSON completo salvo em: {output_file}")
        print(f"{'='*70}\n")

def compare_reports(report1_path: str, report2_path: str) -> Dict:
    """Compara dois relatórios forenses."""
    with open(report1_path, 'r') as f:
        report1 = json.load(f)
    with open(report2_path, 'r') as f:
        report2 = json.load(f)

    comparison = {
        'report1': report1_path,
        'report2': report2_path,
        'consciousness_changes': {},
        'error_changes': {},
        'test_changes': {},
    }

    # Comparar métricas de consciência
    c1 = report1.get('consciousness', {})
    c2 = report2.get('consciousness', {})

    for metric in ['phi', 'phi_conscious', 'force']:
        if c1.get(metric) and c2.get(metric):
            mean1 = c1[metric].get('mean', 0)
            mean2 = c2[metric].get('mean', 0)
            comparison['consciousness_changes'][metric] = {
                'before': mean1,
                'after': mean2,
                'delta': mean2 - mean1,
                'percent_change': ((mean2 - mean1) / mean1 * 100) if mean1 > 0 else 0,
            }

    # Comparar erros
    comparison['error_changes'] = {
        'tracebacks': {
            'before': report1['errors']['total_tracebacks'],
            'after': report2['errors']['total_tracebacks'],
            'delta': report2['errors']['total_tracebacks'] - report1['errors']['total_tracebacks'],
        },
        'cuda_oom': {
            'before': report1.get('cuda_oom_count', 0),
            'after': report2.get('cuda_oom_count', 0),
            'delta': report2.get('cuda_oom_count', 0) - report1.get('cuda_oom_count', 0),
        },
    }

    # Comparar testes
    t1 = report1.get('tests', {})
    t2 = report2.get('tests', {})
    comparison['test_changes'] = {
        'success_rate': {
            'before': (t1.get('passed', 0) / max(t1.get('total', 1), 1) * 100),
            'after': (t2.get('passed', 0) / max(t2.get('total', 1), 1) * 100),
        },
    }

    return comparison

def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description='OmniMind Log Forensics - Análise profunda de logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Análise básica
  python scripts/omnimind_log_forensics.py data/test_reports/consolidated_fast_20251207_120233.log

  # Com chunk size menor (menos memória)
  python scripts/omnimind_log_forensics.py log.log --chunk-size 5000

  # Comparar dois relatórios
  python scripts/omnimind_log_forensics.py --compare report1.json report2.json
        """
    )

    parser.add_argument('log_path', nargs='?', help='Caminho para arquivo de log')
    parser.add_argument('--chunk-size', type=int, default=10000, help='Tamanho do chunk (linhas)')
    parser.add_argument('--compare', nargs=2, metavar=('REPORT1', 'REPORT2'),
                       help='Comparar dois relatórios JSON')

    args = parser.parse_args()

    if args.compare:
        # Modo comparação
        comparison = compare_reports(args.compare[0], args.compare[1])
        output_file = f"data/test_reports/analysis/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        print(f"✅ Comparação salva em: {output_file}")
        print(f"\n📊 Mudanças de Consciência:")
        for metric, changes in comparison['consciousness_changes'].items():
            print(f"   {metric}: {changes['before']:.4f} → {changes['after']:.4f} "
                  f"({changes['percent_change']:+.1f}%)")

    elif args.log_path:
        # Modo análise
        analyzer = OmniMindForensicsAnalyzer(args.log_path, chunk_size=args.chunk_size)
        analyzer.process_log()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

