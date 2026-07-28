# -*- coding: utf-8 -*-
"""
AI知库 快速演示脚本 - 展示RAG引擎基础能力
"""

import os
import sys
import tempfile
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.basicConfig(level=logging.INFO)

from app.rag.loader import DocumentLoader, load_text
from app.rag.chunker import Chunker
from app.rag.pipeline import RAGPipeline


def demo():
    print("=" * 56)
    print("  AI知库 - RAG引擎演示")
    print("=" * 56)

    # 1. 加载器演示
    print("\n📄 1. 文档加载器")
    loader = DocumentLoader()
    print(f"   支持类型: {loader.SUPPORTED_EXT}")

    # 2. 分块演示
    print("\n✂️  2. 智能分块（多种策略）")
    sample = """# AI知库简介

## 产品概述

AI知库是一个面向中小企业的智能知识库问答系统。

## 核心功能

### 文档解析
支持PDF、Word、Excel、Markdown等多种格式。

### 智能检索
基于向量语义搜索，支持MMR重排序。

### 答案生成
集成OpenAI与Ollama，提供精准回答。"""
    for strategy in ["heading", "fixed", "semantic"]:
        chunker = Chunker(strategy=strategy, chunk_size=200)
        chunks = chunker.chunk_documents(load_text(sample))
        print(f"   [{strategy}] {len(chunks)} 个块")

    # 3. 完整管道演示（无LLM模式）
    print("\n🔧 3. RAG管道（模拟模式）")
    pipeline = RAGPipeline({})
    pipeline.add_text("RAG（检索增强生成）是当前最主流的企业知识库技术路线。它通过检索+生成的方式，实现精准问答。")
    pipeline.add_text("向量数据库是RAG系统的核心组件，常用的包括ChromaDB、Milvus、Qdrant等。")
    pipeline.add_text("BGE是由北京人工智能研究院（BAAI）发布的中文嵌入模型，在多个榜单上表现优异。")

    result = pipeline.query("什么是RAG技术？")
    print(f"   问题: {'什么是RAG技术？'}")
    print(f"   回答: {result['answer']}")
    print(f"   检索: {result['chunks_retrieved']} / {result['total_chunks']} 块")

    print("\n✅ 演示完成!")
    print(f"   启动API: python run.py")
    print(f"   Web界面: http://localhost:8000/ui")


if __name__ == "__main__":
    demo()
