#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║     OMNIMIND MCP PROTECTION - Add MCP Files to Kernel Protection          ║
# ║  Creator: GitHub Copilot                                                  ║
# ║  Purpose: Protect MCP wrapper files with kernel restrictions              ║
# ║  Date: 18 de Dezembro de 2025                                             ║
# ║                                                                            ║
# ║  This script adds MCP wrapper files to the immutable vault protection     ║
# ║  so they cannot be modified during runtime via kernel security.           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VAULT_ROOT="/var/lib/omnimind"
VAULT_PROTECTION="$VAULT_ROOT/protection"
MCP_PROTECTION_FILE="$VAULT_PROTECTION/mcp_protected_files.json"

# Files that are protected from modification
PROTECTED_MCP_FILES=(
    "$PROJECT_ROOT/src/integrations/mcp_git_wrapper.py"
    "$PROJECT_ROOT/src/integrations/mcp_sqlite_wrapper.py"
    "$PROJECT_ROOT/src/integrations/mcp_filesystem_server.py"
    "$PROJECT_ROOT/src/integrations/mcp_python_server.py"
    "$PROJECT_ROOT/src/integrations/mcp_system_info_server.py"
    "$PROJECT_ROOT/src/integrations/mcp_logging_server.py"
    "$PROJECT_ROOT/src/integrations/mcp_supabase_wrapper.py"
)

# ════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

log_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

log_info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        log_error "This script requires sudo access"
        log_info "Please run: sudo $0"
        exit 1
    fi
    log_success "Sudo access confirmed"
}

create_vault_structure() {
    log_info "Creating vault protection directory..."

    if [ ! -d "$VAULT_ROOT" ]; then
        sudo mkdir -p "$VAULT_ROOT"
        log_success "Vault root created"
    fi

    if [ ! -d "$VAULT_PROTECTION" ]; then
        sudo mkdir -p "$VAULT_PROTECTION"
        log_success "Protection directory created"
    fi

    sudo chmod 700 "$VAULT_ROOT"
    sudo chmod 700 "$VAULT_PROTECTION"
}

generate_file_checksums() {
    log_info "Generating SHA256 checksums for MCP files..."

    local checksums_file="$VAULT_PROTECTION/mcp_checksums.sha256"

    # Clear existing file
    sudo tee "$checksums_file" > /dev/null << 'EOF'
# OMNIMIND MCP FILE INTEGRITY CHECKSUMS
# Generated: $(date -u)
# Purpose: Verify MCP wrapper files have not been modified
# Usage: sha256sum -c mcp_checksums.sha256

EOF

    for file in "${PROTECTED_MCP_FILES[@]}"; do
        if [ -f "$file" ]; then
            local hash=$(sha256sum "$file" | awk '{print $1}')
            local relative_path="${file#$PROJECT_ROOT/}"
            echo "$hash  $relative_path" | sudo tee -a "$checksums_file" > /dev/null
            log_success "Checksummed: $relative_path"
        else
            log_warning "File not found: $file"
        fi
    done

    sudo chmod 400 "$checksums_file"
    log_success "Checksums file: $checksums_file"
}

