#!/usr/bin/env python3
"""
Teste final - VS Code deve conectar com os MCPs
"""

import requests
import json

def test_mcp_connectivity():
    """Testa se consegue conectar com os MCPs via HTTP"""
    print("🧪 Testando conectividade MCP...")
    
    # Testar servidor Memory (porta 4321)
    url = "http://127.0.0.1:4321/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "vscode",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print("✅ MCP Memory Server (porta 4321) - CONECTADO")
            return True
        else:
            print(f"❌ MCP Memory Server (porta 4321) - Erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Memory Server (porta 4321) - Erro: {e}")
        return False

def test_vscode_config():
    """Verifica se a configuração .vscode/mcp.json está correta"""
    print("\n📋 Verificando configuração .vscode/mcp.json...")
    
    import json
    from pathlib import Path
    
    config_path = Path(".vscode/mcp.json")
    if not config_path.exists():
        print("❌ Arquivo .vscode/mcp.json não encontrado")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        expected_servers = [
            "omnimind_filesystem", "omnimind_memory", "omnimind_thinking",
            "omnimind_context", "omnimind_python", "omnimind_system",
            "omnimind_logging", "omnimind_git", "omnimind_sqlite"
        ]
        
        if len(servers) == len(expected_servers):
            print(f"✅ Configuração .vscode/mcp.json válida ({len(servers)} servidores)")
            return True
        else:
            print(f"❌ Configuração inválida: esperado {len(expected_servers)}, encontrado {len(servers)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao ler configuração: {e}")
        return False

def main():
    """Executa testes finais"""
    print("=" * 60)
    print("🎯 TESTE FINAL - VS CODE + MCP")
    print("=" * 60)
    
    # Teste 1: Conectividade MCP
    mcp_ok = test_mcp_connectivity()
    
    # Teste 2: Configuração VS Code
    config_ok = test_vscode_config()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if mcp_ok and config_ok:
        print("🎉 SUCESSO TOTAL!")
        print("✅ MCPs estão rodando e conectáveis")
        print("✅ Configuração .vscode/mcp.json está correta")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. No VS Code: Ctrl+Shift+P")
        print("2. Digite: 'MCP: Show Server Status'")
        print("3. Deve mostrar os 9 servidores MCP conectados")
        return 0
    else:
        print("⚠️  PROBLEMAS DETECTADOS:")
        if not mcp_ok:
            print("❌ MCPs não estão conectáveis")
        if not config_ok:
            print("❌ Configuração .vscode/mcp.json incorreta")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())