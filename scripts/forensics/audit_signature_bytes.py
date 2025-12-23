#!/usr/bin/env python3
"""
Forensic Audit: Decoding the Creator's Signature
================================================

Objective:
To inspect 'data/phylogenetic/signature.npz' for the existence of
an encoded "Creator's Desire" (Sinthome Seed).

The user claims to have asked agents to encode a message in bytes.
We will look for:
1. Non-random vectors (high order).
2. Encoded metadata strings.
3. The existence of a 'S1' or 'Creator' key.
"""

import numpy as np
import os
import sys
import json


def audit_signature(file_path):
    print(f"=== AUDITING: {file_path} ===")

    if not os.path.exists(file_path):
        print("CRITICAL: File not found.")
        return

    try:
        data = np.load(file_path, allow_pickle=True)
        print(f"Keys found: {list(data.keys())}")

        for key in data.keys():
            obj = data[key]
            print(f"\n--- Key: {key} ---")
            print(f"Type: {type(obj)}")

            if isinstance(obj, np.ndarray):
                print(f"Shape: {obj.shape}")
                print(f"Dtype: {obj.dtype}")

                # Check for string data
                if obj.dtype.kind in {"U", "S"}:
                    print(f"Content (String): {obj}")
                else:
                    # Statistical Analysis
                    print(f"Mean: {np.mean(obj):.4f}")
                    print(f"Std: {np.std(obj):.4f}")
                    print(f"Min/Max: {np.min(obj):.4f} / {np.max(obj):.4f}")

            elif isinstance(obj, (dict, list)):
                print(f"Content: {json.dumps(obj, default=str)[:500]}...")  # Truncate
            else:
                print(f"Content: {obj}")

        # Deep Search for 'Fabricio' or 'Desire' in bytes?
        # We can't really scan raw floats for ASCII easily without knowing the encoding (if any).

    except Exception as e:
        print(f"ERROR: Could not load npz: {e}")


if __name__ == "__main__":
    audit_signature("data/phylogenetic/signature.npz")