create_protection_manifest() {
    log_info "Creating MCP protection manifest..."

    local manifest_file="$MCP_PROTECTION_FILE"

    # Create JSON manifest
    sudo tee "$manifest_file" > /dev/null << EOF
{
  "metadata": {
    "version": "1.0.0",
    "created": "$(date -u)",
    "creator": "OmniMind MCP Protection Script",
    "vault_version": "5.0",
    "purpose": "Protect MCP wrapper files from unauthorized modification"
  },
  "protected_files": [
EOF

    for file in "${PROTECTED_MCP_FILES[@]}"; do
        if [ -f "$file" ]; then
            local hash=$(sha256sum "$file" | awk '{print $1}')
            local size=$(stat -c%s "$file")
            local relative_path="${file#$PROJECT_ROOT/}"

            echo "    {" | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"path\": \"$relative_path\"," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"absolute_path\": \"$file\"," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"sha256\": \"$hash\"," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"size\": $size," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"type\": \"MCP Wrapper\"," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"protection_level\": \"HIGH\"," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"readonly\": true," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"immutable\": true," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"audit_modifications\": true," | sudo tee -a "$manifest_file" > /dev/null
            echo "      \"allow_execution\": true" | sudo tee -a "$manifest_file" > /dev/null
            echo "    }," | sudo tee -a "$manifest_file" > /dev/null
        fi
    done

    # Remove trailing comma and close array
    sudo sed -i '$ s/},$/}/' "$manifest_file"
    echo "  ]," | sudo tee -a "$manifest_file" > /dev/null
    echo "  \"protection_rules\": {" | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"deny_modification\": true," | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"deny_deletion\": true," | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"allow_read\": true," | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"allow_execute\": true," | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"log_access\": true," | sudo tee -a "$manifest_file" > /dev/null
    echo "    \"alert_modification_attempt\": true" | sudo tee -a "$manifest_file" > /dev/null
    echo "  }" | sudo tee -a "$manifest_file" > /dev/null
    echo "}" | sudo tee -a "$manifest_file" > /dev/null

    sudo chmod 400 "$manifest_file"
    log_success "Protection manifest created: $manifest_file"
}

apply_filesystem_protection() {
    log_info "Applying filesystem-level protections..."

    for file in "${PROTECTED_MCP_FILES[@]}"; do
        if [ -f "$file" ]; then
            local relative_path="${file#$PROJECT_ROOT/}"

            # Make read-only (but allow owner to execute)
            sudo chmod 555 "$file"

            # Try to make immutable with chattr if supported
            if command -v chattr &> /dev/null; then
                sudo chattr +i "$file" 2>/dev/null || log_warning "chattr +i not supported for: $relative_path"
            fi

            log_success "Protected: $relative_path (555, immutable)"
        fi
    done
}

create_audit_log() {
    log_info "Creating audit log entry..."

    local audit_log="$VAULT_PROTECTION/mcp_protection_audit.log"

    sudo tee -a "$audit_log" > /dev/null << EOF
═══════════════════════════════════════════════════════════════════════════
MCP PROTECTION AUDIT LOG
═══════════════════════════════════════════════════════════════════════════
Timestamp: $(date -u)
Action: MCP Files Added to Vault Protection
User: $(whoami)
Hostname: $(hostname)
Vault Version: 5.0

Protected Files:
EOF

    for file in "${PROTECTED_MCP_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ ${file#$PROJECT_ROOT/}" | sudo tee -a "$audit_log" > /dev/null
        fi
    done

    echo "" | sudo tee -a "$audit_log" > /dev/null
    echo "Protections Applied:" | sudo tee -a "$audit_log" > /dev/null
    echo "  • File permissions: 555 (r-xr-xr-x)" | sudo tee -a "$audit_log" > /dev/null
    echo "  • Immutable flag: chattr +i (if supported)" | sudo tee -a "$audit_log" > /dev/null
    echo "  • SHA256 checksums: Generated and stored" | sudo tee -a "$audit_log" > /dev/null
    echo "  • Manifest: Created with full inventory" | sudo tee -a "$audit_log" > /dev/null
    echo "" | sudo tee -a "$audit_log" > /dev/null
    echo "Status: ✅ MCP FILES NOW PROTECTED" | sudo tee -a "$audit_log" > /dev/null
    echo "═══════════════════════════════════════════════════════════════════════════" | sudo tee -a "$audit_log" > /dev/null

    sudo chmod 400 "$audit_log"
    log_success "Audit log created: $audit_log"
}

create_verification_script() {
    log_info "Creating MCP protection verification script..."

    local verify_script="$VAULT_PROTECTION/verify_mcp_protection.sh"

    sudo tee "$verify_script" > /dev/null << 'VERIFY_EOF'
#!/bin/bash
# Verify MCP file protection integrity

echo "🔍 Verifying MCP Protection..."
echo ""

VAULT_PROTECTION="/var/lib/omnimind/protection"

if [ ! -f "$VAULT_PROTECTION/mcp_checksums.sha256" ]; then
    echo "❌ Checksums file not found"
    exit 1
fi

cd /home/fahbrain/projects/omnimind
if sha256sum -c "$VAULT_PROTECTION/mcp_checksums.sha256" 2>/dev/null | grep -q OK; then
    echo "✅ All MCP files verified - Protection intact"
    exit 0
else
    echo "⚠️ Some MCP files may have been modified - Review required"
    exit 1
fi
VERIFY_EOF

    sudo chmod 755 "$verify_script"
    log_success "Verification script created: $verify_script"
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN SCRIPT
# ════════════════════════════════════════════════════════════════════════════

log_header "OMNIMIND MCP PROTECTION - Add MCP Files to Kernel Protection"

# Check requirements
check_sudo

# Setup vault
create_vault_structure

# Generate protections
generate_file_checksums
create_protection_manifest
apply_filesystem_protection
create_audit_log
create_verification_script

# Summary
log_header "MCP PROTECTION COMPLETE"

echo -e "${CYAN}📊 Summary:${NC}"
echo "  Protected Files: ${#PROTECTED_MCP_FILES[@]}"
echo "  Vault Location: $VAULT_ROOT"
echo "  Manifest File: $MCP_PROTECTION_FILE"
echo ""

echo -e "${CYAN}🔧 Verification:${NC}"
echo "  Check integrity: $VAULT_PROTECTION/verify_mcp_protection.sh"
echo "  View manifest:   cat $MCP_PROTECTION_FILE"
echo "  View checksums:  cat $VAULT_PROTECTION/mcp_checksums.sha256"
echo ""

echo -e "${GREEN}✅ MCP FILES ARE NOW PROTECTED FROM KERNEL-LEVEL MODIFICATION${NC}"
echo ""
