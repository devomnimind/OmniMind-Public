# OmniMind Code Signing System

## Overview

This directory contains tools for cryptographically signing Python modules with developer credentials. The signing system:

- ✅ **Secure**: Credentials stored only in environment variables, never hardcoded
- ✅ **Non-destructive**: Signatures are added as comments, don't affect code execution
- ✅ **Reversible**: Can be removed without modifying actual code
- ✅ **Auditable**: Every signature includes author, timestamp, and content hash
- ✅ **Verifiable**: Signatures can be validated to ensure authenticity

## Quick Start

### 1. Setup Credentials

```bash
cd /home/fahbrain/projects/omnimind
source scripts/code_signing/setup_code_signing.sh
```

This will:
- Prompt for your credentials (name, email, Lattes URL)
- Set environment variables
- Optionally sign all modules in `src/`

### 2. Sign Modules Manually

```bash
export OMNIMIND_AUTHOR_NAME="Fabrício da Silva"
export OMNIMIND_AUTHOR_EMAIL="fabricioslv@hotmail.com.br"
export OMNIMIND_AUTHOR_LATTES="https://lattes.cnpq.br/3571784975796376"

python scripts/code_signing/sign_modules.py
```

### 3. Dry-Run (Recommended)

Always test first:

```bash
python scripts/code_signing/sign_modules.py --dry-run
```

## Commands

### Sign Modules

```bash
# Sign all modules in src/
python scripts/code_signing/sign_modules.py

# Dry-run (no changes)
python scripts/code_signing/sign_modules.py --dry-run

# Sign specific directory
python scripts/code_signing/sign_modules.py --module-path src/consciousness
```

### Verify Signatures

```bash
python scripts/code_signing/sign_modules.py --verify
```

Output example:
```
✓ Valid: src/consciousness/novelty_generator.py (by Fabrício da Silva)
✓ Valid: src/consciousness/qualia_engine.py (by Fabrício da Silva)
...
```

### Remove Signatures

```bash
python scripts/code_signing/unsign_modules.py

# Dry-run first
python scripts/code_signing/unsign_modules.py --dry-run
```

## How Signatures Work

### Signature Block Format

Each signed module gets a signature block added after its docstring:

```python
"""Module docstring."""

# ┌─ MODULE SIGNATURE
#
# Author: Fabrício da Silva
# Email: fabricioslv@hotmail.com.br
# Lattes: https://lattes.cnpq.br/3571784975796376
# Signed: 2025-11-29T12:00:00+00:00
#
# MODULE_SIGNATURE:a7f3d9c2e8b1f4a6d2c5e9b1a3d7f2e4c8b1d5a9e2f4c7a1d3e5b8c2f4a6d
#
# This module is cryptographically signed to verify authorship and
# integrity. The signature hash ensures that module metadata has not
# been tampered with. The module hash verifies content integrity.
#
# Verification:
# - Author: Check credentials against OMNIMIND_AUTHOR_NAME
# - Signature: Verify signature_hash matches module metadata
# - Content: Verify module_hash matches current content SHA-256
#
# └─ END MODULE SIGNATURE

# ... rest of module code ...
```

### What Gets Signed

- **Author Name**: Your full name (e.g., Fabrício da Silva)
- **Email**: Contact email (e.g., fabricioslv@hotmail.com.br)
- **Lattes URL**: Academic profile (optional)
- **Timestamp**: ISO 8601 UTC timestamp
- **Module Hash**: SHA-256 of module content (without signature)
- **Signature Hash**: SHA-256 of signature metadata

### Why Signatures Don't Affect Code

- Signature blocks are Python comments (`#` prefix)
- They're placed after module docstrings
- They don't interfere with imports or execution
- Signature removal doesn't change code behavior

## Environment Variables

Required:
- `OMNIMIND_AUTHOR_NAME`: Your full name
- `OMNIMIND_AUTHOR_EMAIL`: Your email address

Optional:
- `OMNIMIND_AUTHOR_LATTES`: Your Lattes URL (for Brazilian researchers)

## Security Model

### Threat Model

This system protects against:
- ✅ Accidental modifications to module authorship
- ✅ Attribution confusion (knowing who wrote what)
- ✅ Basic tamper detection (content hash changes)

