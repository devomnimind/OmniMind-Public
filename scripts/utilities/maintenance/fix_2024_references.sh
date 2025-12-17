#!/usr/bin/env bash
# fix_2024_references.sh

echo "🔧 Corrigindo referências a 2024..."

# 1. temp_spaces/devbrain-inference/static/documentation.md
if [ -f temp_spaces/devbrain-inference/static/documentation.md ]; then
    sed -i 's/omnimind_archive_2024-11-24/omnimind_archive_2025-11-24/g' \
      temp_spaces/devbrain-inference/static/documentation.md
fi

# 2. tests/coevolution/test_bias_detector.py
if [ -f tests/coevolution/test_bias_detector.py ]; then
    sed -i 's/"2024-01-01"/"2025-01-01"/g' tests/coevolution/test_bias_detector.py
    sed -i 's/"2024-06-01"/"2025-06-01"/g' tests/coevolution/test_bias_detector.py
fi

# 3. tests/security/test_forensics_system.py
if [ -f tests/security/test_forensics_system.py ]; then
    sed -i 's/CVE-2024-1234/CVE-2025-1234/g' tests/security/test_forensics_system.py
fi

# 4. scripts/consolidation/autonomous_cleanup.py
if [ -f scripts/consolidation/autonomous_cleanup.py ]; then
    sed -i 's/AUDIT_CONSOLIDATION_2024-11-24/AUDIT_CONSOLIDATION_2025-11-24/g' \
      scripts/consolidation/autonomous_cleanup.py
fi

# 5. web/frontend/src/utils/formatters.ts
if [ -f web/frontend/src/utils/formatters.ts ]; then
    sed -i 's/@example formatRelativeTime("2024-01-01/@example formatRelativeTime("2025-01-01/g' \
      web/frontend/src/utils/formatters.ts
    sed -i 's/@example formatDate("2024-01-01/@example formatDate("2025-01-01/g' \
      web/frontend/src/utils/formatters.ts
fi

echo "✅ Correções concluídas!"
