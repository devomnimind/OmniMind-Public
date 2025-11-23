# 🚨 Troubleshooting - Problemas Comuns e Soluções

**Data:** 23 de novembro de 2025
**Status:** ✅ VALIDADO

---

## 📋 Índice de Problemas

1. [Serviço não inicia](#serviço-não-inicia)
2. [Portas já em uso](#portas-já-em-uso)
3. [Erro de build Docker](#erro-de-build-docker)
4. [Dependências não resolvidas](#dependências-não-resolvidas)
5. [Problemas de permissão](#problemas-de-permissão)
6. [Logs de erro](#logs-de-erro)
7. [Problemas de rede](#problemas-de-rede)

---

## 🔧 Serviço não inicia

### Sintomas
```
● omnimind-backend.service - OmniMind Backend API
     Loaded: loaded
     Active: failed (Result: exit-code)
```

### Diagnóstico
```bash
# Verificar status detalhado
sudo systemctl status omnimind-backend --no-pager -l

# Verificar logs
sudo journalctl -u omnimind-backend --no-pager -n 50
```

### Soluções

#### Solução 1: Dependências não atendidas
```bash
# Verificar se Qdrant está rodando
sudo systemctl status omnimind-qdrant

# Iniciar dependências primeiro
sudo systemctl start omnimind-qdrant
sudo systemctl start omnimind-backend
```

#### Solução 2: Arquivo .env ausente
```bash
# Verificar se .env existe
ls -la .env

# Criar .env se necessário
cp .env.template .env
# Editar variáveis necessárias
```

#### Solução 3: Recarregar systemd
```bash
# Recarregar configurações
sudo systemctl daemon-reload

# Reiniciar serviço
sudo systemctl restart omnimind-backend
```

---

## 🔌 Portas já em uso

### Sintomas
```
Error response from daemon: driver failed programming external connectivity on endpoint deploy-backend-1: Bind for 0.0.0.0:8000 failed: port is already allocated
```

### Diagnóstico
```bash
# Verificar portas em uso
sudo netstat -tlnp | grep -E ':(3000|8000|6333|6379)'

# Verificar containers Docker
docker ps | grep omnimind
```

### Soluções

#### Solução 1: Parar containers antigos
```bash
# Parar containers específicos
docker stop omnimind-backend-1 omnimind-frontend-1 omnimind-qdrant-1

# Ou parar todos os containers omnimind
docker stop $(docker ps -q --filter "name=omnimind")

# Remover containers parados
docker container prune -f
```

#### Solução 2: Alterar portas (se necessário)
```bash
# Editar docker-compose.yml para usar portas diferentes
# Exemplo: alterar 8000 para 8001
vim deploy/docker-compose.yml
```

#### Solução 3: Limpar completamente
```bash
# Parar todos os serviços
sudo systemctl stop omnimind-*

# Remover containers e volumes
docker-compose -f deploy/docker-compose.yml down -v

# Limpar imagens não utilizadas
docker image prune -f
```

---

## 🐳 Erro de build Docker

### Sintomas
```
ERROR: build path /home/fahbrain/projects/omnimind/deploy/web either does not exist, name is not a directory, or there are no files to build from there
```

### Diagnóstico
```bash
# Verificar estrutura de arquivos
ls -la deploy/
ls -la web/backend/
ls -la web/frontend/

# Verificar docker-compose.yml
cat deploy/docker-compose.yml | grep -A 5 "build:"
```

### Soluções

#### Solução 1: Corrigir contexto de build
```bash
# No docker-compose.yml, alterar:
# DE: context: .
# PARA: context: ..

# E verificar caminhos dos Dockerfiles
# DE: dockerfile: web/backend/Dockerfile
# PARA: dockerfile: web/backend/Dockerfile (já correto com context: ..)
```

#### Solução 2: Reconstruir imagens
```bash
# Limpar cache de build
docker system prune -f

# Reconstruir imagens
docker-compose -f deploy/docker-compose.yml build --no-cache

# Reiniciar serviços
sudo systemctl restart omnimind-backend
```

#### Solução 3: Verificar arquivos Dockerfile
```bash
# Verificar se Dockerfiles existem
ls -la web/backend/Dockerfile
ls -la web/frontend/Dockerfile

# Verificar sintaxe
docker build --dry-run -f web/backend/Dockerfile .
```

---

## 🔗 Dependências não resolvidas

### Sintomas
```
● omnimind-backend.service - Failed to start
Dependency omnimind-qdrant.service failed to start
```

### Diagnóstico
```bash
# Verificar status das dependências
sudo systemctl status omnimind-qdrant
sudo systemctl status omnimind-backend

# Verificar ordem de inicialização
sudo systemctl list-dependencies omnimind-backend
```

### Soluções

#### Solução 1: Iniciar na ordem correta
```bash
# Ordem recomendada:
sudo systemctl start omnimind-qdrant
sudo systemctl start omnimind-backend
sudo systemctl start omnimind-frontend
sudo systemctl start omnimind-mcp
```

#### Solução 2: Verificar arquivos .service
```bash
# Verificar dependências no arquivo .service
cat /etc/systemd/system/omnimind-backend.service | grep -E "(Requires|After)"

# Deve conter:
# Requires=omnimind-qdrant.service
# After=omnimind-qdrant.service
```

#### Solução 3: Reiniciar todos os serviços
```bash
# Parar tudo
sudo systemctl stop omnimind-*

# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar tudo
sudo systemctl start omnimind-*
```

---

## 🔑 Problemas de permissão

### Sintomas
```
Failed to start omnimind-backend.service: Permission denied
```

### Diagnóstico
```bash
# Verificar permissões dos arquivos
ls -la install/systemd/*.service
ls -la install/scripts/*.sh

# Verificar usuário do serviço
cat /etc/systemd/system/omnimind-backend.service | grep User
```

### Soluções

#### Solução 1: Corrigir permissões
```bash
# Tornar scripts executáveis
chmod +x install/scripts/*.sh

# Verificar permissões
ls -la install/scripts/
```

#### Solução 2: Executar como root
```bash
# Verificar se o serviço roda como root
cat /etc/systemd/system/omnimind-backend.service | grep "User=root"

# Se não, adicionar:
# User=root
```

#### Solução 3: Verificar sudo
```bash
# Testar sudo
sudo -v

# Se falhar, verificar configuração sudo
sudo visudo
```

---

## 📜 Logs de erro

### Como ler logs

```bash
# Logs em tempo real
sudo journalctl -u omnimind-backend -f

# Últimas 100 linhas
sudo journalctl -u omnimind-backend --no-pager -n 100

# Logs de todos os serviços
sudo journalctl -u omnimind-* --no-pager --since "1 hour ago"

# Logs com prioridade error
sudo journalctl -u omnimind-backend --no-pager -p err
```

### Erros comuns nos logs

#### Erro: "No such file or directory"
```
Caused by: java.io.FileNotFoundException: /home/fahbrain/projects/omnimind/.env (No such file or directory)
```
**Solução:** Criar arquivo `.env` a partir do template

#### Erro: "Connection refused"
```
ConnectionError: HTTPConnectionPool(host='qdrant', port=6333): Max retries exceeded with url: /collections
```
**Solução:** Verificar se Qdrant está rodando e acessível

#### Erro: "Build failed"
```
ERROR: Service 'backend' failed to build
```
**Solução:** Verificar Dockerfile e contexto de build

---

## 🌐 Problemas de rede

### Sintomas
```
ConnectionError: HTTPConnectionPool(host='backend', port=8000): Max retries exceeded
```

### Diagnóstico
```bash
# Verificar conectividade
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:6333/collections

# Verificar rede Docker
docker network ls
docker network inspect deploy_default
```

### Soluções

#### Solução 1: Verificar rede Docker
```bash
# Listar containers na rede
docker network inspect deploy_default | grep -A 5 "Containers"

# Verificar se todos os containers estão na mesma rede
docker ps --format "table {{.Names}}\t{{.Networks}}"
```

#### Solução 2: Reiniciar rede
```bash
# Parar serviços
sudo systemctl stop omnimind-*

# Remover rede
docker network rm deploy_default

# Reiniciar serviços (recria rede)
sudo systemctl start omnimind-*
```

#### Solução 3: Verificar configuração de rede no docker-compose.yml
```bash
# Verificar se todos os serviços estão na mesma rede
cat deploy/docker-compose.yml | grep -A 10 "networks:"
```

---

## 🆘 Comando de Recuperação Total

Se tudo falhar, use este comando para reset completo:

```bash
# PARAR TUDO
sudo systemctl stop omnimind-*
docker stop $(docker ps -q --filter "name=omnimind")

# LIMPAR
docker-compose -f deploy/docker-compose.yml down -v
docker system prune -f
sudo systemctl disable omnimind-*

# REINSTALAR
./install/scripts/install_systemd.sh
sudo systemctl start omnimind-*

# VALIDAR
sudo systemctl status omnimind-*
curl http://localhost:8000/health
```

---

## 📞 Quando pedir ajuda

Ao reportar problemas, inclua:

```bash
# Informações do sistema
uname -a
docker --version
docker-compose --version

# Status dos serviços
sudo systemctl status omnimind-*

# Logs recentes
sudo journalctl -u omnimind-backend --no-pager -n 20

# Configuração
cat /etc/systemd/system/omnimind-backend.service
```

---

**✅ GUIA DE TROUBLESHOOTING COMPLETO E VALIDADO**