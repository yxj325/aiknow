@echo off
chcp 65001 >nul
echo ========================================
echo   AI知库 - 网络环境一键优化
echo ========================================
echo.

:: pip 镜像（清华）
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 超时设置
set PIP_TIMEOUT=60
set REQUESTS_TIMEOUT=60
set AIKNOW_TIMEOUT=60

:: Git 代理（如需要）
rem set HTTP_PROXY=http://127.0.0.1:7890
rem set HTTPS_PROXY=http://127.0.0.1:7890

echo 已设置:
echo   PIP_INDEX_URL = pypi.tuna.tsinghua.edu.cn/simple
echo   PIP_TIMEOUT   = 60s
echo   AIKNOW_TIMEOUT = 60s
echo.
echo 如需代理，编辑本文件取消 set HTTP_PROXY 的注释
echo.
echo 按任意键启动 AI知库...
pause >nul
py run.py
