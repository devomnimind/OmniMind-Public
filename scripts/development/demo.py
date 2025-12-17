#!/usr/bin/env python3
"""
Demonstration Script - Code Signing in Action

Shows how the code signing system works with a test module.
Run from: /home/fahbrain/projects/omnimind
"""

import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from sign_modules import CodeSigner


def main() -> None:
    """Demonstrate code signing."""
    print("\n" + "=" * 70)
    print("CODE SIGNING DEMONSTRATION")
    print("=" * 70)

    # Setup credentials
    os.environ["OMNIMIND_AUTHOR_NAME"] = "Fabrício da Silva"
    os.environ["OMNIMIND_AUTHOR_EMAIL"] = "fabricioslv@hotmail.com.br"
    os.environ["OMNIMIND_AUTHOR_LATTES"] = "https://lattes.cnpq.br/3571784975796376"

    print("\n📋 Credentials configured:")
    print(f"  • Author: {os.environ['OMNIMIND_AUTHOR_NAME']}")
    print(f"  • Email:  {os.environ['OMNIMIND_AUTHOR_EMAIL']}")
    print(f"  • Lattes: {os.environ['OMNIMIND_AUTHOR_LATTES']}")

    # Create test file
    test_file = Path("/tmp/demo_module.py")
    original_content = '''"""
Demo module for code signing.

This shows how signatures are added.
"""

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
'''

    print("\n📝 Original module:")
    print("-" * 70)
    print(original_content)
    print("-" * 70)

    # Write test file
    test_file.write_text(original_content)

    # Sign it
    print("\n🔏 Signing module...")
    signer = CodeSigner(dry_run=False)

    if signer.sign_module(test_file):
        print("✓ Module signed successfully!")

        # Show signed content
        signed_content = test_file.read_text()
        print("\n📝 Signed module (notice signature block):")
        print("-" * 70)
        print(signed_content[:800] + "\n... (truncated) ...")
        print("-" * 70)

        # Count lines
        orig_lines = len(original_content.split("\n"))
        signed_lines = len(signed_content.split("\n"))
        print("\n📊 Module size:")
        print(f"  • Original:  {orig_lines} lines")
        print(f"  • Signed:    {signed_lines} lines")
        print(f"  • Added:     {signed_lines - orig_lines} lines (comments only)")

        # Verify
        print("\n🔍 Verifying signature...")
        result = signer.verify_module_signature(test_file)
        if result:
            print("✓ Signature verified!")
            print(f"  • Author:    {result['author']}")
            print(f"  • Email:     {result['email']}")
            print(f"  • Signed at: {result['signed_at']}")

        # Show it still works
        print("\n✅ Code still works (import and run):")
        print("-" * 70)

        # Execute the signed module
        exec_globals: dict = {}
        exec(signed_content, exec_globals)
        greet_func = exec_globals.get("greet")
        if greet_func:
            result_msg = greet_func("OmniMind")
            print("  >>> greet('OmniMind')")
            print(f"  '{result_msg}'")
        print("-" * 70)

        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)

        print("\n💡 Key takeaways:")
        print("  1. Signature is added as comments (doesn't affect execution)")
        print("  2. Module size increases slightly (signature metadata)")
        print("  3. Signed code still executes normally")
        print("  4. Signature can be verified to confirm authorship")
        print("  5. Signature can be removed without changing code")

        print("\n🚀 To sign all modules in your project:")
        print("\n  source scripts/code_signing/setup_code_signing.sh")
        print("\n  Or manually:")
        print("\n  export OMNIMIND_AUTHOR_NAME='Fabrício da Silva'")
        print("  export OMNIMIND_AUTHOR_EMAIL='fabricioslv@hotmail.com.br'")
        print("  python scripts/code_signing/sign_modules.py")

    else:
        print("✗ Failed to sign module")
        sys.exit(1)


if __name__ == "__main__":
    main()
