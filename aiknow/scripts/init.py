# -*- coding: utf-8 -*-
"""
AI知库 初始化脚本 - 创建数据目录结构
"""

import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent

DIRS = [
    "data/chroma",
    "data/cache/embeddings",
    "data/uploads",
    "data/backups",
    "logs",
    "tests/fixtures",
    "docs/api",
    "docs/user",
]

FILES = {
    "data/uploads/.gitkeep": "",
    "data/chroma/.gitkeep": "",
    "logs/.gitkeep": "",
    ".env.example": "# OpenAI配置\nOPENAI_API_KEY=sk-your-key-here\nOPENAI_BASE_URL=https://api.openai.com/v1\n\n# 服务配置\nHOST=0.0.0.0\nPORT=8000\n\n# 存储配置\nAIKNOW_UPLOAD=data/uploads\nAIKNOW_CACHE=data/cache/embeddings\n",
    ".gitignore": "data/chroma/\ndata/cache/\n__pycache__/\n*.pyc\n.env\nlogs/*.log\n*.db\n__pycache__/\n",
}


def init():
    print("=" * 50)
    print("  AI知库 - 初始化")
    print("=" * 50)

    # 创建目录
    for d in DIRS:
        path = BASE / d
        path.mkdir(parents=True, exist_ok=True)
        logger.info("创建目录: %s", d)

    # 创建文件
    for name, content in FILES.items():
        path = BASE / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            logger.info("创建文件: %s", name)
        else:
            logger.info("已存在: %s", name)

    print("\n✅ 初始化完成")
    print(f"   项目路径: {BASE}")
    print(f"   启动命令: python run.py")
    print(f"   API文档:  http://localhost:8000/docs")
    print(f"   Web界面:  http://localhost:8000/ui")


if __name__ == "__main__":
    init()
