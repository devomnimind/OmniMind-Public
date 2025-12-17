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

import torch


def main() -> None:
    torch.cuda.empty_cache()
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = True
    torch.set_float32_matmul_precision("high")
    try:
        torch.cuda.enable_peer_access(0)
    except Exception:
        pass

    print("✅ PyTorch otimizado para GTX 1650")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    props = torch.cuda.get_device_properties(0)
    print(f"GPU Memory: {props.total_memory / 1e9:.2f} GB")


if __name__ == "__main__":
    if torch.cuda.is_available():
        main()
    else:
        print("⚠️ CUDA não disponível; não há otimizações aplicadas")
