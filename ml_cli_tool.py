#!/usr/bin/env python3
"""
ML CLI Tool - Interface de linha de comando para otimização híbrida
Uso: python ml_cli_tool.py <comando> [opções]
"""

import argparse
import json
import sys
from pathlib import Path
from hybrid_ml_optimizer import HybridMLOptimizer

class MLCLI:
    def __init__(self):
        self.optimizer = HybridMLOptimizer()
        
    def cmd_limits(self, args):
        """Verifica limites atuais"""
        print("📊 Verificando limites...")
        
        gh_limits = self.optimizer.check_github_limits()
        hf_limits = self.optimizer.check_hf_limits()
        
        print("GitHub Models:")
        print(f"  📈 Requests restantes: {gh_limits.get('remaining', 'N/A')}/5000")
        print(f"  ⏰ Reset em: {gh_limits.get('reset', 'N/A')}")
        
        print("\\nHugging Face:")
        print(f"  📥 Downloads restantes: ~{hf_limits.get('downloads_remaining', 'N/A')}")
        print(f"  📤 Uploads restantes: ~{hf_limits.get('uploads_remaining', 'N/A')} MB")
    
    def cmd_optimize(self, args):
        """Otimiza escolha de modelo para tarefa"""
        if not args.task:
            print("❌ Especifique uma tarefa: --task <tarefa>")
            return
        
        choice = self.optimizer.optimize_model_choice(args.task)
        
        print(f"🎯 Tarefa: {args.task}")
        print(f"🤖 Modelo escolhido: {choice['chosen_model']}")
        print(f"🏢 Provedor: {choice['provider']}")
        print(f"💡 Razão: {choice['reason']}")
    
    def cmd_call(self, args):
        """Chama modelo otimizado"""
        if not args.task or not args.prompt:
            print("❌ Especifique --task e --prompt")
            return
        
        print(f"🚀 Chamando modelo para tarefa: {args.task}")
        print(f"💬 Prompt: {args.prompt[:50]}...")
        
        result = self.optimizer.call_optimized_model(
            args.task, 
            args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        if result["success"]:
            print("✅ Sucesso!")
            print(f"📝 Resposta: {result['response']}")
            print(f"💰 Custo estimado: ${result['cost_estimate']:.4f}")
        else:
            print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    def cmd_report(self, args):
        """Gera relatório de uso"""
        report = self.optimizer.get_usage_report()
        
        print("📊 RELATÓRIO DE USO - ML HÍBRIDO")
        print("=" * 40)
        
        print("\\nGitHub Models:")
        print(f"  📈 Requests restantes: {report['github_usage']['requests_remaining']}")
        print(f"  💰 Custo acumulado: ${report['github_usage']['estimated_cost']:.3f}")
        
        print("\\nHugging Face:")
        print(f"  📥 Downloads restantes: {report['hf_usage']['downloads_remaining']}")
        print(f"  📤 Uploads restantes: {report['hf_usage']['uploads_remaining']} MB")
        
        print("\\n💡 Sugestões de otimização:")
        for suggestion in report['optimization_suggestions']:
            print(f"  • {suggestion}")
    
    def cmd_train(self, args):
        """Inicia treinamento híbrido (simulado)"""
        print("🎓 Iniciando treinamento híbrido...")
        print("📋 Carregando dados de treinamento...")
        
        # Carrega plano de treinamento
        plan_path = Path("training_data_collection/comprehensive_training_plan.json")
        if plan_path.exists():
            with open(plan_path) as f:
                plan = json.load(f)
            
            print(f"📚 Plano carregado: {plan.get('strategy', 'N/A')}")
            print(f"🎯 Fases: {len(plan.get('phased_approach', []))}")
            
            # Simula treinamento
            for phase in plan.get('phased_approach', [])[:3]:  # primeiras 3 fases
                print(f"\\n🏃 Fase: {phase.get('phase', 'N/A')}")
                print(f"   📝 Objetivo: {phase.get('objective', 'N/A')[:50]}...")
                print("   ✅ Concluída (simulado)")
        else:
            print("❌ Arquivo de plano não encontrado")

def main():
    parser = argparse.ArgumentParser(
        description="ML CLI Tool - Otimização híbrida GitHub + HF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python ml_cli_tool.py limits
  python ml_cli_tool.py optimize --task code_generation
  python ml_cli_tool.py call --task text_classification --prompt "Classifique este texto: ..."
  python ml_cli_tool.py report
  python ml_cli_tool.py train
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando limits
    subparsers.add_parser('limits', help='Verifica limites atuais')
    
    # Comando optimize
    optimize_parser = subparsers.add_parser('optimize', help='Otimiza escolha de modelo')
    optimize_parser.add_argument('--task', required=True, 
                                choices=['text_classification', 'text_generation', 
                                       'code_generation', 'sentiment_analysis'],
                                help='Tipo de tarefa')
    
    # Comando call
    call_parser = subparsers.add_parser('call', help='Chama modelo otimizado')
    call_parser.add_argument('--task', required=True,
                            choices=['text_classification', 'text_generation',
                                   'code_generation', 'sentiment_analysis'],
                            help='Tipo de tarefa')
    call_parser.add_argument('--prompt', required=True, help='Prompt para o modelo')
    call_parser.add_argument('--max-tokens', type=int, default=100, 
                            help='Máximo de tokens (padrão: 100)')
    call_parser.add_argument('--temperature', type=float, default=0.7,
                            help='Temperatura (padrão: 0.7)')
    
    # Comando report
    subparsers.add_parser('report', help='Gera relatório de uso')
    
    # Comando train
    subparsers.add_parser('train', help='Inicia treinamento híbrido')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = MLCLI()
    
    # Executa comando
    if args.command == 'limits':
        cli.cmd_limits(args)
    elif args.command == 'optimize':
        cli.cmd_optimize(args)
    elif args.command == 'call':
        cli.cmd_call(args)
    elif args.command == 'report':
        cli.cmd_report(args)
    elif args.command == 'train':
        cli.cmd_train(args)

if __name__ == "__main__":
    main()
