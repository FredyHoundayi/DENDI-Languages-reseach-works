#!/usr/bin/env bash
# Create the inference environments on the GPU VM (Ubuntu 24.04, Tesla V100 32 GB).
# Run from the project root:  bash scripts/setup_vm.sh [hf|omni|gcp ...]   (default: hf omni)
# V100 is compute capability 7.0: CUDA 13 builds of PyTorch no longer support it, so use cu126 wheels.
set -euo pipefail
TORCH_INDEX=https://download.pytorch.org/whl/cu126

check_torch() {
  "$1/bin/python" - <<'EOF'
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda, "available", torch.cuda.is_available())
print("arch list", torch.cuda.get_arch_list())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0), "bf16 supported", torch.cuda.is_bf16_supported())
EOF
}

for env in "${@:-hf omni}"; do
  for e in $env; do
    case $e in
      hf)
        python3 -m venv .venv-hf
        .venv-hf/bin/pip install -q --upgrade pip
        .venv-hf/bin/pip install -q torch --index-url $TORCH_INDEX
        .venv-hf/bin/pip install -q -r envs/requirements-hf.txt
        check_torch .venv-hf ;;
      omni)
        python3 -m venv .venv-omni
        .venv-omni/bin/pip install -q --upgrade pip
        .venv-omni/bin/pip install -q -r envs/requirements-omnilingual.txt
        check_torch .venv-omni ;;
      gcp)
        python3 -m venv .venv-gcp
        .venv-gcp/bin/pip install -q --upgrade pip
        .venv-gcp/bin/pip install -q -r envs/requirements-chirp.txt ;;
      *) echo "unknown env $e" >&2; exit 1 ;;
    esac
    echo "== $e ready"
  done
done
