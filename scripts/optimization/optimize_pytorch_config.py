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
