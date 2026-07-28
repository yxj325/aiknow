# -*- coding: utf-8 -*-
"""
存储层 - SQLite管理知识库元数据 + ChromaDB管理向量
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库元数据管理（SQLite）"""

    def __init__(self, db_path: str = "data/aiknow.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT "",
                created_at TEXT DEFAULT (CURRENT_TIMESTAMP),
                updated_at TEXT DEFAULT (CURRENT_TIMESTAMP)
            );
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kb_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT,
                filetype TEXT,
                pages INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                status TEXT DEFAULT "pending",
                created_at TEXT DEFAULT (CURRENT_TIMESTAMP),
                FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
            );
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kb_id INTEGER,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                answer TEXT,
                sources TEXT DEFAULT "[]",
                tokens_used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (CURRENT_TIMESTAMP),
                FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
            );
        """)
        conn.commit()
        conn.close()
        logger.info("数据库初始化: %s", self.db_path)

    def create_kb(self, name: str, description: str = "") -> int:
        conn = self._get_conn()
        try:
            cur = conn.execute("INSERT INTO knowledge_bases (name, description) VALUES (?, ?)",
                             (name, description))
            conn.commit()
            kb_id = cur.lastrowid
            logger.info("创建知识库: %s (id=%d)", name, kb_id)
            return kb_id
        except sqlite3.IntegrityError:
            conn.execute("UPDATE knowledge_bases SET updated_at = datetime('now','localtime') WHERE name = ?", (name,))
            conn.commit()
            cur = conn.execute("SELECT id FROM knowledge_bases WHERE name = ?", (name,))
            row = cur.fetchone()
            conn.close()
            return row["id"]
        finally:
            conn.close()

    def list_kbs(self) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM knowledge_bases ORDER BY updated_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_kb(self, kb_id: int) -> Optional[Dict]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM knowledge_bases WHERE id = ?", (kb_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_kb(self, kb_id: int) -> bool:
        conn = self._get_conn()
        conn.execute("DELETE FROM documents WHERE kb_id = ?", (kb_id,))
        conn.execute("DELETE FROM knowledge_bases WHERE id = ?", (kb_id,))
        conn.commit()
        conn.close()
        logger.info("删除知识库 id=%d", kb_id)
        return True

    def add_document(self, kb_id: int, filename: str, filepath: str = None,
                     filetype: str = "", pages: int = 0, chunks: int = 0) -> int:
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT INTO documents (kb_id, filename, filepath, filetype, pages, chunk_count, status) "
            "VALUES (?, ?, ?, ?, ?, ?, 'indexed')",
            (kb_id, filename, filepath, filetype, pages, chunks)
        )
        conn.commit()
        doc_id = cur.lastrowid
        conn.execute("UPDATE knowledge_bases SET updated_at = datetime('now','localtime') WHERE id = ?", (kb_id,))
        conn.commit()
        conn.close()
        return doc_id

    def list_documents(self, kb_id: int) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM documents WHERE kb_id = ? ORDER BY created_at DESC", (kb_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def save_conversation(self, kb_id: int, session_id: str,
                          query: str, answer: str, sources: list, tokens: int = 0):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO conversations (kb_id, session_id, query, answer, sources, tokens_used) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (kb_id, session_id, query, answer, json.dumps(sources, ensure_ascii=False), tokens)
        )
        conn.commit()
        conn.close()

    def get_conversations(self, session_id: str, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM conversations WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def init_chroma(persist_dir: str = "data/chroma"):
    """初始化ChromaDB客户端"""
    import chromadb
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    logger.info("ChromaDB初始化: %s", persist_dir)
    return client

