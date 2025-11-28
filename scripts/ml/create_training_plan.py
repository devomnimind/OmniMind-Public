"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

import os
import json
import subprocess
from pathlib import Path


def run_command(cmd, shell=True, timeout=30):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {
            "command": cmd,
            "error": str(e),
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def create_practical_training_plan():
    plan = {}

    # Current limitations identified
    plan["current_limitations"] = [
        "PyTorch não instalado localmente",
        "CUDA não disponível (GPU GTX 1650 não configurada)",
        "Transformers library não instalada",
        "Nenhum token API configurado (GitHub, Azure, OpenAI)",
        "Hardware limitado: 4GB VRAM + 24GB RAM",
    ]

    # Immediate setup recommendations
    plan["immediate_setup"] = [
        "Instalar PyTorch CPU-only para desenvolvimento",
        "Configurar GitHub CLI e token para GitHub Models",
        "Instalar bibliotecas básicas de ML (numpy, pandas, scikit-learn)",
        "Configurar ambiente de desenvolvimento Python",
        "Testar conectividade com APIs remotas",
    ]

    # Phased training approach
    plan["phased_approach"] = {
        "phase_1_preparation": {
            "duration": "1-2 dias",
            "focus": "Setup e validação",
            "tasks": [
                "Instalar dependências Python locais",
                "Configurar tokens API (GitHub, opcionalmente outros)",
                "Validar dados de treinamento coletados",
                "Criar ambiente de desenvolvimento consistente",
            ],
            "local_remote_ratio": "80% local / 20% remoto",
        },
        "phase_2_prototyping": {
            "duration": "3-5 dias",
            "focus": "Experimentos iniciais",
            "tasks": [
                "Testes com GitHub Models (se token disponível)",
                "Fine-tuning básico com APIs remotas",
                "Comparação de performance local vs remoto",
                "Identificação de melhores abordagens",
            ],
            "local_remote_ratio": "40% local / 60% remoto",
        },
        "phase_3_optimization": {
            "duration": "1-2 semanas",
            "focus": "Otimização e produção",
            "tasks": [
                "Otimização de modelos para hardware limitado",
                "Implementação de quantização e compressão",
                "Fine-tuning avançado com melhores práticas",
                "Preparação para deployment",
            ],
            "local_remote_ratio": "60% local / 40% remoto",
        },
    }

    # Specific recommendations based on hardware
    plan["hardware_optimized_strategy"] = {
        "local_focus": [
            "Modelos leves (TinyLLaMA, Phi-1.5, distilBERT)",
            "Quantização 4-bit/8-bit para reduzir uso de memória",
            "LoRA/PEFT para fine-tuning eficiente",
            "CPU optimization com MKL/OpenBLAS",
            "Batch processing otimizado para RAM limitada",
        ],
        "remote_focus": [
            "GitHub Models para experimentação gratuita",
            "Azure AI se disponível via organização",
            "OpenAI API para fine-tuning avançado",
            "Google AI Studio para prototipagem rápida",
            "Hugging Face Spaces para demos",
        ],
    }

    # Cost-benefit analysis
    plan["cost_benefit_analysis"] = {
        "local_advantages": [
            "Controle total sobre dados e modelos",
            "Sem custos recorrentes de API",
            "Privacidade e segurança de dados",
            "Customização completa",
            "Offline capability",
        ],
        "local_disadvantages": [
            "Limitações de hardware (4GB VRAM)",
            "Setup inicial mais complexo",
            "Manutenção de infraestrutura",
            "Curva de aprendizado steeper",
            "Limitações de escala",
        ],
        "remote_advantages": [
            "Acesso a modelos state-of-the-art",
            "Setup rápido e fácil",
            "Escalabilidade automática",
            "Manutenção zero de infraestrutura",
            "APIs bem documentadas",
        ],
        "remote_disadvantages": [
            "Custos recorrentes de API",
            "Dependência de conectividade",
            "Limitações de rate limits",
            "Menos controle sobre dados",
            "Possíveis restrições de uso",
        ],
    }

    # Recommended tools and frameworks
    plan["recommended_tools"] = {
        "local_first": [
            "PyTorch CPU-only (pip install torch --index-url https://download.pytorch.org/whl/cpu)",
            "Transformers (pip install transformers)",
            "Accelerate para otimização (pip install accelerate)",
            "PEFT para fine-tuning eficiente (pip install peft)",
            "BitsAndBytes para quantização (pip install bitsandbytes)",
        ],
        "remote_first": [
            "GitHub CLI (gh auth login)",
            "Azure CLI (az login) se disponível",
            "OpenAI Python client (openai)",
            "Hugging Face Hub (huggingface_hub)",
            "Requests para APIs customizadas",
        ],
        "development_tools": [
            "Jupyter Lab para experimentação",
            "MLflow para tracking de experimentos",
            "Weights & Biases para monitoramento",
            "Streamlit para demos rápidas",
            "Gradio para interfaces de modelo",
        ],
    }

    # Success metrics
    plan["success_metrics"] = {
        "technical": [
            "Modelos treinados com >80% accuracy",
            "Inferência <500ms por exemplo",
            "Uso de memória <3GB durante treinamento",
            "Deployment funcional local/remoto",
        ],
        "business": [
            "ROI positivo vs custos de API",
            "Tempo de desenvolvimento reduzido",
            "Facilidade de manutenção",
            "Escalabilidade para produção",
        ],
    }

    return plan


def generate_setup_script():
    setup_script = """#!/bin/bash
# Script de Setup para Treinamento ML Local/Remoto

echo "🚀 Iniciando setup de ambiente ML/AI..."

# Instalar PyTorch CPU-only
echo "📦 Instalando PyTorch CPU..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Instalar bibliotecas essenciais
echo "📦 Instalando bibliotecas ML..."
pip install transformers accelerate peft datasets evaluate

# Instalar ferramentas de desenvolvimento
echo "🛠️ Instalando ferramentas de desenvolvimento..."
pip install jupyterlab mlflow streamlit gradio

# Configurar GitHub CLI (se disponível)
echo "🔑 Configurando GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "GitHub CLI encontrado. Execute: gh auth login"
else
    echo "GitHub CLI não encontrado. Instale com: sudo apt install gh"
fi

# Verificar instalação
echo "✅ Verificando instalação..."
python3 -c "
import torch
import transformers
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'Transformers: {transformers.__version__}')
print('Setup concluído!')
"

echo "🎯 Setup completo! Próximos passos:"
echo "1. Configure tokens API (GitHub, etc.)"
echo "2. Teste com dados de treinamento"
echo "3. Comece experimentos locais"
"""

    return setup_script


# Create comprehensive plan
print("🧠 Criando plano prático de treinamento ML/AI...")
training_plan = create_practical_training_plan()

# Generate setup script
setup_script = generate_setup_script()

# Save everything
with open("data/ml/training_data_collection/comprehensive_training_plan.json", "w") as f:
    json.dump(training_plan, f, indent=2, default=str)

with open("setup_ml_environment.sh", "w") as f:
    f.write(setup_script)

os.chmod("setup_ml_environment.sh", 0o755)

print("✅ Plano salvo em: data/ml/training_data_collection/comprehensive_training_plan.json")
print("✅ Script de setup criado: setup_ml_environment.sh")
print(
    f'📏 Tamanho do plano: {os.path.getsize("data/ml/training_data_collection/comprehensive_training_plan.json")} bytes'
)

# Display key recommendations
print("\\n" + "=" * 60)
print("🎯 PLANO ABRANGENTE DE TREINAMENTO ML/AI")
print("=" * 60)

print("\\n⚠️ LIMITAÇÕES ATUAIS IDENTIFICADAS:")
for limitation in training_plan["current_limitations"]:
    print(f"• {limitation}")

print("\\n🚀 CONFIGURAÇÃO IMEDIATA RECOMENDADA:")
for i, task in enumerate(training_plan["immediate_setup"], 1):
    print(f"{i}. {task}")

print("\\n📅 ABORDAGEM EM FASES:")
for phase, details in training_plan["phased_approach"].items():
    print(f'\\n{phase.replace("_", " ").title()}:')
    print(f'  • Duração: {details["duration"]}')
    print(f'  • Foco: {details["focus"]}')
    print(f'  • Local/Remoto: {details["local_remote_ratio"]}')

print("\\n💡 ESTRATÉGIA HÍBRIDA ÓTIMA:")
print("\\n🔧 Foco Local (Hardware Otimizado):")
for item in training_plan["hardware_optimized_strategy"]["local_focus"][:3]:
    print(f"• {item}")

print("\\n🌐 Foco Remoto (APIs e Serviços):")
for item in training_plan["hardware_optimized_strategy"]["remote_focus"][:3]:
    print(f"• {item}")

print("\\n🎯 PRÓXIMO PASSO: Execute ./setup_ml_environment.sh para começar!")
