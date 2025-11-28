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
GPU/LLM Configuration Diagnostic and Fix Script

This script diagnoses GPU availability and LLM configuration issues, then applies fixes:

1. Detect GPU hardware and CUDA availability
2. Check LLM configurations (Ollama, HuggingFace)
3. Verify PyTorch/TensorFlow GPU support
4. Apply configuration fixes for GPU utilization
5. Test LLM inference with GPU acceleration

Usage:
    python scripts/fix_gpu_llm_config.py [--apply-fixes] [--test-inference]

Author: OmniMind Development Team
Date: 2025-11-24
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import torch


class GPUConfigurator:
    """Diagnoses and fixes GPU/LLM configuration issues."""

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.fixes_applied: List[str] = []
        self.config_dir = Path("config")

    def diagnose_and_fix(self, apply_fixes: bool = False) -> Dict[str, Any]:
        """Run complete diagnosis and optionally apply fixes."""
        print("🔍 Diagnosing GPU/LLM configuration...")

        diagnosis = {
            "timestamp": "2025-11-24T00:00:00Z",
            "gpu_hardware": self._check_gpu_hardware(),
            "cuda_status": self._check_cuda_status(),
            "pytorch_gpu": self._check_pytorch_gpu(),
            "llm_configs": self._check_llm_configs(),
            "issues_found": [],
            "fixes_applied": [],
            "recommendations": [],
        }

        # Identify issues
        diagnosis["issues_found"] = self._identify_issues(diagnosis)

        # Apply fixes if requested
        if apply_fixes:
            diagnosis["fixes_applied"] = self._apply_fixes(diagnosis["issues_found"])

        # Generate recommendations
        diagnosis["recommendations"] = self._generate_recommendations(diagnosis)

        return diagnosis

    def _check_gpu_hardware(self) -> Dict[str, Any]:
        """Check GPU hardware availability."""
        gpu_info = {
            "available": False,
            "name": None,
            "vram_gb": None,
            "driver_version": None,
            "cuda_capability": None,
        }

        try:
            # Check nvidia-smi
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines and lines[0]:
                    parts = [p.strip() for p in lines[0].split(",")]
                    if len(parts) >= 3:
                        gpu_info["available"] = True
                        gpu_info["name"] = parts[0]
                        gpu_info["vram_gb"] = float(parts[1]) / 1024  # Convert MB to GB
                        gpu_info["driver_version"] = parts[2]

                        # Get CUDA capability
                        cap_result = subprocess.run(
                            [
                                "nvidia-smi",
                                "--query-gpu=compute_cap",
                                "--format=csv,noheader,nounits",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if cap_result.returncode == 0:
                            gpu_info["cuda_capability"] = cap_result.stdout.strip()

        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        return gpu_info

    def _check_cuda_status(self) -> Dict[str, Any]:
        """Check CUDA installation and version."""
        cuda_info = {
            "installed": False,
            "version": None,
            "nvcc_available": False,
            "cudnn_available": False,
        }

        # Check CUDA version via nvcc
        try:
            result = subprocess.run(
                ["nvcc", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "release" in result.stdout:
                cuda_info["nvcc_available"] = True
                # Extract version
                for line in result.stdout.split("\n"):
                    if "release" in line:
                        version_match = re.search(r"release (\d+\.\d+)", line)
                        if version_match:
                            cuda_info["version"] = version_match.group(1)
                            cuda_info["installed"] = True
                        break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check cuDNN (basic check)
        try:
            # Try to import cuDNN-related CUDA libraries
            import ctypes

            libcudnn = ctypes.CDLL("libcudnn.so")
            cuda_info["cudnn_available"] = True
        except (ImportError, OSError):
            pass

        return cuda_info

    def _check_pytorch_gpu(self) -> Dict[str, Any]:
        """Check PyTorch GPU support."""
        pytorch_info = {
            "installed": False,
            "cuda_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "current_device": None,
        }

        try:
            pytorch_info["installed"] = True
            pytorch_info["cuda_available"] = torch.cuda.is_available()

            if pytorch_info["cuda_available"]:
                pytorch_info["cuda_version"] = torch.version.cuda
                pytorch_info["gpu_count"] = torch.cuda.device_count()
                pytorch_info["current_device"] = (
                    torch.cuda.current_device() if torch.cuda.device_count() > 0 else None
                )
        except Exception:
            pass

        return pytorch_info

    def _check_llm_configs(self) -> Dict[str, Any]:
        """Check LLM configuration files."""
        llm_configs = {
            "ollama": self._check_ollama_config(),
            "huggingface": self._check_huggingface_config(),
            "optimization": self._check_optimization_config(),
        }
        return llm_configs

    def _check_ollama_config(self) -> Dict[str, Any]:
        """Check Ollama configuration."""
        ollama_config = {
            "configured": False,
            "base_url": None,
            "gpu_layers": None,
            "model": None,
        }

        config_file = self.config_dir / "agent_config.yaml"
        if config_file.exists():
            try:
                import yaml

                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)

                model_config = config.get("model", {})
                ollama_config["base_url"] = model_config.get("base_url")
                ollama_config["model"] = model_config.get("name")

                gpu_config = config.get("gpu", {})
                ollama_config["gpu_layers"] = gpu_config.get("gpu_layers")

                if ollama_config["base_url"] and ollama_config["model"]:
                    ollama_config["configured"] = True

            except Exception:
                pass

        return ollama_config

    def _check_huggingface_config(self) -> Dict[str, Any]:
        """Check HuggingFace configuration."""
        hf_config = {
            "token_configured": False,
            "cache_dir": None,
            "transformers_available": False,
        }

        # Check for HuggingFace token
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        if hf_token:
            hf_config["token_configured"] = True

        # Check transformers availability
        try:
            import transformers

            hf_config["transformers_available"] = True
            hf_config["cache_dir"] = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE")
        except ImportError:
            pass

        return hf_config

    def _check_optimization_config(self) -> Dict[str, Any]:
        """Check optimization configuration."""
        opt_config = {"use_gpu": False, "device": "cpu", "gpu_memory_limit": None}

        config_file = self.config_dir / "optimization_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    opt_config.update(config)
            except Exception:
                pass

        return opt_config

    def _identify_issues(self, diagnosis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify configuration issues."""
        issues = []

        # GPU hardware issues
        gpu_hw = diagnosis["gpu_hardware"]
        if not gpu_hw["available"]:
            issues.append(
                {
                    "type": "hardware",
                    "severity": "HIGH",
                    "component": "gpu_hardware",
                    "description": "No GPU hardware detected",
                    "fix_available": False,
                }
            )

        # CUDA issues
        cuda_status = diagnosis["cuda_status"]
        if not cuda_status["installed"]:
            issues.append(
                {
                    "type": "cuda",
                    "severity": "HIGH",
                    "component": "cuda",
                    "description": "CUDA not installed or not found",
                    "fix_available": False,
                }
            )

        # PyTorch GPU issues
        pytorch = diagnosis["pytorch_gpu"]
        if not pytorch["cuda_available"]:
            issues.append(
                {
                    "type": "pytorch",
                    "severity": "HIGH",
                    "component": "pytorch_cuda",
                    "description": "PyTorch CUDA support not available",
                    "fix_available": True,
                    "fix_command": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
                }
            )

        # Configuration issues
        opt_config = diagnosis["llm_configs"]["optimization"]
        if not opt_config["use_gpu"]:
            issues.append(
                {
                    "type": "config",
                    "severity": "MEDIUM",
                    "component": "optimization_config",
                    "description": "GPU usage disabled in optimization config",
                    "fix_available": True,
                    "fix_action": "enable_gpu_in_config",
                }
            )

        if opt_config["device"] == "cpu":
            issues.append(
                {
                    "type": "config",
                    "severity": "MEDIUM",
                    "component": "optimization_config",
                    "description": "Device set to CPU instead of CUDA",
                    "fix_available": True,
                    "fix_action": "set_cuda_device",
                }
            )

        # Hardware profile issues
        hw_profile_file = self.config_dir / "hardware_profile.json"
        if hw_profile_file.exists():
            try:
                with open(hw_profile_file, "r") as f:
                    hw_profile = json.load(f)
                    if not hw_profile.get("gpu_available", False):
                        issues.append(
                            {
                                "type": "config",
                                "severity": "MEDIUM",
                                "component": "hardware_profile",
                                "description": "Hardware profile shows GPU as unavailable",
                                "fix_available": True,
                                "fix_action": "update_hardware_profile",
                            }
                        )
            except Exception:
                pass

        return issues

    def _apply_fixes(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Apply available fixes."""
        fixes_applied = []

        for issue in issues:
            if not issue.get("fix_available", False):
                continue

            if issue["fix_action"] == "enable_gpu_in_config":
                self._fix_optimization_config()
                fixes_applied.append("Enabled GPU usage in optimization_config.json")

            elif issue["fix_action"] == "set_cuda_device":
                self._fix_optimization_device()
                fixes_applied.append("Set device to CUDA in optimization_config.json")

            elif issue["fix_action"] == "update_hardware_profile":
                self._fix_hardware_profile()
                fixes_applied.append("Updated hardware profile to reflect GPU availability")

        return fixes_applied

    def _fix_optimization_config(self) -> None:
        """Enable GPU in optimization config."""
        config_file = self.config_dir / "optimization_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)

                config["use_gpu"] = True
                config["device"] = "cuda"

                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)

            except Exception as e:
                print(f"Error fixing optimization config: {e}")

    def _fix_optimization_device(self) -> None:
        """Set CUDA device in optimization config."""
        self._fix_optimization_config()  # Same fix

    def _fix_hardware_profile(self) -> None:
        """Update hardware profile with GPU info."""
        hw_file = self.config_dir / "hardware_profile.json"
        if hw_file.exists():
            try:
                with open(hw_file, "r") as f:
                    hw_profile = json.load(f)

                # Update with current GPU detection
                gpu_info = self._check_gpu_hardware()
                hw_profile.update(
                    {
                        "gpu_available": gpu_info["available"],
                        "gpu_name": gpu_info["name"],
                        "gpu_vram_gb": gpu_info["vram_gb"],
                        "gpu_compute_capability": gpu_info["cuda_capability"],
                    }
                )

                with open(hw_file, "w") as f:
                    json.dump(hw_profile, f, indent=2)

            except Exception as e:
                print(f"Error fixing hardware profile: {e}")

    def _generate_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on diagnosis."""
        recommendations = []

        gpu_hw = diagnosis["gpu_hardware"]
        cuda_status = diagnosis["cuda_status"]
        pytorch = diagnosis["pytorch_gpu"]

        if not gpu_hw["available"]:
            recommendations.append(
                "🔴 HARDWARE: No GPU detected - consider GPU-equipped hardware for LLM acceleration"
            )
        elif gpu_hw["available"] and not cuda_status["installed"]:
            recommendations.append("🟡 CUDA: Install CUDA toolkit for GPU acceleration")
        elif cuda_status["installed"] and not pytorch["cuda_available"]:
            recommendations.append(
                "🟡 PYTORCH: Install PyTorch with CUDA support: pip install torch --index-url https://download.pytorch.org/whl/cu121"
            )

        if pytorch["cuda_available"]:
            recommendations.append(
                "✅ GPU READY: PyTorch CUDA support available - LLMs can use GPU acceleration"
            )

        # Ollama recommendations
        ollama_config = diagnosis["llm_configs"]["ollama"]
        if ollama_config["configured"] and gpu_hw["available"]:
            if ollama_config["gpu_layers"] == -1:  # Auto
                recommendations.append(
                    "✅ OLLAMA: GPU layers set to auto - should use GPU automatically"
                )
            elif ollama_config["gpu_layers"] == 0:
                recommendations.append(
                    "🟡 OLLAMA: GPU layers set to 0 - increase for GPU acceleration"
                )

        # HuggingFace recommendations
        hf_config = diagnosis["llm_configs"]["huggingface"]
        if not hf_config["transformers_available"]:
            recommendations.append(
                "🟡 HUGGINGFACE: Install transformers for HuggingFace model support"
            )
        if not hf_config["token_configured"]:
            recommendations.append(
                "🔵 HUGGINGFACE: Set HF_TOKEN for accessing private/gated models"
            )

        return recommendations

    def test_inference(self) -> Dict[str, Any]:
        """Test LLM inference with current configuration."""
        test_results = {
            "ollama_test": self._test_ollama_inference(),
            "pytorch_gpu_test": self._test_pytorch_gpu(),
            "transformers_test": self._test_transformers_gpu(),
        }
        return test_results

    def _test_ollama_inference(self) -> Dict[str, Any]:
        """Test Ollama inference."""
        result = {"success": False, "error": None, "gpu_used": False}

        try:
            from langchain_ollama import OllamaLLM

            # Test basic connectivity
            llm = OllamaLLM(model="qwen2:7b-instruct", base_url="http://localhost:11434")
            response = llm.invoke("Hello, test message")

            if response:
                result["success"] = True
                # Note: Can't easily detect GPU usage from Ollama response
                result["gpu_used"] = "unknown"

        except Exception as e:
            result["error"] = str(e)

        return result

    def _test_pytorch_gpu(self) -> Dict[str, Any]:
        """Test PyTorch GPU functionality."""
        result = {"success": False, "error": None, "gpu_available": False}

        try:
            result["gpu_available"] = torch.cuda.is_available()
            if result["gpu_available"]:
                result["success"] = True
                result["device_count"] = torch.cuda.device_count()
                result["current_device"] = torch.cuda.current_device()

                # Test basic GPU operation
                x = torch.randn(1000, 1000).cuda()
                y = torch.randn(1000, 1000).cuda()
                z = torch.mm(x, y)
                result["computation_success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def _test_transformers_gpu(self) -> Dict[str, Any]:
        """Test Transformers GPU functionality."""
        result = {"success": False, "error": None, "gpu_used": False}

        try:
            from transformers import pipeline

            # Test with a small model
            pipe = pipeline(
                "text-generation",
                model="distilgpt2",
                device=0 if torch.cuda.is_available() else -1,
            )

            result["gpu_used"] = torch.cuda.is_available()
            result["success"] = True

        except ImportError:
            result["error"] = "transformers not installed"
        except Exception as e:
            result["error"] = str(e)

        return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose and fix GPU/LLM configuration")
    parser.add_argument("--apply-fixes", action="store_true", help="Apply available fixes")
    parser.add_argument(
        "--test-inference", action="store_true", help="Test LLM inference after fixes"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for JSON report",
        default="gpu_llm_diagnosis_report.json",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    configurator = GPUConfigurator()
    diagnosis = configurator.diagnose_and_fix(apply_fixes=args.apply_fixes)

    if args.test_inference:
        diagnosis["inference_tests"] = configurator.test_inference()

    # Save JSON report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False)

    if args.verbose:
        print(json.dumps(diagnosis, indent=2, ensure_ascii=False))
    else:
        print(f"GPU/LLM diagnosis complete. Report saved to {args.output}")

        issues = diagnosis.get("issues_found", [])
        fixes = diagnosis.get("fixes_applied", [])
        recommendations = diagnosis.get("recommendations", [])

        print(f"Issues found: {len(issues)}")
        print(f"Fixes applied: {len(fixes)}")

        if fixes:
            print("\n🔧 Fixes Applied:")
            for fix in fixes:
                print(f"  ✅ {fix}")

        if recommendations:
            print("\n📋 Recommendations:")
            for rec in recommendations[:5]:
                print(f"  {rec}")


if __name__ == "__main__":
    main()
