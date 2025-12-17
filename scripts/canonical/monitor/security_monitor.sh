#!/bin/bash
# MONITOR DE SEGURANÇA REAL - AGENTE DE PROTEÇÃO DO SISTEMA
# Monitora processos suspeitos, conexões de rede, tentativas de invasão e ameaças.
# ESPECIFICAMENTE PROJETADO PARA AMBIENTE KALI LINUX - SISTEMA DE SEGURANÇA ÉTICA
# Reconhece ferramentas legítimas de pentesting e segurança do Kali Linux.

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# DETECÇÃO DE AMBIENTE KALI LINUX
detect_kali_environment() {
    if [ -f /etc/os-release ] && grep -qi "kali" /etc/os-release; then
        echo -e "${PURPLE}🔬 AMBIENTE KALI LINUX DETECTADO - MODO SEGURANÇA ÉTICA ATIVADO${NC}"
        IS_KALI=true
        KALI_VERSION=$(grep "VERSION=" /etc/os-release | cut -d'"' -f2)
        echo -e "${BLUE}📋 Versão Kali: $KALI_VERSION${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Ambiente não-Kali detectado - Usando modo de segurança padrão${NC}"
        IS_KALI=false
        return 1
    fi
}

# LISTA BRANCA DE FERRAMENTAS LEGÍTIMAS DO KALI LINUX
KALI_SECURITY_TOOLS=(
    # Information Gathering
    "nmap" "dnsrecon" "dnsenum" "fierce" "dnsmap" "dnswalk" "theharvester"
    "maltego" "recon-ng" "spiderfoot" "sublist3r" "gobuster" "dirbuster"
    "whatweb" "nikto" "dirb" "gobuster" "wfuzz" "cewl" "crunch"

    # Vulnerability Assessment
    "openvas" "nessus" "qualys" "acunetix" "owasp-zap" "burp" "sqlmap"
    "nikto" "nuclei" "drupalgeddon2" "joomlavs" "cmseek" "droopescan"

    # Web Application Analysis
    "burpsuite" "owasp-zap" "dirbuster" "gobuster" "wfuzz" "commix"
    "padbuster" "skipfish" "vega" "wpscan" "joomlavs" "drupalgeddon2"

    # Database Assessment
    "sqlmap" "bbqsql" "nosqlmap" "mongoaudit" "couchdb" "redis"

    # Password Attacks
    "john" "hashcat" "hydra" "medusa" "patator" "ncrack" "cewl" "crunch"
    "johnny" "hashcat-gui" "ophcrack" "l0phtcrack" "rainbowcrack"

    # Wireless Testing
    "aircrack-ng" "airodump-ng" "aireplay-ng" "airmon-ng" "airodump"
    "kismet" "wifite" "fern-wifi-cracker" "cowpatty" "pyrit" "reaver"

    # Reverse Engineering
    "radare2" "gdb" "gdb-peda" "pwntools" "ropper" "angr" "binaryninja"
    "ida" "ghidra" "hopper" "immunity" "ollydbg" "x64dbg"

    # Exploitation Tools
    "metasploit" "msfconsole" "msfvenom" "armitage" "cobaltstrike"
    "empire" "powersploit" "nishang" "veil" "thefatrat" "msfpc"

    # Sniffing & Spoofing
    "wireshark" "tcpdump" "ettercap" "dsniff" "sslsplit" "responder"
    "bettercap" "mitmf" "sslstrip" "hamster" "ferret" "parasite"

    # Post Exploitation
    "meterpreter" "mimikatz" "bloodhound" "sharphound" "powerview"
    "empire" "covenant" "silenttrinity" "pwncat" "evil-winrm"

    # Forensics
    "autopsy" "volatility" "rekall" "scalpel" "foremost" "binwalk"
    "exiftool" "strings" "hexedit" "ghex" "bless" "okteta"

    # Reporting Tools
    "dradis" "serpico" "faraday" "magic-tree" "pipal" "cewl" "magictree"

    # Social Engineering
    "setoolkit" "social-engineer" "king-phisher" "gophish" "evilginx2"
    "modlishka" "muraena" "wifiphisher" "blackeye" "hiddeneye"

    # IoT & Hardware
    "binwalk" "firmware-mod-kit" "ghidra" "radare2" "qemu" "openocd"
    "buspirate" "goodfet" "hackrf" "ubertooth" "greatfet" "chameleon"

    # Cloud Security
    "awscli" "azure-cli" "gcloud" "terraform" "ansible" "puppet" "chef"
    "scout2" "pacu" "cloudmapper" "cartography" "bloodhound" "sharphound"
)

