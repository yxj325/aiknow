# -*- coding: utf-8 -*-
"""
嵌入服务 - 支持 BGE / mock 两种模式
mock模式在无 sentence-transformers 时自动启用
"""

import os
import hashlib
import json
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """嵌入服务 - BGE或Mock模式"""

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5",
                 device: str = "cpu", cache_dir: str = None):
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir or os.environ.get("AIKNOW_CACHE", "data/cache/embeddings")
        self._model = None
        self._mock = False
        os.makedirs(self.cache_dir, exist_ok=True)

    @property
    def model(self):
        if self._model is None and not self._mock:
            try:
                from sentence_transformers import SentenceTransformer
                self._mock = False; logger.info("加载嵌入模型: %s (device=%s)", self.model_name, self.device)
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except (ImportError, OSError) as e:
                self._mock = True; logger.warning("嵌入模型不可用，启用Mock模式: %s", e)
                self._mock = True
        return self._model

    def encode(self, texts: List[str], normalize: bool = True,
               show_progress: bool = False) -> np.ndarray:
        if self._mock or self._model is None and not self._is_model_available():
            return self._mock_encode(texts, dim=384)
        try:
            embeddings = self.model.encode(
                texts, normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                batch_size=int(os.environ.get("BATCH_SIZE", "32"))
            )
            return embeddings
        except Exception as e:
            logger.warning("编码失败，回退Mock: %s", e)
            return self._mock_encode(texts, dim=384)

    def _is_model_available(self):
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    def _mock_encode(self, texts: List[str], dim: int = 384, normalize: bool = True) -> np.ndarray:
        """基于文本hash生成确定性伪嵌入"""
        logger.info("Mock编码 %d 文本 (dim=%d)", len(texts), dim)
        results = []
        for text in texts:
            h = hashlib.md5(text.encode("utf-8")).hexdigest()
            rng = np.random.RandomState(int(h[:8], 16))
            vec = rng.randn(dim).astype(np.float32)
            if normalize:
                vec = vec / (np.linalg.norm(vec) + 1e-10)
            results.append(vec)
        return np.array(results)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([query])[0]

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if self._mock:
            # 使用随机种子匹配来模拟相似度
            return float(np.dot(a, b))
        from sentence_transformers import util
        return float(util.cos_sim(a, b)[0][0])

    @property
    def dimension(self) -> int:
        return 384


