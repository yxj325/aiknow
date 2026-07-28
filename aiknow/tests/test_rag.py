# -*- coding: utf-8 -*-
"""AI知库 RAG引擎 单元测试"""
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'aiknow')

import unittest
from app.rag.loader import DocumentLoader, Document, load_text
from app.rag.chunker import Chunker
from app.rag.embeddings import EmbeddingService
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.rag.pipeline import RAGPipeline


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.loader = DocumentLoader()

    def test_load_text(self):
        docs = load_text("Hello World")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].content, "Hello World")

    def test_supported_exts(self):
        self.assertIn(".pdf", self.loader.SUPPORTED_EXT)
        self.assertIn(".md", self.loader.SUPPORTED_EXT)
        self.assertIn(".txt", self.loader.SUPPORTED_EXT)

    def test_markdown_detection(self):
        path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        if os.path.exists(path):
            docs = self.loader.load(path)
            self.assertGreater(len(docs), 0)

    def test_unknown_ext(self):
        docs = self.loader.load("test.xyz")
        self.assertEqual(len(docs), 0)


class TestChunker(unittest.TestCase):
    def test_fixed_chunk(self):
        chunker = Chunker(strategy="fixed", chunk_size=20, chunk_overlap=2)
        text = "A" * 100
        docs = load_text(text)
        chunks = chunker.chunk_documents(docs)
        self.assertGreater(len(chunks), 1)

    def test_heading_chunk(self):
        chunker = Chunker(strategy="heading")
        text = "# Title\n\nContent here.\n\n## Subtitle\n\nMore content."
        docs = load_text(text)
        chunks = chunker.chunk_documents(docs)
        self.assertGreater(len(chunks), 0)

    def test_semantic_chunk(self):
        chunker = Chunker(strategy="semantic", chunk_size=30)
        text = "Para one.\n\nPara two.\n\nPara three.\n\nPara four."
        docs = load_text(text)
        chunks = chunker.chunk_documents(docs)
        self.assertGreater(len(chunks), 0)

    def test_empty_doc(self):
        chunker = Chunker()
        docs = load_text("")
        chunks = chunker.chunk_documents(docs)
        self.assertEqual(len(chunks), 0)


class TestEmbeddings(unittest.TestCase):
    def test_mock_embedding(self):
        emb = EmbeddingService()
        vec = emb.encode(["hello"])
        self.assertEqual(vec.shape, (1, 384))

    def test_mock_dimension(self):
        emb = EmbeddingService()
        self.assertEqual(emb.dimension, 384)

    def test_mock_deterministic(self):
        emb = EmbeddingService()
        v1 = emb.encode(["same text"])
        v2 = emb.encode(["same text"])
        import numpy as np
        self.assertTrue(np.allclose(v1, v2))


class TestRetriever(unittest.TestCase):
    def test_retrieve_empty(self):
        emb = EmbeddingService()
        ret = Retriever(emb)
        results = ret.retrieve("test", [])
        self.assertEqual(len(results), 0)

    def test_retrieve_with_docs(self):
        emb = EmbeddingService()
        ret = Retriever(emb, top_k=2)
        docs = [Document("RAG is retrieval augmented generation technology."),
                Document("Python is a programming language.")]
        emb.encode([d.content for d in docs])
        results = ret.retrieve("RAG technology", docs)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)


class TestGenerator(unittest.TestCase):
    def test_mock_generate(self):
        gen = Generator(provider="mock")
        docs = [Document("RAG is retrieval augmented generation.")]
        result = gen.generate("What is RAG?", docs)
        self.assertIn("answer", result)
        self.assertGreater(len(result["answer"]), 0)

    def test_no_context(self):
        gen = Generator(provider="mock")
        result = gen.generate("test", [])
        self.assertIn("未找到相关知识", result["answer"])


class TestPipeline(unittest.TestCase):
    def test_pipeline_empty_query(self):
        p = RAGPipeline({})
        result = p.query("test")
        self.assertIn("知识库为空", result["answer"])

    def test_pipeline_add_text(self):
        p = RAGPipeline({})
        n = p.add_text("RAG technology is important for enterprise knowledge management.")
        self.assertGreater(n, 0)

    def test_pipeline_query_with_data(self):
        p = RAGPipeline({})
        p.add_text("RAG (Retrieval Augmented Generation) combines retrieval and generation.")
        p.add_text("Vector databases like ChromaDB store embeddings for semantic search.")
        p.add_text("BGE embedding models are optimized for Chinese text.")
        result = p.query("What is RAG?")
        self.assertIn("answer", result)
        self.assertGreater(result["total_chunks"], 0)
        self.assertGreater(result["chunks_retrieved"], 0)

    def test_pipeline_stats(self):
        p = RAGPipeline({})
        stats = p.stats
        self.assertIn("chunks", stats)
        self.assertIn("llm_provider", stats)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