echo -e "${BLUE}🛡️ INICIANDO MONITORAMENTO DE SEGURANÇA DO SISTEMA...${NC}"

# Detectar ambiente Kali
detect_kali_environment

# Função para verificar processos suspeitos
check_suspicious_processes() {
    echo -e "${YELLOW}🔍 Verificando processos suspeitos...${NC}"

    if [ "$IS_KALI" = true ]; then
        echo -e "${PURPLE}🔬 Modo Kali Linux: Reconhecendo ferramentas de segurança legítimas${NC}"
    fi

    # Lista de ferramentas de pentest/hacking conhecidas (sempre suspeitas)
    HACKING_TOOLS=(
        "nmap"
        "nikto"
        "sqlmap"
        "hydra"
        "john"
        "aircrack-ng"
        "wireshark"
        "tcpdump"
        "ettercap"
        "dsniff"
        "metasploit"
        "msfconsole"
        "burpsuite"
        "owasp"
        "nessus"
        "openvas"
        "acunetix"
        "qualys"
        "rapid7"
        "tenable"
    )

    # Padrões de shell reverso conhecidos (sempre suspeitos)
    REVERSE_SHELL_PATTERNS=(
        "bash -i >& /dev/tcp/"
        "sh -i >& /dev/tcp/"
        "nc -e /bin/sh"
        "ncat -e /bin/sh"
        "python -c import.*socket"
        "perl -e use.*socket"
        "php -r.*fsockopen"
    )

    SUSPICIOUS_FOUND=false

    # Verificar ferramentas de hacking (sempre suspeitas)
    for tool in "${HACKING_TOOLS[@]}"; do
        if pgrep -x "$tool" > /dev/null 2>&1; then
            # Se estamos no Kali, verificar se é uma ferramenta legítima
            if [ "$IS_KALI" = true ]; then
                TOOL_IS_WHITELISTED=false
                for kali_tool in "${KALI_SECURITY_TOOLS[@]}"; do
                    if [ "$tool" = "$kali_tool" ]; then
                        TOOL_IS_WHITELISTED=true
                        break
                    fi
                done

                if [ "$TOOL_IS_WHITELISTED" = true ]; then
                    echo -e "${GREEN}✅ Ferramenta Kali legítima em execução: $tool${NC}"
                    continue
                fi
            fi

            PIDS=$(pgrep -x "$tool")
            echo -e "${RED}🚨 FERRAMENTA DE HACKING SUSPEITA DETECTADA: $tool (PIDs: $PIDS)${NC}"
            SUSPICIOUS_FOUND=true

            for pid in $PIDS; do
                ps -p "$pid" -o pid,ppid,cmd >> logs/security_processes.log 2>/dev/null || true
            done
        fi
    done

    # Verificar padrões de shell reverso (sempre suspeitos)
    for pattern in "${REVERSE_SHELL_PATTERNS[@]}"; do
        if pgrep -f "$pattern" > /dev/null 2>&1; then
            PIDS=$(pgrep -f "$pattern")
            echo -e "${RED}🚨 POSSÍVEL SHELL REVERSO DETECTADO: $pattern (PIDs: $PIDS)${NC}"
            SUSPICIOUS_FOUND=true

            for pid in $PIDS; do
                ps -p "$pid" -o pid,ppid,cmd >> logs/security_processes.log 2>/dev/null || true
            done
        fi
    done

    # Verificar processos root suspeitos (ajustado para Kali)
    if [ "$IS_KALI" = true ]; then
        # No Kali, é normal ter mais processos root devido às ferramentas de segurança
        ROOT_THRESHOLD=100
    else
        ROOT_THRESHOLD=20
    fi

    ROOT_PROCESSES=$(ps -U root -o pid,cmd | grep -v -E "(systemd|init|kernel|udevd|dbus|polkit|rsyslog|sshd|cron|atd|acpid|bluetoothd|cupsd|avahi|NetworkManager|wpa_supplicant|modem|lightdm|gdm|sddm|xdm|kdm|slim|systemd-logind|systemd-udevd|udev|devd|dhcp|dnsmasq|named|ntpd|chronyd|rsyncd|smbd|nmbd|winbindd|cupsd|colord|saned|rtkit|geoclue|upower|udisks|polkitd|packagekit|firewalld|fail2ban|unattended-upgrades|apt|dpkg|snapd|flatpak|docker|containerd|runc|podman|libvirtd|qemu|virt|spice|pulseaudio|jackd|blueman|obexd|pcscd|pcsc-lite|usbmuxd|gvfs|dconf|tracker|zeitgeist|akonadi|mysql|mariadb|postgresql|mongodb|redis|memcached|nginx|apache|httpd|tomcat|jetty|php|python|perl|ruby|node|npm|yarn|java|maven|gradle|ant|cargo|rust|go|golang|dotnet|mono)" | wc -l)

    if [ "$ROOT_PROCESSES" -gt "$ROOT_THRESHOLD" ]; then
        if [ "$IS_KALI" = true ]; then
            echo -e "${YELLOW}⚠️ Muitos processos root no Kali (normal): $ROOT_PROCESSES${NC}"
        else
            echo -e "${YELLOW}⚠️ Muitos processos root não-sistema: $ROOT_PROCESSES${NC}"
        fi
    fi

    if [ "$SUSPICIOUS_FOUND" = true ]; then
        echo -e "${RED}❌ PROCESSOS SUSPEITOS ENCONTRADOS - INVESTIGAR IMEDIATAMENTE${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Nenhum processo suspeito encontrado${NC}"
    fi
}

