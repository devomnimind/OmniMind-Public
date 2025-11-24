import hashlib
from typing import List
import numpy as np

# Try to import tenseal, but provide a fallback/mock if not available
# so the code can be analyzed without crashing immediately.
try:
    import tenseal as ts

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

    Based on BFV scheme (Brakerski-Fan-Vercauteren) for integer arithmetic.
    """

    def __init__(self, security_level: int = 128):
        self.context = None
        if TENSEAL_AVAILABLE:
            # Setup BFV context for integer arithmetic
            # Poly modulus degree 8192 is standard for 128-bit security
            self.context = ts.context(
                ts.SCHEME_TYPE.BFV, poly_modulus_degree=8192, plain_modulus=1032193
            )
            self.context.generate_galois_keys()
            self.context.global_scale = 2**40

        self.audit_log = []

    def _quantize_event(self, event_vector: np.ndarray) -> List[int]:
        """
        Quantizes a float vector into integers for BFV encryption.
        Simple scaling strategy.
        """
        scale_factor = 1000
        return [int(x * scale_factor) for x in event_vector]

    def repress_memory(self, event_vector: np.ndarray, metadata: dict) -> bytes:
        """
        Encrypts a traumatic event (vector representation) so it cannot be read.
        Returns the serialized encrypted vector.
        """
        if not TENSEAL_AVAILABLE:
            return b"MOCK_ENCRYPTED_DATA"

        quantized_data = self._quantize_event(event_vector)

        # Encrypt the vector
        encrypted_vector = ts.bfv_vector(self.context, quantized_data)
        serialized_data = encrypted_vector.serialize()

        # Log the repression action, but NOT the content
        content_hash = hashlib.sha256(serialized_data).hexdigest()

        self.audit_log.append(
            {
                "event": "repression",
                "content_hash": content_hash,
                "metadata": metadata,  # Metadata might be visible, but content is not
                "accessible_to_ego": False,
                "encryption": "BFV post-quantum 128-bit",
            }
        )

        return serialized_data

    def unconscious_influence(
        self, encrypted_memories: List[bytes], ego_query_vector: np.ndarray
    ) -> float:
        """
        Calculates the 'influence' of repressed memories on the current Ego query
        WITHOUT decrypting the memories.

        Performs Homomorphic Dot Product.
        """
        if not TENSEAL_AVAILABLE:
            return 0.0

        if not encrypted_memories:
            return 0.0

        # Encrypt the Ego's query vector to perform operations in the encrypted domain
        quantized_query = self._quantize_event(ego_query_vector)
        # We use the same context
        # Note: For dot product, we might need CKKS if we wanted floats,
        # but BFV is fine for quantized integers.

        total_influence = 0

        # In a real BFV scheme, we would encrypt the query and multiply.
        # However, TenSEAL allows plain_vector * encrypted_vector multiplication.
        # This is more efficient.

        for enc_mem_bytes in encrypted_memories:
            # Deserialize memory
            enc_mem = ts.bfv_vector_from(self.context, enc_mem_bytes)

            # Homomorphic Dot Product (Ciphertext * Plaintext)
            # Result is an encrypted scalar (in vector form)
            enc_dot = enc_mem.dot(quantized_query)

            # The Ego "feels" the result (decrypts the scalar score)
            # Note: In a strict implementation, the decryption key might be held
            # by a separate 'Superego' or 'Analyst' entity, but here the system
            # needs the result to act. The key is: it never saw the memory vector.
            decrypted_score = enc_dot.decrypt()[0]
            total_influence += decrypted_score

        # Normalize back to float scale (scale * scale = scale^2)
        normalized_influence = total_influence / (1000 * 1000)

        return normalized_influence / len(encrypted_memories)
