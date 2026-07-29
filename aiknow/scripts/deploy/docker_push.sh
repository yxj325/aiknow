#!/bin/bash
# AI知库 Docker 镜像构建与推送
# 用法: ./docker_push.sh <DOCKER_USERNAME> [tag]

set -e

USERNAME=${1:-yxj325}
TAG=${2:-latest}
IMAGE="$USERNAME/aiknow:$TAG"

echo "Building Docker image: $IMAGE"
docker build -t "$IMAGE" -f aiknow/Dockerfile aiknow/

echo "Pushing to Docker Hub..."
docker push "$IMAGE"

echo "Done: $IMAGE"