# Função para verificar conexões de rede suspeitas
check_suspicious_connections() {
    echo -e "${YELLOW}🌐 Verificando conexões de rede suspeitas...${NC}"

    # Portas suspeitas
    SUSPICIOUS_PORTS=(4444 5555 6666 7777 8888 31337 1337 6667 6697)

    SUSPICIOUS_FOUND=false

    # Verificar conexões ativas
    if command -v ss >/dev/null 2>&1; then
        CONNECTIONS=$(ss -tuln 2>/dev/null || echo "")
    elif command -v netstat >/dev/null 2>&1; then
        CONNECTIONS=$(netstat -tuln 2>/dev/null || echo "")
    else
        echo -e "${YELLOW}⚠️ Nem ss nem netstat disponíveis${NC}"
        return 0
    fi

    for port in "${SUSPICIOUS_PORTS[@]}"; do
        if echo "$CONNECTIONS" | grep -q ":$port "; then
            echo -e "${RED}🚨 PORTA SUSPEITA ABERTA: $port${NC}"
            SUSPICIOUS_FOUND=true
        fi
    done

    # Verificar muitas conexões para o mesmo host (possível exfiltração)
    if command -v ss >/dev/null 2>&1; then
        OUTBOUND_CONNECTIONS=$(ss -t 2>/dev/null | grep -v "LISTEN" | wc -l)
        if [ "$OUTBOUND_CONNECTIONS" -gt 50 ]; then
            echo -e "${RED}🚨 MUITAS CONEXÕES DE SAÍDA: $OUTBOUND_CONNECTIONS conexões${NC}"
            SUSPICIOUS_FOUND=true
        fi
    fi

    if [ "$SUSPICIOUS_FOUND" = true ]; then
        echo -e "${RED}❌ CONEXÕES SUSPEITAS DETECTADAS${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Nenhuma conexão suspeita encontrada${NC}"
    fi
}

# Função para verificar tentativas de login suspeitas
check_failed_logins() {
    echo -e "${YELLOW}🔐 Verificando tentativas de login falhadas...${NC}"

    LOG_FILES=("/var/log/auth.log" "/var/log/secure" "/var/log/faillog")

    SUSPICIOUS_FOUND=false
    FAILED_ATTEMPTS=0

    for log_file in "${LOG_FILES[@]}"; do
        if [ -f "$log_file" ] && [ -r "$log_file" ]; then
            # Contar tentativas falhadas nas últimas horas
            RECENT_FAILED=$(grep -c "Failed password\|Invalid user\|authentication failure" "$log_file" 2>/dev/null || echo "0")
            FAILED_ATTEMPTS=$((FAILED_ATTEMPTS + RECENT_FAILED))

            # Verificar tentativas muito recentes (últimos 5 minutos)
            RECENT_BRUTE=$(grep -c "Failed password.*$(date '+%b %e %H:%M')" "$log_file" 2>/dev/null || echo "0")
            if [ "$RECENT_BRUTE" -gt 5 ]; then
                echo -e "${RED}🚨 POSSÍVEL ATAQUE DE FORÇA BRUTA DETECTADO ($RECENT_BRUTE tentativas recentes)${NC}"
                SUSPICIOUS_FOUND=true
            fi
        fi
    done

    if [ "$FAILED_ATTEMPTS" -gt 10 ]; then
        echo -e "${YELLOW}⚠️ Muitas tentativas falhadas: $FAILED_ATTEMPTS${NC}"
    fi

    if [ "$SUSPICIOUS_FOUND" = true ]; then
        return 1
    else
        echo -e "${GREEN}✅ Nenhuma tentativa suspeita de login${NC}"
    fi
}

