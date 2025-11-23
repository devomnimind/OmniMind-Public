#!/usr/bin/env python3
"""
Script para identificar documentação desatualizada no projeto OmniMind.

Verifica:
- README.md com informações incorretas sobre testes
- Documentação de testing desatualizada
- Comentários em pytest.ini e .coveragerc
- Documentação em docs/ que menciona números de testes
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def check_readme(readme_path: Path, actual_stats: Dict) -> List[Dict]:
    """Check README.md for outdated test statistics."""
    issues = []
    
    if not readme_path.exists():
        return issues
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for test count mentions
    test_patterns = [
        r'(\d+)\s+tests?',
        r'(\d+)\s+unit tests?',
        r'test coverage:?\s*(\d+)%',
        r'coverage:?\s*(\d+)%',
        r'(\d+)\s+test cases?',
    ]
    
    for pattern in test_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'file': 'README.md',
                'line': line_num,
                'found': match.group(0),
                'context': content[max(0, match.start()-50):match.end()+50],
                'type': 'test_count_reference'
            })
    
    return issues


def check_docs_directory(docs_dir: Path) -> List[Dict]:
    """Check documentation directory for outdated test information."""
    issues = []
    
    if not docs_dir.exists():
        return issues
    
    # Files to check
    test_docs = [
        'TESTING_QA_QUICK_START.md',
        'VALIDATION_GUIDE.md',
        'STATUS_PROJECT.md',
        'RESUMO_EXECUTIVO_PHASE6.md'
    ]
    
    for doc_file in test_docs:
        doc_path = docs_dir.parent / doc_file
        if not doc_path.exists():
            doc_path = docs_dir / doc_file
        
        if not doc_path.exists():
            continue
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for test statistics
        patterns = [
            (r'(\d+)\s+testes?', 'test_count'),
            (r'cobertura:?\s*(\d+)%', 'coverage'),
            (r'(\d+)\s+arquivos?\s+de\s+teste', 'test_files'),
        ]
        
        for pattern, issue_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': str(doc_path.relative_to(docs_dir.parent)),
                    'line': line_num,
                    'found': match.group(0),
                    'type': issue_type
                })
    
    return issues


def check_pytest_ini(pytest_ini_path: Path) -> List[Dict]:
    """Check pytest.ini for outdated comments or configurations."""
    issues = []
    
    if not pytest_ini_path.exists():
        return issues
    
    with open(pytest_ini_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Check for --maxfail=5 which is preventing full collection
        if '--maxfail' in line and '=' in line:
            value = line.split('=')[1].strip()
            if value.isdigit() and int(value) < 100:
                issues.append({
                    'file': 'pytest.ini',
                    'line': i,
                    'found': line.strip(),
                    'type': 'low_maxfail',
                    'suggestion': 'Increase --maxfail to allow full test collection'
                })
        
        # Check for legacy exclusion that doesn't exist
        if 'legacy' in line.lower() and 'ignore' in line.lower():
            issues.append({
                'file': 'pytest.ini',
                'line': i,
                'found': line.strip(),
                'type': 'legacy_exclusion',
                'suggestion': 'Verificar se diretório legacy ainda existe'
            })
    
    return issues


def check_coverage_config(coveragerc_path: Path) -> List[Dict]:
    """Check .coveragerc for outdated exclusions."""
    issues = []
    
    if not coveragerc_path.exists():
        return issues
    
    with open(coveragerc_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Check if excluded files still exist
        if line.strip() and not line.strip().startswith('[') and not line.strip().startswith('#'):
            if 'src/' in line or '.py' in line:
                # This is a file exclusion
                file_pattern = line.strip()
                issues.append({
                    'file': '.coveragerc',
                    'line': i,
                    'found': line.strip(),
                    'type': 'coverage_exclusion',
                    'suggestion': 'Verificar se arquivo ainda deve ser excluído'
                })
    
    return issues


def find_test_count_in_files(project_root: Path, extensions: List[str] = ['.md', '.txt', '.rst']) -> List[Dict]:
    """Find any files mentioning specific test counts."""
    issues = []
    
    # Common places where test counts might be mentioned
    search_paths = [
        project_root / 'docs',
        project_root / '.github',
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        for ext in extensions:
            for file_path in search_path.rglob(f'*{ext}'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for specific numbers that might be test counts
                    # Common patterns: "2538 tests", "1290 tests", etc.
                    pattern = r'(\d{3,4})\s+(?:tests?|testes?)'
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        context_start = max(0, match.start() - 40)
                        context_end = min(len(content), match.end() + 40)
                        
                        issues.append({
                            'file': str(file_path.relative_to(project_root)),
                            'line': line_num,
                            'found': match.group(0),
                            'context': content[context_start:context_end].replace('\n', ' '),
                            'type': 'specific_test_count'
                        })
                except Exception:
                    pass
    
    return issues


def main():
    """Run documentation check."""
    project_root = Path(__file__).resolve().parent.parent
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("="*80)
    print("VERIFICAÇÃO DE DOCUMENTAÇÃO DESATUALIZADA".center(80))
    print("="*80)
    print(f"{Colors.ENDC}\n")
    
    # Get actual statistics from the analysis
    report_path = project_root / 'test_suite_analysis_report.json'
    actual_stats = {}
    if report_path.exists():
        import json
        with open(report_path, 'r') as f:
            data = json.load(f)
            actual_stats = data.get('summary', {})
    
    all_issues = []
    
    # Check README
    print(f"{Colors.OKBLUE}Verificando README.md...{Colors.ENDC}")
    readme_issues = check_readme(project_root / 'README.md', actual_stats)
    all_issues.extend(readme_issues)
    print(f"  Encontrados {len(readme_issues)} possíveis problemas")
    
    # Check docs directory
    print(f"\n{Colors.OKBLUE}Verificando diretório docs/...{Colors.ENDC}")
    docs_issues = check_docs_directory(project_root / 'docs')
    all_issues.extend(docs_issues)
    print(f"  Encontrados {len(docs_issues)} possíveis problemas")
    
    # Check pytest.ini
    print(f"\n{Colors.OKBLUE}Verificando pytest.ini...{Colors.ENDC}")
    pytest_issues = check_pytest_ini(project_root / 'pytest.ini')
    all_issues.extend(pytest_issues)
    print(f"  Encontrados {len(pytest_issues)} possíveis problemas")
    
    # Check .coveragerc
    print(f"\n{Colors.OKBLUE}Verificando .coveragerc...{Colors.ENDC}")
    coverage_issues = check_coverage_config(project_root / '.coveragerc')
    all_issues.extend(coverage_issues)
    print(f"  Encontrados {len(coverage_issues)} possíveis problemas")
    
    # Search for specific test counts
    print(f"\n{Colors.OKBLUE}Procurando menções de contagens de testes...{Colors.ENDC}")
    count_issues = find_test_count_in_files(project_root)
    all_issues.extend(count_issues)
    print(f"  Encontrados {len(count_issues)} possíveis problemas")
    
    # Display results
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("="*80)
    print("RESUMO DE PROBLEMAS ENCONTRADOS".center(80))
    print("="*80)
    print(f"{Colors.ENDC}\n")
    
    if not all_issues:
        print(f"{Colors.OKGREEN}✓ Nenhum problema de documentação encontrado!{Colors.ENDC}")
        return 0
    
    # Group by file
    by_file = {}
    for issue in all_issues:
        file_name = issue['file']
        if file_name not in by_file:
            by_file[file_name] = []
        by_file[file_name].append(issue)
    
    for file_name, issues in sorted(by_file.items()):
        print(f"\n{Colors.WARNING}{Colors.BOLD}{file_name}{Colors.ENDC}")
        for issue in issues:
            print(f"  Linha {issue['line']}: {issue['found']}")
            if 'suggestion' in issue:
                print(f"    → {Colors.OKBLUE}{issue['suggestion']}{Colors.ENDC}")
            if 'context' in issue and len(issue['context']) < 100:
                print(f"    Contexto: ...{issue['context']}...")
    
    # Print statistics
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("="*80)
    print("ESTATÍSTICAS CORRETAS (Para Referência)".center(80))
    print("="*80)
    print(f"{Colors.ENDC}\n")
    
    if actual_stats:
        print(f"Total de arquivos de teste: {Colors.OKGREEN}{actual_stats.get('total_test_files', 'N/A')}{Colors.ENDC}")
        print(f"Total de funções de teste definidas: {Colors.OKGREEN}{actual_stats.get('total_test_functions_defined', 'N/A')}{Colors.ENDC}")
        print(f"Testes executáveis: {Colors.OKGREEN}{actual_stats.get('expected_runnable_tests', 'N/A')}{Colors.ENDC}")
        print(f"Testes bloqueados por imports: {Colors.WARNING}{actual_stats.get('tests_blocked_by_imports', 'N/A')}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Total de problemas encontrados: {len(all_issues)}{Colors.ENDC}")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_issues': len(all_issues),
        'issues_by_file': {k: len(v) for k, v in by_file.items()},
        'all_issues': all_issues,
        'current_stats': actual_stats
    }
    
    report_file = project_root / 'documentation_issues_report.json'
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.OKGREEN}Relatório salvo em: {report_file}{Colors.ENDC}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
