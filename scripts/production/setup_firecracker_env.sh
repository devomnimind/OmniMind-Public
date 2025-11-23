#!/usr/bin/env bash
set -euo pipefail

FIRECRACKER_BASE=${1:-/opt/firecracker}
KERNEL_FILE=${FIRECRACKER_BASE}/vmlinux.bin
ROOTFS_FILE=${FIRECRACKER_BASE}/rootfs.ext4

KERNEL_URL=${FIRECRACKER_KERNEL_URL:-}
ROOTFS_URL=${FIRECRACKER_ROOTFS_URL:-}

mkdir -p "$FIRECRACKER_BASE"

if [[ -n "$KERNEL_URL" && ! -f "$KERNEL_FILE" ]]; then
  echo "Baixando kernel Firecracker de $KERNEL_URL..."
  curl -fsSL "$KERNEL_URL" -o "$KERNEL_FILE"
  chmod 644 "$KERNEL_FILE"
elif [[ ! -f "$KERNEL_FILE" ]]; then
  echo "Atenção: kernel Firecracker ausente. Defina FIRECRACKER_KERNEL_URL ou coloque o binário manualmente em $KERNEL_FILE" >&2
  exit 1
fi

if [[ -n "$ROOTFS_URL" && ! -f "$ROOTFS_FILE" ]]; then
  echo "Baixando rootfs Firecracker de $ROOTFS_URL..."
  curl -fsSL "$ROOTFS_URL" -o "$ROOTFS_FILE"
  chmod 644 "$ROOTFS_FILE"
elif [[ ! -f "$ROOTFS_FILE" ]]; then
  echo "Atenção: rootfs Firecracker ausente. Defina FIRECRACKER_ROOTFS_URL ou coloque o arquivo manualmente em $ROOTFS_FILE" >&2
  exit 1
fi

cat <<EOF
Firecracker assets prontos:
  Kernel: $KERNEL_FILE
  Rootfs: $ROOTFS_FILE
Use as variáveis OMNIMIND_FIRECRACKER_KERNEL/rootfs ao iniciar agentes de segurança.
EOF