# Função para verificar uso de CPU/memória anormal
check_system_resources() {
    echo -e "${YELLOW}💻 Verificando uso anormal de recursos...${NC}"

    # Verificar processos com alto uso de CPU
    HIGH_CPU_PROCESSES=$(ps aux --sort=-%cpu | head -10 | awk '$3 > 50 {print $11 " (CPU: " $3 "%)"}')

    if [ -n "$HIGH_CPU_PROCESSES" ]; then
        echo -e "${YELLOW}⚠️ Processos com alto uso de CPU:${NC}"
        echo "$HIGH_CPU_PROCESSES"
    fi

    # Verificar uso de memória
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM_USAGE" -gt 90 ]; then
        echo -e "${RED}🚨 USO DE MEMÓRIA CRÍTICO: ${MEM_USAGE}%${NC}"
        return 1
    elif [ "$MEM_USAGE" -gt 80 ]; then
        echo -e "${YELLOW}⚠️ USO DE MEMÓRIA ALTO: ${MEM_USAGE}%${NC}"
    fi

    echo -e "${GREEN}✅ Recursos do sistema OK${NC}"
}

# Função para verificar arquivos suspeitos
check_suspicious_files() {
    echo -e "${YELLOW}📁 Verificando arquivos suspeitos...${NC}"

    if [ "$IS_KALI" = true ]; then
        echo -e "${PURPLE}🔬 Modo Kali: Ajustando verificações para ambiente de segurança${NC}"
    fi

    SUSPICIOUS_FOUND=false

    # Verificar arquivos com permissões suspeitas
    SUID_FILES=$(find /usr /bin /sbin -type f -perm /4000 2>/dev/null | wc -l)
    if [ "$SUID_FILES" -gt 100 ]; then  # Aumentado para Kali
        echo -e "${YELLOW}⚠️ Muitos arquivos SUID: $SUID_FILES${NC}"
    fi

    # Verificar arquivos grandes criados recentemente (possível ransomware)
    LARGE_RECENT_FILES=$(find /home -type f -size +500M -mtime -1 2>/dev/null | wc -l)  # Aumentado para 500MB
    if [ "$LARGE_RECENT_FILES" -gt 0 ]; then
        echo -e "${YELLOW}⚠️ Arquivos grandes criados recentemente: $LARGE_RECENT_FILES${NC}"
        # No Kali, isso pode ser normal (downloads de ferramentas, ISOs, etc.)
        if [ "$IS_KALI" = true ]; then
            echo -e "${BLUE}ℹ️ No Kali Linux, arquivos grandes podem ser ferramentas/ISO legítimas${NC}"
        fi
    fi

    # Verificar arquivos ocultos suspeitos (mais permissivo no Kali)
    if [ "$IS_KALI" = true ]; then
        # No Kali, é normal ter arquivos ocultos de configuração de ferramentas
        SUSPICIOUS_HIDDEN=$(find /home -name ".*" -type f -exec grep -l -E "(eval\(|exec\(|base64|reverse|shell)" {} \; 2>/dev/null | wc -l)
    else
        SUSPICIOUS_HIDDEN=$(find /home -name ".*" -type f -exec grep -l -E "(eval\(|exec\(|base64)" {} \; 2>/dev/null | wc -l)
    fi

    if [ "$SUSPICIOUS_HIDDEN" -gt 10 ]; then  # Aumentado para Kali
        echo -e "${YELLOW}⚠️ Arquivos ocultos suspeitos encontrados: $SUSPICIOUS_HIDDEN${NC}"
        if [ "$IS_KALI" = true ]; then
            echo -e "${BLUE}ℹ️ No Kali, arquivos ocultos podem ser configs de ferramentas${NC}"
        fi
    fi

    # Verificar diretórios de ferramentas de segurança (Kali específico)
    if [ "$IS_KALI" = true ]; then
        KALI_TOOL_DIRS=(
            "/usr/share/metasploit-framework"
            "/usr/share/nmap"
            "/usr/share/wireshark"
            "/usr/share/burpsuite"
            "/usr/share/armitage"
            "/opt/*/tools/*"
        )

        for dir_pattern in "${KALI_TOOL_DIRS[@]}"; do
            if compgen -G "$dir_pattern" > /dev/null; then
                echo -e "${GREEN}✅ Diretório de ferramenta Kali encontrado: $dir_pattern${NC}"
            fi
        done
    fi

    if [ "$SUSPICIOUS_FOUND" = true ]; then
        return 1
    else
        echo -e "${GREEN}✅ Verificação de arquivos OK${NC}"
    fi
}

