import hashlib
from typing import Any, Dict, List

import numpy as np

# Try to import tenseal, but provide a fallback/mock if not available
# so the code can be analyzed without crashing immediately.
ts = None
try:
    import tenseal as ts_lib  # type: ignore[import-untyped]

    ts = ts_lib
    TENSEAL_AVAILABLE = True
except ImportError:
    TENSEAL_AVAILABLE = False
    print(
        "Warning: 'tenseal' library not found. EncryptedUnconsciousLayer will operate in mock mode."
    )


class EncryptedUnconsciousLayer:
    """
    Implements the 'Transparent Unconscious' fix using Homomorphic Encryption (HE).

    This layer ensures that 'repressed' memories are mathematically inaccessible
    to the Ego (and the auditor) in their raw form, but can still influence
    decision-making via homomorphic operations (dot products) in the encrypted domain.

    Based on CKKS scheme (Cheon-Kim-Kim-Song) for real number arithmetic.
    """

    def __init__(self, security_level: int = 128):
        self.context = None
        if TENSEAL_AVAILABLE and ts:
            # Setup CKKS context for real number arithmetic
            # Poly modulus degree 8192 is standard for 128-bit security
            self.context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=8192,
                coeff_mod_bit_sizes=[60, 40, 40, 60],
            )
            self.context.generate_galois_keys()
            self.context.generate_relin_keys()
            self.context.global_scale = 2**40

        self.audit_log: List[Dict[str, Any]] = []

    def repress_memory(self, event_vector: np.ndarray, metadata: dict) -> bytes:
        """
        Encrypts a traumatic event (vector representation) so it cannot be read.
        Returns the serialized encrypted vector.
        """
        if not TENSEAL_AVAILABLE or ts is None or self.context is None:
            # Log for mock mode too
            self.audit_log.append(
                {
                    "event": "repression (mock)",
                    "content_hash": hashlib.sha256(b"MOCK_ENCRYPTED_DATA").hexdigest(),
                    "metadata": metadata,
                    "accessible_to_ego": False,
                    "encryption": "MOCK",
                }
            )
            return b"MOCK_ENCRYPTED_DATA"

        # Convert to list of floats for CKKS
        float_data = event_vector.tolist()

        # Encrypt the vector
        encrypted_vector = ts.ckks_vector(self.context, float_data)
        serialized_data = encrypted_vector.serialize()

        # Log the repression action, but NOT the content
        content_hash = hashlib.sha256(serialized_data).hexdigest()

        self.audit_log.append(
            {
                "event": "repression",
                "content_hash": content_hash,
                "metadata": metadata,  # Metadata might be visible, but content is not
                "accessible_to_ego": False,
                "encryption": "CKKS post-quantum 128-bit",
            }
        )

        return serialized_data

    def unconscious_influence(
        self, encrypted_memories: List[bytes], ego_query_vector: np.ndarray
    ) -> float:
        """
        Calculates the 'influence' of repressed memories on the current Ego query
        WITHOUT decrypting the memories.

        Performs Homomorphic Dot Product using CKKS.
        """
        if not TENSEAL_AVAILABLE or ts is None or self.context is None:
            return 0.0

        if not encrypted_memories:
            return 0.0

        # Convert query to list of floats for CKKS
        query_data = ego_query_vector.tolist()

        total_influence = 0.0

        for enc_mem_bytes in encrypted_memories:
            # Deserialize memory
            enc_mem = ts.ckks_vector_from(self.context, enc_mem_bytes)

            # Homomorphic Dot Product (Ciphertext * Plaintext)
            # Result is an encrypted scalar
            enc_dot = enc_mem.dot(query_data)

            # Decrypt the scalar score
            decrypted_score = enc_dot.decrypt()[0]
            total_influence += decrypted_score

        # Average across all memories
        return total_influence / len(encrypted_memories)
