# -*- coding: utf-8 -*-
"""
答案生成器 - 支持 OpenAI / Ollama / Mock 模式
Mock模式在无API Key时自动启用
"""

import os
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

from .loader import Document


class Generator:
    def __init__(self, provider: str = "mock", model: str = "gpt-3.5-turbo",
                 api_key: str = None, api_base: str = None,
                 ollama_base: str = "http://localhost:11434",
                 ollama_model: str = "qwen2:7b",
                 temperature: float = 0.3, max_tokens: int = 2048):
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.api_base = api_base or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.ollama_base = ollama_base
        self.ollama_model = ollama_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 自动检测 - 无API Key则使用Mock
        if self.provider == "openai" and not self.api_key:
            logger.info("无OPENAI_API_KEY，启用Mock LLM模式")
            self.provider = "mock"

    def generate(self, query: str, contexts: List[Document],
                 system_prompt: str = None) -> dict:
        if not contexts:
            return {"answer": "未找到相关知识，请补充文档后再试。", "sources": [], "tokens_used": 0}

        context_text = self._format_context(contexts)

        if self.provider == "mock":
            return self._mock_generate(query, contexts, context_text)
        elif self.provider == "ollama":
            return self._call_ollama(query, contexts, context_text)
        elif self.provider == "openai":
            return self._call_openai(query, contexts, context_text)
        else:
            return self._mock_generate(query, contexts, context_text)

    def _format_context(self, contexts: List[Document]) -> str:
        parts = []
        for i, ctx in enumerate(contexts):
            source = ctx.metadata.get("source", f"文档{i+1}")
            page = ctx.metadata.get("page", "")
            heading = ctx.metadata.get("heading", "")
            score = ctx.metadata.get("relevance_score", "")
            loc_parts = [f"来源: {source}"]
            if page:
                loc_parts.append(f"第{page}页")
            if heading:
                loc_parts.append(heading)
            if score:
                loc_parts.append(f"相关度: {score}")
            parts.append(f"[{' | '.join(loc_parts)}]\n{ctx.content.strip()}")
        return "\n\n---\n\n".join(parts)

    def _mock_generate(self, query: str, contexts: List[Document],
                       context_text: str) -> dict:
        """Mock生成 - 基于检索结果摘要"""
        source_list = []
        seen = set()
        for c in contexts:
            src = c.metadata.get("source", "未知来源")
            if src not in seen:
                seen.add(src)
                source_list.append(src)

        # 提取上下文前200字作为伪回答
        top_context = contexts[0].content.strip()[:200] if contexts else ""
        answer = (
            f"基于检索结果，关于「{query}」的信息如下：\n\n"
            f"{top_context}\n\n"
            f"📎 共检索到 {len(contexts)} 个相关片段，"
            f"来自 {len(source_list)} 个文档。"
        )

        sources = [{"source": c.metadata.get("source", ""),
                     "page": c.metadata.get("page", None),
                     "score": c.metadata.get("relevance_score", None)}
                   for c in contexts if c.metadata.get("relevance_score", 0) > 0.3]

        return {"answer": answer, "sources": sources, "tokens_used": 0}

    def _call_openai(self, query: str, contexts: List[Document],
                     context_text: str) -> dict:
        import httpx
        prompt = f"你是一个专业的企业知识库助手。请基于以下文档内容回答问题。引用信息来源。\n\n## 参考文档\n{context_text}\n\n## 问题\n{query}\n\n## 回答"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature, "max_tokens": self.max_tokens}
        try:
            resp = httpx.post(f"{self.api_base}/chat/completions", headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            answer = result["choices"][0]["message"]["content"]
            sources = [{"source": c.metadata.get("source", ""), "page": c.metadata.get("page", None),
                        "score": c.metadata.get("relevance_score", None)}
                       for c in contexts if c.metadata.get("relevance_score", 0) > 0.3]
            return {"answer": answer, "sources": sources, "tokens_used": result.get("usage", {}).get("total_tokens", 0)}
        except Exception as e:
            logger.error("OpenAI调用失败: %s", e)
            return {"answer": f"生成失败: {e}", "sources": [], "tokens_used": 0}

    def _call_ollama(self, query: str, contexts: List[Document],
                     context_text: str) -> dict:
        import httpx
        prompt = f"基于以下文档回答问题：\n\n{context_text}\n\n问题：{query}"
        data = {"model": self.ollama_model, "prompt": prompt, "stream": False,
                "options": {"temperature": self.temperature, "num_predict": self.max_tokens}}
        try:
            resp = httpx.post(f"{self.ollama_base}/api/generate", json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            sources = [{"source": c.metadata.get("source", ""), "page": c.metadata.get("page", None)}
                       for c in contexts if c.metadata.get("relevance_score", 0) > 0.3]
            return {"answer": result.get("response", ""), "sources": sources, "tokens_used": 0}
        except Exception as e:
            logger.error("Ollama调用失败: %s", e)
            return {"answer": f"Ollama生成失败: {e}", "sources": [], "tokens_used": 0}
