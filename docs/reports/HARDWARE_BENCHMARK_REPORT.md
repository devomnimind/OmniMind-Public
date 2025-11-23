# Hardware Benchmark Report — OmniMind

Data: 2025-11-23T12:00:50.796560+00:00

## Resumo Executivo

- **CPU:** None phys / None log cores
- **Memória:** 0.0 GB total
- **GPU:** OK
- **Disco:** N/A

## Resultados de Benchmark
| Teste | Resultado | Unidade |
| --- | --- | --- |
| Loop 1M iterações | 66.94 | ms |
| Operações matemáticas | 45.08 | ms |
| SHA-256 (hash) | 267.17 | ms |
| Compressão (zlib) | 41.19 | ms |
| Memory throughput | 16698.51 | MB/s |
| Disk seq. write | 1128.80 | MB/s |
| Disk seq. read | 8724.15 | MB/s |
| Disk random | 1013.75 | MB/s |

## Recomendações

- GPU está subutilizada ou indisponível; priorizar mais workloads CUDA caso seja confirmada a sustentabilidade.
- CPU com headroom: considerar paralelizar loops críticos e usar vectores em numpy/torch.
- Memória em nível alto; usar caches em RAM para evitar re-loads.
- Disco pode ser gargalo; cache parcial em memória e monitorar latência por I/O random.

## Detalhes
{
  "system_info": {
    "system_info": {
      "timestamp": "2025-11-19T05:35:46.457278",
      "os": {
        "system": "Linux",
        "node": "kali",
        "release": "6.16.8+kali-amd64",
        "version": "#1 SMP PREEMPT_DYNAMIC Kali 6.16.8-1kali1 (2025-09-24)",
        "machine": "x86_64",
        "processor": ""
      },
      "cpu": {
        "physical_cores": 4,
        "logical_cores": 8,
        "frequency": {
          "current_mhz": 2500.070375,
          "min_mhz": 800.0,
          "max_mhz": 2500.0
        },
        "architecture": "x86_64"
      },
      "memory": {
        "total": 24931753984,
        "available": 20167045120,
        "used": 4764708864,
        "percent": 19.1
      },
      "swap": {
        "total": 25492975616,
        "used": 12288,
        "percent": 0.0
      },
      "disk": [
        {
          "device": "/dev/mapper/kali--vg-root",
          "mountpoint": "/",
          "fstype": "ext4",
          "total": 956184760320,
          "used": 152126627840,
          "free": 755411128320,
          "percent": 16.8
        },
        {
          "device": "/dev/nvme0n1p2",
          "mountpoint": "/boot",
          "fstype": "ext4",
          "total": 989052928,
          "used": 385974272,
          "free": 535080960,
          "percent": 41.9
        },
        {
          "device": "/dev/nvme0n1p1",
          "mountpoint": "/boot/efi",
          "fstype": "vfat",
          "total": 1021394944,
          "used": 311296,
          "free": 1021083648,
          "percent": 0.0
        }
      ],
      "network": {
        "lo": {
          "isup": true,
          "speed": 0,
          "mtu": 65536,
          "addresses": [
            {
              "family": "AF_INET",
              "address": "127.0.0.1"
            },
            {
              "family": "AF_INET6",
              "address": "::1"
            },
            {
              "family": "AF_PACKET",
              "address": "00:00:00:00:00:00"
            }
          ]
        },
        "eth0": {
          "isup": true,
          "speed": 1000,
          "mtu": 1500,
          "addresses": [
            {
              "family": "AF_INET",
              "address": "192.168.15.2"
            },
            {
              "family": "AF_INET6",
              "address": "2804:7f0:9482:4cc5:231d:99c9:93f6:5fe8"
            },
            {
              "family": "AF_INET6",
              "address": "2804:7f0:9482:4cc5:661c:67ff:fef3:8460"
            },
            {
              "family": "AF_INET6",
              "address": "fe80::661c:67ff:fef3:8460%eth0"
            },
            {
              "family": "AF_PACKET",
              "address": "64:1c:67:f3:84:60"
            }
          ]
        },
        "docker0": {
          "isup": false,
          "speed": 0,
          "mtu": 1500,
          "addresses": [
            {
              "family": "AF_INET",
              "address": "172.17.0.1"
            },
            {
              "family": "AF_PACKET",
              "address": "02:42:5a:97:7d:8d"
            }
          ]
        },
        "wlan0": {
          "isup": false,
          "speed": 0,
          "mtu": 1500,
          "addresses": [
            {
              "family": "AF_PACKET",
              "address": "d6:32:3b:9b:44:0f"
            }
          ]
        }
      },
      "uptime": "2025-11-19T01:53:31"
    }
  },
  "cpu": {
    "loop_ms": 66.94481233322828,
    "math_ms": 45.07838700010325,
    "hash_ms": 267.1741239999695,
    "compression_ms": 41.19483533349921,
    "timestamp": 1763530552.3408542
  },
  "gpu": {
    "init_ms": 17.247957999643404,
    "cpu_to_gpu_ms": 110.73699600092368,
    "matrix_mult_ms": 23.364186999970116,
    "gpu_to_cpu_ms": 30.18749000148091,
    "status": "OK"
  },
  "memory": {
    "memory_total": 24931749888,
    "memory_throughput_mb_s": [
      16698.50793853115,
      16158.783783896306
    ],
    "timestamp": 1763525823.645532
  },
  "disk": {
    "write_throughput_mb_s": 1128.8020607320964,
    "read_throughput_mb_s": 8724.149037787858,
    "random_access_mb_s": 1013.7501502093163,
    "timestamp": 1763899250.74795
  }
}