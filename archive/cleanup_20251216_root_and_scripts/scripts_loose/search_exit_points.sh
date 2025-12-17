#!/bin/bash

# 🔎 SEARCH FOR ALL EXIT POINTS IN THE CODE
# Procura por qualquer coisa que pode fazer o script parar

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
cd "$PROJECT_ROOT"

echo "🔍 SEARCHING FOR EXIT TRIGGERS..."
echo "=========================================="
echo ""

# 1. Search for sys.exit() calls
echo "1️⃣  sys.exit() calls:"
echo "─────────────────────────"
grep -rn "sys.exit\|os._exit\|exit()" src/ \
  --include="*.py" \
  | grep -v "test_" \
  | grep -v "#.*exit" \
  | head -20

echo ""

# 2. Search for raise SystemExit
echo "2️⃣  raise SystemExit:"
echo "─────────────────────────"
grep -rn "raise SystemExit" src/ --include="*.py" | head -20

echo ""

# 3. Search for break statements in loops
echo "3️⃣  break statements (potential cycle stops):"
echo "─────────────────────────"
grep -rn "break" src/consciousness/integration_loop.py --include="*.py" | head -20

echo ""

# 4. Search for return statements in critical paths
echo "4️⃣  return statements in execute_cycle_sync():"
echo "─────────────────────────"
sed -n '464,530p' src/consciousness/integration_loop.py | grep -n "return\|break"

echo ""

# 5. Search for cycle limits or max checks
echo "5️⃣  Cycle limits or max checks:"
echo "─────────────────────────"
grep -rn "max.*cycle\|cycle.*max\|>.*50\|>=.*50\|cycle.*==.*15\|cycle.*==.*30" src/ --include="*.py" | head -20

echo ""

# 6. Search for memory/resource thresholds
echo "6️⃣  Memory/resource thresholds that could stop cycles:"
echo "─────────────────────────"
grep -rn "memory.*exit\|threshold.*exit\|limit.*exit" src/ --include="*.py" | head -20

echo ""

# 7. Search in scripts
echo "7️⃣  Exit/break in QUICK_FIX_STEP3.sh:"
echo "─────────────────────────"
grep -n "exit\|break\|return" scripts/recovery/QUICK_FIX_STEP3.sh | head -20

echo ""

# 8. Search for "Terminado" string
echo "8️⃣  'Terminado' string location:"
echo "─────────────────────────"
grep -rn "Terminado\|terminado\|TERMINADO" . --include="*.py" 2>/dev/null | grep -v ".git" | head -20

echo ""

# 9. Check if there's a hard limit in integration_loop.py
echo "9️⃣  Hard-coded numbers around 15-30 in integration_loop.py:"
echo "─────────────────────────"
grep -n "\b15\b\|\b16\b\|\b17\b\|\b25\b\|\b30\b\|\b31\b\|\b32\b" src/consciousness/integration_loop.py | head -20

echo ""

# 10. Search for any daemon/background exit
echo "🔟  Daemon-related exit calls:"
echo "─────────────────────────"
grep -rn "daemon.*exit\|background.*exit" src/ --include="*.py" | head -20

echo ""
echo "=========================================="
echo "✅ Search complete"
