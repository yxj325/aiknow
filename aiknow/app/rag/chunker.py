# -*- coding: utf-8 -*-
"""
智能文档分块引擎 - 支持 heading-aware / semantic / fixed 三种策略
"""

import re
from typing import List
import logging

logger = logging.getLogger(__name__)

from .loader import Document


class Chunker:
    def __init__(self, strategy: str = "heading", chunk_size: int = 500, chunk_overlap: int = 50):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        chunks = []
        for doc in docs:
            chunks.extend(self._chunk_single(doc))
        logger.info("分块完成: %d 文档 -> %d 块", len(docs), len(chunks))
        return chunks

    def _chunk_single(self, doc: Document) -> List[Document]:
        if self.strategy == "heading":
            return self._heading_chunk(doc)
        elif self.strategy == "semantic":
            return self._semantic_chunk(doc)
        else:
            return self._fixed_chunk(doc)

    def _heading_chunk(self, doc: Document) -> List[Document]:
        """基于标题层级的分块（heading-aware）"""
        text = doc.content
        pattern = r"(^#+\s+.*$|^.*[。！？!?]\s*$)"
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        sections = heading_pattern.split(text)
        chunks = []
        current_heading = doc.metadata.get("source", "")
        current_text = []
        for i, part in enumerate(sections):
            if i % 3 == 1:
                if current_text:
                    content = "\n".join(current_text).strip()
                    if len(content) > 50:
                        meta = dict(doc.metadata)
                        meta["heading"] = current_heading
                        chunks.append(Document(content, meta))
                    current_text = []
                current_heading = part.strip()
            elif i % 3 == 2:
                para = part.strip()
                if para:
                    current_text.append(para)
        if current_text:
            content = "\n".join(current_text).strip()
            if content:
                meta = dict(doc.metadata)
                meta["heading"] = current_heading
                chunks.append(Document(content, meta))
        return chunks if chunks else self._fixed_chunk(doc)

    def _fixed_chunk(self, doc: Document) -> List[Document]:
        """固定大小分块（带overlap）"""
        text = doc.content
        chunks = []
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            content = text[start:end]
            meta = dict(doc.metadata)
            meta["chunk_index"] = chunk_idx
            meta["chunk_start"] = start
            chunks.append(Document(content, meta))
            start += self.chunk_size - self.chunk_overlap
            chunk_idx += 1
        return chunks

    def _semantic_chunk(self, doc: Document) -> List[Document]:
        """语义分块：按段落+长度组合"""
        text = doc.content
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = []
        current_len = 0
        chunk_idx = 0
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            para_len = len(para)
            if current_len + para_len > self.chunk_size and current_chunk:
                content = "\n\n".join(current_chunk)
                meta = dict(doc.metadata)
                meta["chunk_index"] = chunk_idx
                chunks.append(Document(content, meta))
                current_chunk = []
                current_len = 0
                chunk_idx += 1
            current_chunk.append(para)
            current_len += para_len
        if current_chunk:
            content = "\n\n".join(current_chunk)
            meta = dict(doc.metadata)
            meta["chunk_index"] = chunk_idx
            chunks.append(Document(content, meta))
        return chunks if chunks else self._fixed_chunk(doc)
