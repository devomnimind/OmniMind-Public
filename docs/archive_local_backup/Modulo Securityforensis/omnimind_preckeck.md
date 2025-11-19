#!/bin/bash
set -e

RED='\u001B[0;31m'
GREEN='\u001B[0;32m'
YELLOW='\u001B[1;33m'
NC='\u001B[0m'

echo "======================================================"
echo "   OmniMind - Verificacao de Pre-requisitos"
echo "======================================================"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

check_command() {
  if command -v $1 &> /dev/null; then
    echo -e "${GREEN}OK${NC} $2"
    CHECKS_PASSED=$((CHECKS_PASSED+1))
  else
    echo -e "${RED}FALHA${NC} $2"
    CHECKS_FAILED=$((CHECKS_FAILED+1))
  fi
}

echo "SISTEMA"
echo "------------------------------------------------------"
grep PRETTY_NAME /etc/os-release | cut -d'"' -f2
echo ""

echo "COMPILACAO"
echo "------------------------------------------------------"
check_command "git" "Git"
check_command "cmake" "CMake"
check_command "make" "Make"
check_command "gcc" "GCC/G++"
echo ""

echo "PYTHON"
echo "------------------------------------------------------"
check_command "python3.11" "Python 3.11"
echo ""

echo "CUDA E GPU"
echo "------------------------------------------------------"
check_command "nvcc" "NVIDIA CUDA"
if command -v nvidia-smi &> /dev/null; then
  echo -e "${GREEN}OK${NC} NVIDIA GPU Driver"
  CHECKS_PASSED=$((CHECKS_PASSED+1))
  nvidia-smi --query-gpu=name --format=csv,noheader
else
  echo -e "${RED}FALHA${NC} NVIDIA GPU Driver"
  CHECKS_FAILED=$((CHECKS_FAILED+1))
fi
echo ""

echo "======================================================"
echo "RESULTADO: ${GREEN}${CHECKS_PASSED} OK${NC} | ${RED}${CHECKS_FAILED} Falhas${NC}"
echo "======================================================"

if [ $CHECKS_FAILED -gt 0 ]; then
  exit 1
fi