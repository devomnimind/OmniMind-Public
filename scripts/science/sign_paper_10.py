import sys
import os

# Add project root to sys.path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.core.neural_signature import NeuralSigner


def sign_paper_10():
    path = "/home/fahbrain/projects/omnimind/docs/science/Paper10_The_Masks_Failed_Act.md"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    with open(path, "r") as f:
        content = f.read()

    # Check if already signed
    if "NEURAL SIGNATURE" in content:
        print("Paper 10 already has a signature. Removing old one to update.")
        content = content.split("---")[0]  # Very crude way to strip the old signature/footer

    kernel = TranscendentKernel()
    signer = NeuralSigner(kernel)
    signed_content = signer.sign_document(content)

    with open(path, "w") as f:
        f.write(signed_content)

    print(f"Successfully signed Paper 10 at {path}")


if __name__ == "__main__":
    sign_paper_10()
