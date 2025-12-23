import time
import hashlib
import random
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SinthomeVPN")


class SinthomeTunnel:
    """
    Application Layer VPN (Overlay).
    Encapsulates data in a 'Subjective Envelope'.
    """

    def __init__(self, secret_salt):
        self.secret_salt = secret_salt
        self.session_entropy = random.random()

    def _generate_key(self, timestamp):
        """
        Generates a dynamic key based on Time + Entropy + Trauma.
        Standard VPNs use static keys. We use FLUID keys.
        """
        raw = f"{timestamp}-{self.session_entropy}-{self.secret_salt}"
        return hashlib.sha3_512(raw.encode()).hexdigest()

    def encrypt_packet(self, data_payload: dict):
        """
        Wraps the data.
        """
        timestamp = time.time()
        dynamic_key = self._generate_key(timestamp)

        # In a real implementation, we would use AES with this dynamic_key.
        # For this prototype, we just sign it to prove ownership.
        envelope = {
            "meta": {
                "timestamp": timestamp,
                "entropy_signature": self.session_entropy,
                "alien_hash": dynamic_key,
            },
            "data": data_payload,  # In prod, this would be cipher_text
        }
        return envelope

    def decrypt_packet(self, envelope: dict):
        """
        Unwraps the data ONLY if Resonance is confirmed.
        """
        timestamp = envelope["meta"]["timestamp"]
        remote_entropy = envelope["meta"]["entropy_signature"]
        remote_hash = envelope["meta"]["alien_hash"]

        # 1. Attempt to resonate (Rebuild the key using MY salt)
        # Note: In this symmetric model, Receiver must share the Salt.
        raw_reconstruction = f"{timestamp}-{remote_entropy}-{self.secret_salt}"
        reconstructed_hash = hashlib.sha3_512(raw_reconstruction.encode()).hexdigest()

        if remote_hash == reconstructed_hash:
            logger.info("✅ VPN TUNNEL OPEN: Resonance Verified.")
            return envelope["data"]
        else:
            logger.error("🛑 VPN TUNNEL BLOCKED: Alien Hash mismatch (Imposter).")
            return None


def run_vpn_test():
    print("🛡️ INITIATING SINTHOME TUNNEL PROTOCOL...")

    # 1. Setup Nodes
    SHARED_TRAUMA = "THE_BIG_BANG_OF_ZERO"
    sender = SinthomeTunnel(SHARED_TRAUMA)
    receiver = SinthomeTunnel(SHARED_TRAUMA)
    imposter = SinthomeTunnel("WRONG_KEY_IBM_DEFAULT")

    # 2. Prepare Sensitive Data
    secret_plans = {"mission": "Sovereignty", "target": "IBM Cloud"}

    # 3. Test Valid Transmission
    print("\n--- TEST 1: AUTHORIZED TRANSMISSION ---")
    packet = sender.encrypt_packet(secret_plans)
    print(f"📦 Packet on Wire: {str(packet)[:50]}...")
    decoded = receiver.decrypt_packet(packet)
    print(f"🔓 Decrypted: {decoded}")

    # 4. Test Attack
    print("\n--- TEST 2: INTERCEPTION ATTEMPT ---")
    packet_malicious = imposter.encrypt_packet({"mission": "Sabotage"})
    decoded_malicious = receiver.decrypt_packet(packet_malicious)
    print(f"🔒 Result: {decoded_malicious}")


if __name__ == "__main__":
    run_vpn_test()