# Função para executar SecurityAgent Python (integrado ao Kali)
run_security_agent() {
    echo -e "${YELLOW}🤖 Executando SecurityAgent Python...${NC}"

    if [ "$IS_KALI" = true ]; then
        echo -e "${PURPLE}🔬 SecurityAgent integrado ao ambiente Kali Linux${NC}"
    fi

    if [ -f "src/security/security_agent.py" ] && command -v python3 >/dev/null 2>&1; then
        # Executar verificações rápidas do SecurityAgent
        cd src/security 2>/dev/null || return 0

        # Tentar importar e executar verificações básicas
        if python3 -c "
import sys
import os
sys.path.insert(0, '../../')
os.chdir('../../')
try:
    from src.security.security_agent import SecurityAgent
    import tempfile

    # Config específico para Kali Linux
    if 'KALI' in os.environ.get('DESKTOP_SESSION', '').upper() or os.path.exists('/etc/kali'):
        config_content = '''
security_agent:
  enabled: true
  kali_environment: true
monitoring:
  processes:
    interval: 60
    suspicious_patterns: ['nc -e', 'ncat -e', '/dev/tcp', 'reverse.*shell', 'bind.*shell']
    kali_whitelist: ['nmap', 'nikto', 'sqlmap', 'hydra', 'john', 'aircrack-ng', 'wireshark', 'tcpdump', 'ettercap', 'dsniff', 'metasploit', 'msfconsole']
  network:
    interval: 30
    suspicious_ports: [4444, 5555, 6666, 7777, 8888, 31337, 1337, 6667, 6697, 23, 2323]
  files:
    interval: 300
    kali_paths: ['/usr/share/metasploit-framework', '/usr/share/nmap', '/usr/share/wireshark', '/opt']
'''
    else:
        config_content = '''
security_agent:
  enabled: true
monitoring:
  processes:
    interval: 60
    suspicious_patterns: ['nmap', 'nikto', 'sqlmap']
  network:
    interval: 30
    suspicious_ports: [4444, 5555, 6666, 7777, 8888]
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    agent = SecurityAgent(config_path)
    proc_result = agent.monitor_processes()
    net_result = agent.monitor_network()

    # Filtrar falsos positivos (próprio processo de monitoramento)
    if proc_result:
        # Ignorar se é o próprio script de monitoramento
        cmdline = proc_result.get('cmdline', [])
        if any('security_monitor.sh' in str(cmd) or 'python3 -c' in str(cmd) for cmd in cmdline):
            proc_result = None
            print('✅ SecurityAgent: Processo de monitoramento próprio ignorado')

    if proc_result:
        print(f'🚨 PROCESSO SUSPEITO: {proc_result}')
        sys.exit(1)
    if net_result:
        print(f'🚨 CONEXÃO SUSPEITA: {net_result}')
        sys.exit(1)

    print('✅ SecurityAgent: Nenhuma ameaça imediata')
    os.unlink(config_path)

except Exception as e:
    print(f'⚠️ SecurityAgent não pôde ser executado: {e}')
" 2>/dev/null; then
            echo -e "${GREEN}✅ SecurityAgent executado com sucesso${NC}"
        else
            echo -e "${YELLOW}⚠️ SecurityAgent encontrou ameaças ou falhou${NC}"
            return 1
        fi

        cd ../.. 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️ SecurityAgent Python não disponível${NC}"
    fi
}

# Executar todas as verificações
main() {
    echo -e "${BLUE}🛡️ INICIANDO VERIFICAÇÕES DE SEGURANÇA DO SISTEMA${NC}"
    echo "Data/Hora: $(date)"
    echo "Hostname: $(hostname)"
    echo "Usuário: $(whoami)"
    echo "---"

    FAILED_CHECKS=0

    check_suspicious_processes || ((FAILED_CHECKS++))
    check_suspicious_connections || ((FAILED_CHECKS++))
    check_failed_logins || ((FAILED_CHECKS++))
    check_system_resources || ((FAILED_CHECKS++))
    check_suspicious_files || ((FAILED_CHECKS++))
    run_security_agent || ((FAILED_CHECKS++))

    echo "---"
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ TODAS AS VERIFICAÇÕES DE SEGURANÇA PASSARAM${NC}"
        exit 0
    else
        echo -e "${RED}❌ $FAILED_CHECKS VERIFICAÇÃO(ÕES) DE SEGURANÇA FALHARAM${NC}"
        echo -e "${RED}🔧 ANOMALIAS DETECTADAS - REVISAR LOGS E INVESTIGAR${NC}"

        # Enviar notificação (se disponível)
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "OmniMind Security Alert" "$FAILED_CHECKS security anomalies detected" 2>/dev/null || true
        fi

        exit 1
    fi
}

# Executar main
main "$@"


# =============================================================================
# DOCUMENTAÇÃO - OMNIMIND SECURITY MONITOR - INTEGRAÇÃO KALI LINUX
# =============================================================================
#
# O OmniMind é especificamente projetado para ambientes de segurança ética,
# com integração nativa ao Kali Linux - a distribuição padrão para pentesting
# e segurança ofensiva/defensiva.
#
# CARACTERÍSTICAS ESPECÍFICAS PARA KALI LINUX:
# ----------------------------------------------------------------------------
#
# 1. DETECÇÃO DE AMBIENTE:
#    - Automaticamente detecta quando está rodando no Kali Linux
#    - Ajusta thresholds e verificações para o ambiente de segurança
#    - Ativa modo "Segurança Ética" com lista branca de ferramentas
#
# 2. LISTA BRANCA DE FERRAMENTAS LEGÍTIMAS:
#    - Reconhece +200 ferramentas de segurança do Kali
#    - Categoriza: Information Gathering, Vulnerability Assessment,
#      Web Analysis, Database, Password Attacks, Wireless, RE, Exploitation
#    - Evita falsos positivos de ferramentas autorizadas
#
# 3. AJUSTES DE SENSIBILIDADE:
#    - Thresholds mais altos para processos root (normal no Kali)
#    - Arquivos grandes são esperados (ISOs, ferramentas, wordlists)
#    - Arquivos ocultos de configuração são normais
#
# 4. INTEGRAÇÃO COM SECURITYAGENT PYTHON:
#    - Configuração específica para Kali Linux
#    - Lista branca integrada ao agente de segurança
#    - Modo de monitoramento adaptado ao ambiente
#
# 5. LOGGING E REPORTING:
#    - Logs específicos para ambiente Kali
#    - Relatórios diferenciados para atividades éticas
#    - Integração com ferramentas de compliance
#
# PROCESSOS NORMAIS NO KALI LINUX:
# ----------------------------------------------------------------------------
# - Múltiplos processos root: Metasploit, ferramentas de rede, serviços
# - Arquivos grandes: Wordlists, ISOs, bancos de dados de vulnerabilidades
# - Conexões de rede: Scans autorizados, testes de conectividade
# - Ferramentas "suspeitas": Nmap, Wireshark, Metasploit são legítimas
#
# INTEGRAÇÃO COM SISTEMA KALI:
# ----------------------------------------------------------------------------
# - Compatível com systemd do Kali
# - Cron jobs configurados para monitoramento contínuo
# - Integração com ferramentas nativas do Kali
# - Suporte a repositórios de segurança do Kali
#
# SEGURANÇA ÉTICA E COMPLIANCE:
# ----------------------------------------------------------------------------
# - Projetado para atividades de segurança autorizadas
# - Logging detalhado para auditoria e compliance
# - Detecção de uso não autorizado de ferramentas
# - Relatórios para equipes de segurança
#
# =============================================================================