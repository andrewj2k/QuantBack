#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT_SUFFIX="$(python3-config --extension-suffix)"

c++ \
  -O3 \
  -std=c++17 \
  -Wall \
  -Wextra \
  -bundle \
  -undefined dynamic_lookup \
  $(python3-config --includes) \
  "$ROOT_DIR/cpp/fastStats.cpp" \
  -o "$ROOT_DIR/engine/fastStatsCpp${EXT_SUFFIX}"

echo "Built engine/fastStatsCpp${EXT_SUFFIX}"
