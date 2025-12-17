#!/usr/bin/env python3
"""
Teste de configuração MCP para VS Code
Verifica se a configuração .vscode/mcp.json está correta
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def test_vscode_mcp_config():
    """Testa a configuração .vscode/mcp.json"""
    
    print("🔍 Testando configuração .vscode/mcp.json")
    
    # Verificar se o arquivo existe
    mcp_config_path = Path(".vscode/mcp.json")
    if not mcp_config_path.exists():
        print("❌ Arquivo .vscode/mcp.json não encontrado!")
        return False
    
    # Ler e validar JSON
    try:
        with open(mcp_config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return False
    
    # Verificar estrutura
    if "mcpServers" not in config:
        print("❌ Campo 'mcpServers' não encontrado")
        return False
    
    servers = config["mcpServers"]
    print(f"✅ Encontrados {len(servers)} servidores MCP")
    
    # Verificar cada servidor
    expected_servers = [
        "omnimind_filesystem", "omnimind_memory", "omnimind_thinking",
        "omnimind_context", "omnimind_python", "omnimind_system",
        "omnimind_logging", "omnimind_git", "omnimind_sqlite"
    ]
    
    ports_used = set()
    for server_name in expected_servers:
        if server_name not in servers:
            print(f"❌ Servidor {server_name} não encontrado")
            return False
        
        server_config = servers[server_name]
        
        # Verificar se usa comando python3
        if server_config.get("command") != "python3":
            print(f"❌ {server_name}: comando deve ser 'python3', encontrado '{server_config.get('command')}'")
            return False
        
        # Verificar se tem args
        if "args" not in server_config:
            print(f"❌ {server_name}: campo 'args' não encontrado")
            return False
        
        # Verificar porta única
        port = server_config.get("env", {}).get("MCP_PORT")
        if not port:
            print(f"❌ {server_name}: porta não definida")
            return False
        
        if port in ports_used:
            print(f"❌ Porta {port} duplicada para {server_name}")
            return False
        
        ports_used.add(port)
        print(f"✅ {server_name}: porta {port} - OK")
    
    print(f"✅ Configuração .vscode/mcp.json válida!")
    print(f"✅ {len(ports_used)} portas únicas em uso: {sorted(ports_used)}")
    return True

def test_python_environment():
    """Testa o ambiente Python"""
    print("\n🐍 Testando ambiente Python")
    
    # Verificar python do venv
    try:
        result = subprocess.run([".venv/bin/python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python3 encontrado: {result.stdout.strip()}")
        else:
            print("❌ python3 não encontrado")
            return False
    except FileNotFoundError:
        print("❌ python3 não está no PATH")
        return False
    
    # Verificar se consegue importar módulos
    try:
        result = subprocess.run([
            "python3", "-c", 
            "import sys; sys.path.insert(0, '.'); from src.integrations.mcp_memory_server import MemoryMCPServer; print('OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Módulos MCP importáveis")
        else:
            print(f"❌ Erro ao importar módulos: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de importação: {e}")
        return False
    
    return True

def test_mcp_servers_startup():
    """Testa se consegue iniciar um servidor MCP"""
    print("\n🚀 Testando inicialização de servidor MCP")
    
    # Testar apenas o servidor de memória (mais simples)
    try:
        cmd = [
            "python3", "-m", "src.integrations.mcp_memory_server"
        ]
        env = os.environ.copy()
        env["MCP_PORT"] = "4321"
        env["PYTHONPATH"] = os.getcwd()
        
        # Iniciar em background por 5 segundos
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        import time
        time.sleep(3)  # Aguardar inicialização
        
        if process.poll() is None:
            print("✅ Servidor MCP memory iniciou com sucesso")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Servidor MCP falhou ao iniciar")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar inicialização: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTE DE CONFIGURAÇÃO MCP VS CODE")
    print("=" * 60)
    
    tests = [
        ("Configuração VS Code", test_vscode_mcp_config),
        ("Ambiente Python", test_python_environment),
        ("Inicialização MCP", test_mcp_servers_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Configuração MCP VS Code está correta!")
        print("\n📝 Próximos passos:")
        print("1. Reinicie o VS Code completamente")
        print("2. Abra o projeto")
        print("3. Teste: Ctrl+Shift+P → 'MCP: Show Server Status'")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} teste(s) falharam")
        print("🔧 Corrija os problemas acima antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())