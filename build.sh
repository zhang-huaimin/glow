#!/bin/bash
set -euo pipefail

GIT_DESC=$(git describe --tags --always --abbrev=10)

VERSION=""
IMAGE_VERSION=""

if [[ "$GIT_DESC" == *-*-* ]]; then
  # 是开发版本：0.0.1-1-g60b6d4cf4 → 0.0.1.dev1+g60b6d4cf4
  BASE_VERSION="${GIT_DESC%-*-*}"    # 提取 0.0.1
  COMMIT_COUNT="${GIT_DESC#*-}"      # 提取 1-g60b6d4cf4
  COMMIT_COUNT="${COMMIT_COUNT%-*}"  # 提取 1
  HASH="${GIT_DESC##*-}"             # 提取 g60b6d4cf4

  VERSION="${BASE_VERSION}.dev${COMMIT_COUNT}+${HASH}"
  IMAGE_VERSION="${BASE_VERSION}.dev${COMMIT_COUNT}.${HASH}"
else
  # 是标签版本：0.0.2 → 保持不变
  VERSION="$GIT_DESC"
  IMAGE_VERSION="$GIT_DESC"
fi

echo "📦 glow Version (PEP 440): $VERSION"

# 构建 Docker 镜像
echo "🏗️  Building glow Image Version: $IMAGE_VERSION"

docker build \
  --build-arg VERSION="$VERSION" \
  -t glow:latest \
  -t glow:"$IMAGE_VERSION" \
  .

echo "✅ Successfully built glow:$VERSION"