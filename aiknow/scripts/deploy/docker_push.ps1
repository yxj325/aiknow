# AI知库 Docker 镜像构建与推送
param(
    [string]$Username = "yxj325",
    [string]$Tag = "latest"
)

$Image = "$Username/aiknow:$Tag"

Write-Host "Building Docker image: $Image"
docker build -t $Image -f aiknow/Dockerfile aiknow/

Write-Host "Pushing to Docker Hub..."
docker push $Image

Write-Host "Done: $Image"