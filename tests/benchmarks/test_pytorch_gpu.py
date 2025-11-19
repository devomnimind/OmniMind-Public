import time

import torch


def main() -> None:
    print(f"PyTorch version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")

    if cuda_available:
        print(f"\nGPU Device: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"GPU Memory Total: {props.total_memory / 1024**3:.2f} GB")

        device = torch.device("cuda:0")
        x = torch.randn(5000, 5000, device=device)
        y = torch.randn(5000, 5000, device=device)

        # Warmup
        _ = torch.mm(x, y)
        torch.cuda.synchronize()

        start = time.time()
        for _ in range(10):
            _ = torch.mm(x, y)
        torch.cuda.synchronize()
        elapsed = time.time() - start

        print(f"\n5000x5000 Matrix Mult (GPU): {elapsed / 10 * 1000:.2f} ms")
        gflops = (5000 * 5000 * 5000 * 2) / ((elapsed / 10) * 1e9)
        print(f"Throughput: {gflops:.2f} GFLOPS")
    else:
        print("❌ CUDA not available!")


if __name__ == "__main__":
    main()

