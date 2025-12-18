#!/bin/bash
# Force CUDA environment variables BEFORE Python interpreter starts
# This must happen at shell level, not in Python code

export CUDA_HOME=/usr
export CUDA_VISIBLE_DEVICES=0
export CUDA_PATH=/usr
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}
export CUDA_LAUNCH_BLOCKING=1

# Log the environment setup
echo "🔧 CUDA Environment Setup:"
echo "   CUDA_HOME=$CUDA_HOME"
echo "   CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "   CUDA_PATH=$CUDA_PATH"
echo "   LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo "   CUDA_LAUNCH_BLOCKING=$CUDA_LAUNCH_BLOCKING"
echo ""

# Now run the backend with these vars locked in
cd /home/fahbrain/projects/omnimind

# Make the vars read-only to prevent modification
readonly CUDA_HOME
readonly CUDA_VISIBLE_DEVICES
readonly CUDA_PATH
readonly LD_LIBRARY_PATH

echo "🚀 Starting OmniMind Backend with GPU forcing..."
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 "$@"
