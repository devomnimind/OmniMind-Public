#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Diagnóstico de Spaces no Hugging Face.
Lista Spaces, status e hardware.
"""
import os
from huggingface_hub import HfApi, get_token


def check_spaces():
    token = get_token()
    if not token:
        print("❌ No token found. Run 'huggingface-cli login' first.")
        return

    api = HfApi(token=token)
    user = api.whoami()["name"]
    print(f"👤 User: {user}")

    print("\n🚀 Checking Spaces...")
    spaces = api.list_spaces(author=user)

    found = False
    for space in spaces:
        found = True
        runtime = api.get_space_runtime(repo_id=space.id)
        print(f"\n📦 Space: {space.id}")
        print(f"   Status: {runtime.stage}")
        print(f"   Hardware: {runtime.hardware}")
        print(f"   URL: https://huggingface.co/spaces/{space.id}")

        if runtime.stage == "SLEEPING":
            print("   💤 Space is sleeping. Attempting to wake up...")
            try:
                # Fazer uma requisição para acordar (ou restart via API se possível)
                api.restart_space(repo_id=space.id)
                print("   ✅ Restart signal sent!")
            except Exception as e:
                print(f"   ❌ Failed to restart: {e}")

    if not found:
        print("⚠️  No Spaces found for this user.")


if __name__ == "__main__":
    check_spaces()
