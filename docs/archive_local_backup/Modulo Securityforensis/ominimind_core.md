#!/usr/bin/env python3
"""
OmniMind Core Agent - Nucleo do Sistema Autonomo
Responsavel por orquestracao e coordenacao principal
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio

import yaml
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llama_cpp import Llama


class OmniMindConfig(BaseModel):
    """Configuracao do sistema OmniMind"""
    name: str = "OmniMind"
    version: str = "0.1.0"
    config_path: Path = Path.home() / ".omnimind" / "config.yaml"
    model_path: str = ""
    gpu_layers: int = 20
    context_window: int = 2048
    debug: bool = False


class OmniMindAgent:
    """Agente Principal - OmniMind"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Inicializa o agente OmniMind"""
        
        self.console = Console()
        self.logger = self._setup_logging()
        
        self.config_path = Path(config_path) if config_path else Path.home() / "projects/omnimind/config/omnimind.yaml"
        self.config = self._load_config()
        
        self.status = "initializing"
        self.started_at = datetime.now()
        self.tasks_completed = 0
        self.memory_entries = 0
        
        self.logger.info(f"Iniciando {self.config['omnimind']['name']} v{self.config['omnimind']['version']}")
        
        self._initialize_llm()
        self._initialize_memory()
        self._initialize_agents()
        self._initialize_tools()
        
        self.status = "ready"
        self.logger.info("OmniMind pronto!")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging"""
        logger = logging.getLogger("omnimind")
        logger.setLevel(logging.DEBUG)
        
        log_dir = Path.home() / ".omnimind" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        fh = logging.FileHandler(
            log_dir / f"omnimind_{datetime.now().strftime('%Y%m%d')}.log"
        )
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuracao YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Configuracao carregada: {self.config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Arquivo de config nao encontrado: {self.config_path}")
            raise
    
    def _initialize_llm(self):
        """Inicializa modelo LLM com llama.cpp"""
        model_config = self.config['model']
        model_path = os.path.expanduser(model_config['primary']['model_path'])
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo nao encontrado: {model_path}")
        
        self.logger.info(f"Carregando modelo: {model_config['primary']['name']}")
        self.logger.info(f"   Quantizacao: {model_config['primary']['quantization']}")
        self.logger.info(f"   GPU Layers: {model_config['inference']['gpu_layers']}")
        
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=model_config['inference']['gpu_layers'],
            n_ctx=model_config['primary']['context_window'],
            n_threads=model_config['inference']['threads'],
            verbose=model_config['inference'].get('verbose', False)
        )
        
        self.logger.info(f"Modelo carregado com sucesso")
    
    def _initialize_memory(self):
        """Inicializa sistema de memoria"""
        self.logger.info("Inicializando sistema de memoria...")
        self.short_term_memory = []
        self.logger.info("Memoria inicializada")
    
    def _initialize_agents(self):
        """Inicializa agentes especializados"""
        self.logger.info("Inicializando agentes especializados...")
        self.agents = {}
        self.logger.info("Agentes inicializados")
    
    def _initialize_tools(self):
        """Inicializa ferramentas do sistema"""
        self.logger.info("Inicializando ferramentas...")
        self.tools = {}
        self.logger.info("Ferramentas inicializadas")
    
    async def process_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Processa requisicao do usuario"""
        
        self.logger.info(f"Nova requisicao: {user_input[:100]}...")
        
        result = {
            "status": "success",
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "agent_responses": [],
            "final_response": "",
            "memory_updated": False
        }
        
        try:
            response = self.llm(
                user_input,
                max_tokens=512,
                temperature=0.7,
                top_p=0.9
            )
            
            result["final_response"] = response['choices'][0]['text']
            self.tasks_completed += 1
            
        except Exception as e:
            self.logger.error(f"Erro ao processar: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def show_status(self):
        """Exibe status do sistema no console"""
        table = Table(title="Status do OmniMind")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        
        table.add_row("Agente", "Pronto")
        table.add_row("Modelo LLM", "Carregado")
        table.add_row("Memoria", "Inicializada")
        table.add_row("Ferramentas", "Disponivel")
        
        uptime = datetime.now() - self.started_at
        table.add_row("Uptime", f"{uptime.seconds}s")
        table.add_row("Tarefas Completadas", str(self.tasks_completed))
        table.add_row("Entradas de Memoria", str(self.memory_entries))
        
        self.console.print(table)
    
    async def run_chat_loop(self):
        """Loop principal de chat interativo"""
        self.console.print(Panel(
            "[bold cyan]OmniMind[/] - Agente Autonomo Local",
            subtitle="Digite 'help' para assistencia"
        ))
        
        while True:
            try:
                user_input = input("
Voce: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    self.console.print("[yellow]Encerrando OmniMind...[/]")
                    break
                
                if user_input.lower() == "status":
                    self.show_status()
                    continue
                
                result = await self.process_request(user_input)
                
                if result["status"] == "success":
                    self.console.print(f"
OmniMind: {result['final_response']}")
                else:
                    self.console.print(f"
Erro: {result.get('error')}")
                    
            except KeyboardInterrupt:
                self.console.print("
[yellow]Interrompido[/]")
                break
            except Exception as e:
                self.console.print(f"
Erro: {str(e)}")


def main():
    """Funcao principal"""
    try:
        agent = OmniMindAgent()
        agent.show_status()
        
        asyncio.run(agent.run_chat_loop())
        
    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()