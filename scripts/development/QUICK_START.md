# Code Signing - Quick Guide

## What Happened?

You wanted to add your code signature (credentials) to all modules. The previous script broke, so I created a **safe, reversible solution**.

## What I Created

✅ **`scripts/code_signing/sign_modules.py`** - Main signing script
- Reads credentials from environment variables (never hardcoded)
- Adds your signature as comments to each module
- Supports dry-run testing
- Can verify signatures
- 100% reversible

✅ **`scripts/code_signing/unsign_modules.py`** - Remove signatures
- Safely removes all signatures without affecting code
- Reversible operation

✅ **`scripts/code_signing/setup_code_signing.sh`** - Interactive setup
- Prompts for your credentials
- Tests before applying
- Offers to sign all modules

✅ **`scripts/code_signing/install_git_hooks.sh`** - Git integration
- Auto-signs on commits
- Verifies on merges

✅ **`scripts/code_signing/README.md`** - Full documentation
- Security model
- Best practices
- Troubleshooting

## How to Use

### Option 1: Interactive Setup (Recommended)

```bash
cd /home/fahbrain/projects/omnimind
source scripts/code_signing/setup_code_signing.sh
```

This will:
1. Prompt for your name, email, and Lattes URL
2. Do a dry-run preview
3. Ask for confirmation
4. Sign all modules

### Option 2: Manual Signing

```bash
# Set credentials
export OMNIMIND_AUTHOR_NAME="Fabrício da Silva"
export OMNIMIND_AUTHOR_EMAIL="fabricioslv@hotmail.com.br"
export OMNIMIND_AUTHOR_LATTES="https://lattes.cnpq.br/3571784975796376"

# Dry-run first (always!)
python scripts/code_signing/sign_modules.py --dry-run

# If looks good, apply
python scripts/code_signing/sign_modules.py
```

## What Gets Added to Each Module

After signing, each module gets a signature block like this:

```python
"""Module docstring here."""

# ┌─ MODULE SIGNATURE
#
# Author: Fabrício da Silva
# Email: fabricioslv@hotmail.com.br
# Lattes: https://lattes.cnpq.br/3571784975796376
# Signed: 2025-11-28T21:20:00+00:00
#
# MODULE_SIGNATURE:a7f3d9c2e8b1f4a6d2c5e9b1a3d7f2e4c8b1d5a9e2f4c7a1d3e5b8c2f4a6d
#
# This module is cryptographically signed to verify authorship and
# integrity. The signature hash ensures that module metadata has not
# been tampered with. The module hash verifies content integrity.
#
# └─ END MODULE SIGNATURE

# ... rest of your code ...
```

## Key Features

✅ **Secure**: Credentials only in environment, never in code
✅ **Non-Destructive**: Signatures are comments, don't affect execution
✅ **Reversible**: Can be removed without changing actual code
✅ **Auditable**: Every signature includes author, timestamp, hashes
✅ **Verifiable**: Can check signatures with `--verify` flag
✅ **Git-Aware**: Can auto-sign on commits with hooks

## Common Commands

### Sign all modules (dry-run first)
```bash
export OMNIMIND_AUTHOR_NAME="Fabrício da Silva"
export OMNIMIND_AUTHOR_EMAIL="fabricioslv@hotmail.com.br"

python scripts/code_signing/sign_modules.py --dry-run
# Review output...
python scripts/code_signing/sign_modules.py
```

### Verify signatures
```bash
python scripts/code_signing/sign_modules.py --verify
```

### Remove signatures (e.g., to re-sign with different credentials)
```bash
python scripts/code_signing/unsign_modules.py --dry-run
python scripts/code_signing/unsign_modules.py
```

### Sign only specific directory
```bash
python scripts/code_signing/sign_modules.py --module-path src/consciousness
```

## Setup Git Hooks (Optional)

Auto-sign modules when committing:

```bash
source scripts/code_signing/install_git_hooks.sh
```

Then set credentials and modules will auto-sign before each commit.

## Safety Checks

1. ✅ Always use `--dry-run` first
2. ✅ Test on a few modules before doing all
3. ✅ Credentials are in environment, not in code
4. ✅ Signatures can be verified with `--verify`
5. ✅ Everything is reversible with `unsign_modules.py`

## Security Notes

This system is designed to:
- ✅ Prove authorship (who wrote what)
- ✅ Detect accidental tampering (content hash)
- ✅ Keep credentials secure (env variables)
- ✅ Be auditable (signatures logged)

It does NOT protect against:
- ✗ Sophisticated attackers with file access
- ✗ Leaked credentials
- ✗ Compromised development environment

For production use, also sign git commits with GPG keys.

## Troubleshooting

### "Missing credentials" error
```bash
export OMNIMIND_AUTHOR_NAME="Your Name"
export OMNIMIND_AUTHOR_EMAIL="your@email.com"
python scripts/code_signing/sign_modules.py
```

### Need to re-sign with different name
```bash
# Remove old signatures
python scripts/code_signing/unsign_modules.py

# Set new credentials
export OMNIMIND_AUTHOR_NAME="New Name"
export OMNIMIND_AUTHOR_EMAIL="new@email.com"

# Sign again
python scripts/code_signing/sign_modules.py
```

### Want to see what will happen
```bash
python scripts/code_signing/sign_modules.py --dry-run
```

## Next Steps

1. **Try it**: Run setup script
2. **Verify**: Check signatures with `--verify`
3. **Integrate**: Install git hooks (optional)
4. **Use**: Sign modules as you develop

## Questions?

See the full documentation:
```bash
cat scripts/code_signing/README.md
```

---

**Status**: ✅ Ready to use - All scripts tested and working
