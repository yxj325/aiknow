# -*- coding: utf-8 -*-
"""
RAG管道编排器
"""

import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

from .loader import DocumentLoader, Document
from .chunker import Chunker
from .embeddings import EmbeddingService
from .retriever import Retriever
from .generator import Generator


class RAGPipeline:
    def __init__(self, config: dict = None):
        cfg = config or {}
        emb_cfg = cfg.get("embedding", {})
        llm_cfg = cfg.get("llm", {})
        chunk_cfg = cfg.get("chunking", {})
        ret_cfg = cfg.get("retrieval", {})

        self.loader = DocumentLoader()
        self.chunker = Chunker(
            strategy=chunk_cfg.get("strategy", "heading"),
            chunk_size=chunk_cfg.get("chunk_size", 500),
            chunk_overlap=chunk_cfg.get("chunk_overlap", 50)
        )
        self.embedding = EmbeddingService(
            model_name=emb_cfg.get("model", "BAAI/bge-small-zh-v1.5"),
            device=emb_cfg.get("device", "cpu")
        )
        self.retriever = Retriever(
            embedding_service=self.embedding,
            top_k=ret_cfg.get("top_k", 5),
            rerank=ret_cfg.get("rerank", True),
            mmr_lambda=ret_cfg.get("mmr_lambda", 0.7)
        )
        self.generator = Generator(
            provider=llm_cfg.get("provider", "mock"),
            model=llm_cfg.get("model", "gpt-3.5-turbo"),
            api_key=llm_cfg.get("api_key"),
            api_base=llm_cfg.get("api_base"),
            ollama_base=llm_cfg.get("ollama_base", "http://localhost:11434"),
            ollama_model=llm_cfg.get("ollama_model", "qwen2:7b"),
            temperature=llm_cfg.get("temperature", 0.3),
            max_tokens=llm_cfg.get("max_tokens", 2048)
        )
        self._documents = []
        self._chunks = []

    def ingest(self, path: str) -> int:
        docs = self.loader.load(path)
        if not docs:
            return 0
        chunks = self.chunker.chunk_documents(docs)
        self._chunks.extend(chunks)
        self._documents.extend(docs)
        if chunks:
            self.embedding.encode([c.content for c in chunks])
        logger.info("已索引: %s -> %d 个块", path, len(chunks))
        return len(chunks)

    def ingest_directory(self, directory: str, recursive: bool = True) -> int:
        docs = self.loader.load_dir(directory, recursive=recursive)
        if not docs:
            return 0
        chunks = self.chunker.chunk_documents(docs)
        self._chunks.extend(chunks)
        self._documents.extend(docs)
        if chunks:
            self.embedding.encode([c.content for c in chunks])
        logger.info("已索引目录: %s -> %d 个块", directory, len(chunks))
        return len(chunks)

    def add_text(self, text: str, metadata: dict = None) -> int:
        from .loader import load_text
        docs = load_text(text, metadata)
        chunks = self.chunker.chunk_documents(docs)
        self._chunks.extend(chunks)
        self._documents.extend(docs)
        if chunks:
            self.embedding.encode([c.content for c in chunks])
        return len(chunks)

    def query(self, query: str, top_k: int = None) -> dict:
        if not self._chunks:
            return {"answer": "知识库为空，请先导入文档。", "sources": [], "tokens_used": 0}
        relevant = self.retriever.retrieve(query, self._chunks, top_k=top_k)
        result = self.generator.generate(query, relevant)
        result["chunks_retrieved"] = len(relevant)
        result["total_chunks"] = len(self._chunks)
        return result

    def answer(self, query: str) -> str:
        result = self.query(query)
        return result.get("answer", "")

    @property
    def stats(self) -> dict:
        return {
            "documents": len(self._documents),
            "chunks": len(self._chunks),
            "chunk_strategy": self.chunker.strategy,
            "embedding_model": self.embedding.model_name,
            "embedding_mode": "mock" if self.embedding._mock else "bge",
            "retriever_top_k": self.retriever.top_k,
            "llm_provider": self.generator.provider,
            "llm_model": self.generator.model,
        }

    def reset(self):
        self._documents.clear()
        self._chunks.clear()
        logger.info("知识库已重置")
