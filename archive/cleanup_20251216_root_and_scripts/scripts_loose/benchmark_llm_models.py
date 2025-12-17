#!/usr/bin/env python3
"""
Benchmark script to compare Phi vs Qwen2 response times and quality.

Tests:
1. Simple prompt (fast inference)
2. Complex prompt (reasoning)
3. Measures: latency, tokens/sec, quality

Usage:
    python scripts/benchmark_llm_models.py
"""

import sys
import time
from typing import Any, Dict

import requests

# Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/generate"

# Test prompts
PROMPTS = {
    "simple": "What is 2+2?",
    "medium": "Explain quantum entanglement in one sentence.",
    "complex": "Design a Python function that validates email addresses and explain the logic.",
}


def test_model(model_name: str, prompt: str, prompt_name: str) -> Dict[str, Any]:
    """Test a model with a prompt and measure performance."""

    print(f"\n  🧪 Testing {model_name} with '{prompt_name}' prompt...")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    try:
        start_time = time.time()
        response = requests.post(OLLAMA_API, json=payload, timeout=300)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"     ❌ Error: {response.status_code}")
            return {"error": response.status_code}

        data = response.json()

        # Extract metrics
        response_text = data.get("response", "")
        tokens_generated = data.get("eval_count", 0)
        tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0

        result = {
            "model": model_name,
            "prompt": prompt_name,
            "elapsed": elapsed,
            "tokens": tokens_generated,
            "tokens_per_sec": tokens_per_sec,
            "response_length": len(response_text),
            "response_preview": (
                response_text[:100] + "..." if len(response_text) > 100 else response_text
            ),
        }

        print(
            f"     ✅ {elapsed:.2f}s | {tokens_generated} tokens | {tokens_per_sec:.2f} tokens/sec"
        )

        return result

    except requests.exceptions.Timeout:
        print("     ⏱️  TIMEOUT (>300s)")
        return {"error": "timeout"}
    except Exception as e:
        print(f"     ❌ Exception: {type(e).__name__}: {e}")
        return {"error": str(e)}


def main():
    print("=" * 70)
    print("🤖 LLM MODEL BENCHMARK: Phi vs Qwen2")
    print("=" * 70)

    # Check available models
    print("\n📦 Checking available models...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json().get("models", [])
        available = [m["name"].split(":")[0] for m in models]
        print(f"   Found: {', '.join(available)}")
    except Exception as e:
        print(f"   ❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        sys.exit(1)

    results = {}

    for model in ["phi", "qwen2"]:
        print(f"\n{'='*70}")
        print(f"🔬 Testing {model.upper()}")
        print(f"{'='*70}")

        model_tag = f"{model}:latest"
        model_results = []

        for prompt_name, prompt_text in PROMPTS.items():
            result = test_model(model_tag, prompt_text, prompt_name)
            model_results.append(result)

        results[model] = model_results

    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}\n")

    for model, model_results in results.items():
        print(f"\n{model.upper()}:")
        total_time = 0
        total_tokens = 0

        for result in model_results:
            if "error" not in result:
                print(
                    f"  {result['prompt']:10} | {result['elapsed']:6.2f}s | {result['tokens_per_sec']:6.2f} tok/s | {result['response_length']:4} chars"
                )
                total_time += result["elapsed"]
                total_tokens += result["tokens"]

        if total_time > 0:
            avg_tok_per_sec = total_tokens / total_time
            print(f"  {'TOTAL':10} | {total_time:6.2f}s | {avg_tok_per_sec:6.2f} tok/s avg")

    # Recommendations
    print(f"\n{'='*70}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*70}\n")

    try:
        phi_time = sum(
            r.get("elapsed", float("inf")) for r in results.get("phi", []) if "error" not in r
        )
        qwen_time = sum(
            r.get("elapsed", float("inf")) for r in results.get("qwen2", []) if "error" not in r
        )

        if phi_time < qwen_time:
            speedup = qwen_time / phi_time
            print(f"✅ Phi is {speedup:.1f}x FASTER than Qwen2")
            print("   Recommendation: Use Phi in tests for faster execution")
            print(f"   Expected test time reduction: ~{(1 - 1/speedup)*100:.0f}%")
        else:
            speedup = phi_time / qwen_time
            print(f"⚠️  Qwen2 is {speedup:.1f}x faster than Phi")
            print("   Recommendation: Keep using Qwen2 or investigate Phi setup")

    except Exception as e:
        print(f"❌ Cannot compare: {e}")

    print()


if __name__ == "__main__":
    main()
    main()
