#!/usr/bin/env python3
"""
Hybrid ML Optimizer - Integração GitHub Models + Hugging Face
Otimizado para limites mensais e recursos limitados
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class RateLimits:
    github_requests_remaining: int = 5000
    github_reset_time: int = 0
    hf_downloads_remaining: int = 10000  # aproximado
    hf_uploads_remaining: int = 5000  # MB aproximado
    
    def can_make_github_request(self) -> bool:
        return self.github_requests_remaining > 10  # margem de segurança
    
    def can_download_hf(self) -> bool:
        return self.hf_downloads_remaining > 100
    
    def wait_for_reset(self):
        if self.github_reset_time > time.time():
            wait_time = self.github_reset_time - time.time()
            print(f"⏳ Aguardando reset GitHub: {wait_time:.0f}s")
            time.sleep(min(wait_time, 60))  # max 1 min

class HybridMLOptimizer:
    def __init__(self):
        self.rate_limits = RateLimits()
        self.models_cache = {}
        self.training_data_path = Path("training_data_collection")
        
    def check_github_limits(self) -> Dict:
        """Verifica limites atuais do GitHub"""
        try:
            result = os.popen("gh api /rate_limit --jq '.rate'").read()
            if result:
                limits = json.loads(result)
                self.rate_limits.github_requests_remaining = limits.get('remaining', 0)
                self.rate_limits.github_reset_time = limits.get('reset', 0)
                return limits
        except Exception as e:
            print(f"❌ Erro ao verificar GitHub: {e}")
        return {}
    
    def check_hf_limits(self) -> Dict:
        """Verifica limites aproximados do Hugging Face"""
        # Como HF não expõe limites via API facilmente, usamos estimativas
        return {
            "downloads_remaining": self.rate_limits.hf_downloads_remaining,
            "uploads_remaining": self.rate_limits.hf_uploads_remaining,
            "estimated_reset": "monthly"
        }
    
    def optimize_model_choice(self, task: str) -> Dict:
        """Escolhe modelo otimizado baseado na tarefa e limites"""
        
        # Estratégia híbrida baseada em tarefa
        strategies = {
            "text_classification": {
                "primary": "github:copilot-chat",  # GitHub Models
                "fallback": "hf:distilbert-base-uncased",  # HF local
                "reason": "GitHub melhor para classificação rápida"
            },
            "text_generation": {
                "primary": "github:gpt-4o-mini",  # GitHub Models
                "fallback": "hf:phi-1_5",  # Modelo leve local
                "reason": "Balanceia qualidade e custo"
            },
            "code_generation": {
                "primary": "github:copilot-chat",  # Melhor para código
                "fallback": "hf:codeparrot-small",  # Modelo código local
                "reason": "GitHub otimizado para desenvolvimento"
            },
            "sentiment_analysis": {
                "primary": "hf:cardiffnlp/twitter-roberta-base-sentiment",
                "fallback": "github:gpt-4o-mini",
                "reason": "Modelo especializado local primeiro"
            }
        }
        
        strategy = strategies.get(task, strategies["text_classification"])
        
        # Verifica disponibilidade baseado em limites
        if self.rate_limits.can_make_github_request():
            chosen = strategy["primary"]
            provider = "github"
        else:
            chosen = strategy["fallback"] 
            provider = "hf"
            
        return {
            "task": task,
            "chosen_model": chosen,
            "provider": provider,
            "reason": strategy["reason"],
            "limits_checked": True
        }
    
    def call_optimized_model(self, task: str, prompt: str, **kwargs) -> Dict:
        """Chama modelo de forma otimizada"""
        
        # Atualiza limites
        self.check_github_limits()
        
        # Escolhe modelo
        model_choice = self.optimize_model_choice(task)
        
        result = {
            "model_choice": model_choice,
            "success": False,
            "response": None,
            "tokens_used": 0,
            "cost_estimate": 0
        }
        
        try:
            if model_choice["provider"] == "github":
                # Chamada GitHub Models
                response = self._call_github_model(model_choice["chosen_model"], prompt, **kwargs)
                result.update({
                    "success": True,
                    "response": response,
                    "cost_estimate": 0.002  # estimativa por chamada
                })
                self.rate_limits.github_requests_remaining -= 1
                
            elif model_choice["provider"] == "hf":
                # Chamada Hugging Face (local ou API)
                response = self._call_hf_model(model_choice["chosen_model"], prompt, **kwargs)
                result.update({
                    "success": True,
                    "response": response,
                    "cost_estimate": 0  # gratuito para inference básica
                })
                
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Erro na chamada: {e}")
        
        return result
    
    def _call_github_model(self, model: str, prompt: str, **kwargs) -> str:
        """Chama modelo via GitHub Models API"""
        # Simulação - em produção usaria GitHub Models API
        model_name = model.split(":")[1]
        
        # Simula chamada baseada no modelo
        if "copilot" in model_name:
            return f"[GitHub {model_name}] Análise completa do prompt: {prompt[:50]}..."
        elif "gpt" in model_name:
            return f"[GitHub {model_name}] Resposta otimizada: {prompt[:50]}..."
        
        return f"[GitHub {model_name}] Resposta padrão para: {prompt[:50]}..."
    
    def _call_hf_model(self, model: str, prompt: str, **kwargs) -> str:
        """Chama modelo via Hugging Face"""
        model_name = model.split(":")[1]
        
        # Simulação - em produção usaria transformers
        return f"[HF {model_name}] Processamento local: {prompt[:50]}..."
    
    def get_usage_report(self) -> Dict:
        """Relatório de uso e otimização"""
        return {
            "github_usage": {
                "requests_remaining": self.rate_limits.github_requests_remaining,
                "estimated_cost": (5000 - self.rate_limits.github_requests_remaining) * 0.002
            },
            "hf_usage": {
                "downloads_remaining": self.rate_limits.hf_downloads_remaining,
                "uploads_remaining": self.rate_limits.hf_uploads_remaining
            },
            "optimization_suggestions": [
                "Use GitHub Models para tarefas rápidas",
                "Cache resultados HF localmente",
                "Batch requests quando possível",
                "Monitore limites semanalmente"
            ]
        }

def main():
    """Função principal para demonstração"""
    optimizer = HybridMLOptimizer()
    
    print("�� Hybrid ML Optimizer Iniciado")
    print("=" * 50)
    
    # Verifica limites
    print("📊 Verificando limites...")
    gh_limits = optimizer.check_github_limits()
    hf_limits = optimizer.check_hf_limits()
    
    print(f"GitHub: {gh_limits.get('remaining', 'N/A')} requests restantes")
    print(f"HF: ~{hf_limits.get('downloads_remaining', 'N/A')} downloads restantes")
    
    # Demonstra otimizações
    print("\\n🧠 Testando otimizações...")
    
    test_tasks = ["text_classification", "code_generation", "sentiment_analysis"]
    
    for task in test_tasks:
        choice = optimizer.optimize_model_choice(task)
        print(f"📋 {task}: {choice['chosen_model']} ({choice['provider']})")
        print(f"   💡 {choice['reason']}")
    
    # Relatório final
    print("\\n📈 Relatório de Uso:")
    report = optimizer.get_usage_report()
    print(f"💰 Custo estimado GitHub: ${report['github_usage']['estimated_cost']:.3f}")
    
    print("\\n✅ Otimizador configurado! Use hybrid_ml_optimizer.call_optimized_model()")

if __name__ == "__main__":
    main()
