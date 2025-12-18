#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║         OMNIMIND MCP REAL-TIME MONITORING - Live Connection Monitor       ║
# ║  Creator: GitHub Copilot                                                  ║
# ║  Purpose: Monitor MCP connections, health, and performance in real-time   ║
# ║  Date: 18 de Dezembro de 2025                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
declare -A MCP_PORTS=(
    [Filesystem]=4331
    [Git]=4332
    [Python]=4333
    [SQLite]=4334
    [System-Info]=4335
    [Logging]=4336
    [Supabase]=4337
)

REFRESH_INTERVAL=2
COLUMNS=120

# ════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

clear_screen() {
    clear
    tput civis  # Hide cursor
}

show_cursor() {
    tput cnorm  # Show cursor
}

# Trap to show cursor on exit
trap show_cursor EXIT

get_process_info() {
    local port=$1
    local name=$2

    # Check if port is listening
    local pid=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null || echo "")

    if [ -z "$pid" ]; then
        echo "DOWN"
        return 1
    fi

    # Get process info
    local rss=$(ps -p "$pid" -o rss= 2>/dev/null | tr -d ' ' || echo "0")
    local cpu=$(ps -p "$pid" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
    local elapsed=$(ps -p "$pid" -o etime= 2>/dev/null || echo "0")

    # Test connectivity
    local response_time=$(curl -s --connect-timeout 1 --max-time 1 -w "%{time_total}" -o /dev/null \
        "http://127.0.0.1:$port/mcp" \
        -X POST \
        -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' 2>/dev/null || echo "timeout")

    local status="UP"
    if [ "$response_time" = "timeout" ]; then
        status="SLOW"
    fi

    printf "%-15s %5s %6s %8s %8s" "$name" "$status" "$cpu" "$rss" "$elapsed"
}

show_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  OMNIMIND MCP REAL-TIME MONITOR - Live Connection Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
}

show_mcp_table() {
    echo -e "${CYAN}📡 MCP Status:${NC}"
    echo ""
    printf "  %-15s %5s %6s %8s %8s\n" "MCP Name" "Status" "CPU%" "Memory" "Uptime"
    echo "  ──────────────────────────────────────────────────────"

    for name in "${!MCP_PORTS[@]}" | sort; do
        local port=${MCP_PORTS[$name]}
        local info=$(get_process_info "$port" "$name")

        # Determine color based on status
        if echo "$info" | grep -q "DOWN"; then
            echo -e "  ${RED}$info${NC}"
        elif echo "$info" | grep -q "SLOW"; then
            echo -e "  ${YELLOW}$info${NC}"
        else
            echo -e "  ${GREEN}$info${NC}"
        fi
    done
}

show_system_stats() {
    echo ""
    echo -e "${CYAN}💻 System Resources:${NC}"
    echo ""

    # Memory
    local mem_info=$(free -h | grep Mem)
    printf "  %-20s %s\n" "Memory:" "$mem_info"

    # Disk
    local disk_info=$(df -h / | tail -1 | awk '{printf "%s / %s (%s used)", $3, $2, $5}')
    printf "  %-20s %s\n" "Disk (/):" "$disk_info"

    # CPU Load
    local load=$(uptime | awk -F'load average:' '{print $2}')
    printf "  %-20s %s\n" "Load Average:" "$load"

    # Network
    local connections=$(netstat -an 2>/dev/null | grep -c ESTABLISHED || echo "0")
    printf "  %-20s %s connections\n" "Active Connections:" "$connections"
}

show_quick_stats() {
    echo ""
    echo -e "${CYAN}📊 MCP Statistics:${NC}"
    echo ""

    local total=0
    local up=0
    local down=0
    local slow=0

    for name in "${!MCP_PORTS[@]}"; do
        local port=${MCP_PORTS[$name]}
        local info=$(get_process_info "$port" "$name")
        ((total++))

        if echo "$info" | grep -q "DOWN"; then
            ((down++))
        elif echo "$info" | grep -q "SLOW"; then
            ((slow++))
        else
            ((up++))
        fi
    done

    local pct=$((up * 100 / total))
    printf "  %-20s %d / %d (${pct}%%)\n" "MCPs Online:" "$up" "$total"
    printf "  %-20s %d\n" "MCPs Slow:" "$slow"
    printf "  %-20s %d\n" "MCPs Down:" "$down"
}

show_help() {
    echo ""
    echo -e "${CYAN}🎮 Controls:${NC}"
    echo ""
    echo "  h - Show this help"
    echo "  q - Quit"
    echo "  r - Reset"
    echo ""
}

show_diagnostics() {
    echo ""
    echo -e "${CYAN}🔧 Diagnostics:${NC}"
    echo ""

    local ports_open=0
    for name in "${!MCP_PORTS[@]}"; do
        local port=${MCP_PORTS[$name]}
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            ((ports_open++))
        fi
    done

    printf "  %-30s %d/7\n" "Ports listening:" "$ports_open"

    # Check Python processes
    local python_procs=$(pgrep -f "mcp_.*_server|mcp_.*_wrapper" | wc -l || echo "0")
    printf "  %-30s %d\n" "Python MCP processes:" "$python_procs"

    # Check for errors in logs
    local errors=$(grep -r "ERROR\|CRITICAL" /tmp/mcp_*.log 2>/dev/null | wc -l || echo "0")
    printf "  %-30s %d\n" "Errors in logs:" "$errors"
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN SCRIPT
# ════════════════════════════════════════════════════════════════════════════

clear_screen

# Initial display
show_header
show_mcp_table
show_system_stats
show_quick_stats
show_diagnostics
show_help

echo -e "${YELLOW}Press 'q' to quit, 'h' for help, 'r' to refresh...${NC}"
echo ""

# Real-time monitoring loop
while true; do
    # Check for user input (non-blocking)
    if read -t 0.1 -n 1 key 2>/dev/null; then
        case "$key" in
            q|Q)
                echo ""
                echo -e "${YELLOW}Exiting monitor...${NC}"
                exit 0
                ;;
            h|H)
                clear_screen
                show_header
                show_mcp_table
                show_system_stats
                show_quick_stats
                show_diagnostics
                show_help
                ;;
            r|R)
                clear_screen
                show_header
                show_mcp_table
                show_system_stats
                show_quick_stats
                show_diagnostics
                ;;
        esac
    fi

    # Refresh display every REFRESH_INTERVAL seconds
    sleep "$REFRESH_INTERVAL"
    clear_screen
    show_header
    show_mcp_table
    show_system_stats
    show_quick_stats
    show_diagnostics
    echo -e "${YELLOW}Press 'q' to quit, 'h' for help, 'r' to refresh...${NC}"
done