This system does NOT protect against:
- ✗ Sophisticated attackers who can modify files and signatures
- ✗ Compromised development environment
- ✗ Leaked credentials

### Best Practices

1. **Never commit credentials** - Use environment variables
2. **Use SSH keys** - Sign git commits with GPG when pushing
3. **Verify before committing** - Run `--verify` before git commit
4. **Protect your environment** - Keep .env files secure
5. **Rotate credentials** - Change passwords regularly

## Reversibility

All signatures can be safely removed without affecting code:

```bash
python scripts/code_signing/unsign_modules.py

# Result: All signature blocks are removed, code unchanged
```

This is useful when:
- Re-signing with new credentials
- Updating author information
- Removing signatures from public releases (if desired)

## Integration with Git

### Sign Before Committing

```bash
# Setup credentials
source scripts/code_signing/setup_code_signing.sh

# Make changes to modules
echo "# new code" >> src/my_module.py

# Sign modules
python scripts/code_signing/sign_modules.py

# Verify
python scripts/code_signing/sign_modules.py --verify

# Commit
git add src/
git commit -m "feat: Add new feature and sign modules"
```

### Verify in CI/CD

In GitHub Actions or other CI/CD:

```yaml
- name: Verify code signatures
  run: python scripts/code_signing/sign_modules.py --verify
  env:
    OMNIMIND_AUTHOR_NAME: ${{ secrets.OMNIMIND_AUTHOR_NAME }}
    OMNIMIND_AUTHOR_EMAIL: ${{ secrets.OMNIMIND_AUTHOR_EMAIL }}
    OMNIMIND_AUTHOR_LATTES: ${{ secrets.OMNIMIND_AUTHOR_LATTES }}
```

## Troubleshooting

### "Missing credentials" Error

```
ValueError: Missing credentials. Set OMNIMIND_AUTHOR_NAME and OMNIMIND_AUTHOR_EMAIL
```

**Solution**: Set environment variables:

```bash
export OMNIMIND_AUTHOR_NAME="Your Name"
export OMNIMIND_AUTHOR_EMAIL="your.email@example.com"
```

### Signature Hash Mismatch

This happens if:
1. A signature was edited manually
2. File was modified incorrectly
3. Signature metadata changed

**Solution**: Re-sign the module:

```bash
python scripts/code_signing/unsign_modules.py --module-path src/path/to/module.py
python scripts/code_signing/sign_modules.py --module-path src/path/to/module.py
```

### Dry-Run Still Modifying Files

This should never happen. If it does, it's a bug. Report it with:

```bash
python scripts/code_signing/sign_modules.py --dry-run 2>&1 | tee dry_run_output.log
```

## Examples

### Example 1: Sign all modules

```bash
export OMNIMIND_AUTHOR_NAME="Fabrício da Silva"
export OMNIMIND_AUTHOR_EMAIL="fabricioslv@hotmail.com.br"

python scripts/code_signing/sign_modules.py
```

Output:
```
✓ Signed: src/consciousness/novelty_generator.py
✓ Signed: src/consciousness/qualia_engine.py
✓ Signed: src/metacognition/iit_metrics.py
...

SIGNING SUMMARY
===============
Total files found:  45
Files signed:       42
Files skipped:      3 (tests)
Files failed:       0

Setup complete!
```

### Example 2: Verify signatures

```bash
python scripts/code_signing/sign_modules.py --verify
```

Output:
```
✓ Valid: src/consciousness/novelty_generator.py (by Fabrício da Silva)
✓ Valid: src/consciousness/qualia_engine.py (by Fabrício da Silva)
✓ Valid: src/metacognition/iit_metrics.py (by Fabrício da Silva)
...

Verification complete: 42 valid, 0 invalid
```

### Example 3: Remove signatures

```bash
python scripts/code_signing/unsign_modules.py --dry-run

# Looks good?
python scripts/code_signing/unsign_modules.py
```

## References

- [Module Signature Dataclass](./sign_modules.py#L20)
- [CodeSigner Class](./sign_modules.py#L47)
- [AgentIdentity Integration](../src/identity/agent_signature.py)

## License

Part of OmniMind project. See LICENSE file.
