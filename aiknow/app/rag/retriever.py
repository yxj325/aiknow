# -*- coding: utf-8 -*-
"""
语义检索器 - 纯NumPy实现（无外部依赖）
"""

import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

from .loader import Document
from .embeddings import EmbeddingService


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """纯NumPy余弦相似度"""
    a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=-1, keepdims=True) + 1e-10)
    return np.dot(a_norm, b_norm.T)


class Retriever:
    def __init__(self, embedding_service: EmbeddingService,
                 top_k: int = 5, rerank: bool = True, mmr_lambda: float = 0.7):
        self.embedding = embedding_service
        self.top_k = top_k
        self.rerank = rerank
        self.mmr_lambda = mmr_lambda

    def retrieve(self, query: str, documents: List[Document],
                 top_k: int = None) -> List[Document]:
        k = top_k or self.top_k
        if not documents:
            return []
        query_emb = self.embedding.encode_query(query)
        doc_texts = [d.content for d in documents]
        doc_embs = self.embedding.encode(doc_texts)

        # 余弦相似度
        scores = cosine_similarity(query_emb.reshape(1, -1), doc_embs)[0]
        scored = list(zip(documents, scores.tolist()))

        if self.rerank and len(scored) > k:
            scored = self._mmr_rerank(query_emb, scored, k)
        else:
            scored.sort(key=lambda x: x[1], reverse=True)
            scored = scored[:k]

        results = []
        for doc, score in scored:
            doc.metadata["relevance_score"] = round(score, 4)
            results.append(doc)
        return results

    def _mmr_rerank(self, query_emb: np.ndarray,
                    scored: list, top_k: int) -> list:
        selected = []
        remaining = list(scored)
        while len(selected) < top_k and remaining:
            mmr_scores = []
            for doc, sim_score in remaining:
                doc_emb = self.embedding.encode([doc.content])[0]
                if selected:
                    max_sim = max(
                        cosine_similarity(doc_emb.reshape(1, -1),
                            self.embedding.encode([s[0].content]).reshape(1, -1))[0, 0]
                        for s in selected
                    )
                else:
                    max_sim = 0
                mmr = self.mmr_lambda * sim_score - (1 - self.mmr_lambda) * max_sim
                mmr_scores.append(mmr)
            best_idx = int(np.argmax(mmr_scores))
            selected.append(remaining.pop(best_idx))
        return selected
