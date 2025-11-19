# Hardware Benchmark Report — OmniMind

Data: 2025-11-19T02:19:05.050424

## Resumo Executivo

- **CPU:** None phys / None log cores
- **Memória:** 0.0 GB total
- **GPU:** OK
- **Disco:** N/A

## Resultados de Benchmark
| Teste | Resultado | Unidade |
| --- | --- | --- |
| Loop 1M iterações | 56.59 | ms |
| Operações matemáticas | 34.91 | ms |
| SHA-256 (hash) | 287.93 | ms |
| Compressão (zlib) | 45.71 | ms |
| Memory throughput | 20875.45 | MB/s |
| Disk seq. write | 985.04 | MB/s |
| Disk seq. read | 7922.26 | MB/s |
| Disk random | 1230.17 | MB/s |

## Recomendações

- GPU está subutilizada ou indisponível; priorizar mais workloads CUDA caso seja confirmada a sustentabilidade.
- CPU com headroom: considerar paralelizar loops críticos e usar vectores em numpy/torch.
- Memória em nível alto; usar caches em RAM para evitar re-loads.
- Disco pode ser gargalo; cache parcial em memória e monitorar latência por I/O random.

## Detalhes
{
  "system_info": {
    "system_info": {
      "timestamp": "2025-11-19T02:17:53.136373",
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
          "current_mhz": 2500.1861249999997,
          "min_mhz": 800.0,
          "max_mhz": 2500.0
        },
        "architecture": "x86_64"
      },
      "memory": {
        "total": 24931753984,
        "available": 15765573632,
        "used": 9166180352,
        "percent": 36.8
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
          "used": 142051561472,
          "free": 765486194688,
          "percent": 15.7
        },
        {
          "device": "/dev/nvme0n1p2",
          "mountpoint": "/boot",
          "fstype": "ext4",
          "total": 989052928,
          "used": 384290816,
          "free": 536764416,
          "percent": 41.7
        },
        {
          "device": "/dev/nvme0n1p1",
          "mountpoint": "/boot/efi",
          "fstype": "vfat",
          "total": 1021394944,
          "used": 311296,
          "free": 1021083648,
          "percent": 0.0
        },
        {
          "device": "/dev/sda1",
          "mountpoint": "/mnt/dev_brain_clean",
          "fstype": "ext4",
          "total": 491081818112,
          "used": 19773530112,
          "free": 446286753792,
          "percent": 4.2
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
              "address": "2804:7f0:9482:4cc5:6499:87f9:3f20:1358"
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
              "address": "02:42:f8:c2:40:49"
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
              "address": "4a:86:dd:b6:0f:28"
            }
          ]
        }
      },
      "uptime": "2025-11-18T10:15:16"
    }
  },
  "cpu": {
    "loop_ms": 56.59115866971357,
    "math_ms": 34.91044466742702,
    "hash_ms": 287.92961133391753,
    "compression_ms": 45.71238266847407,
    "timestamp": 1763518682.2479289
  },
  "gpu": {
    "init_ms": 11.726748998626135,
    "cpu_to_gpu_ms": 108.85301700182026,
    "matrix_mult_ms": 21.970768000755925,
    "gpu_to_cpu_ms": 30.581625003833324,
    "status": "OK"
  },
  "memory": {
    "memory_total": 24931753984,
    "memory_throughput_mb_s": [
      20875.44517210614,
      20514.148261669114
    ],
    "timestamp": 1763518724.760559
  },
  "disk": {
    "write_throughput_mb_s": 985.0376232770991,
    "read_throughput_mb_s": 7922.2610703220025,
    "random_access_mb_s": 1230.1716039842938,
    "timestamp": 1763518734.8419156
  }
}