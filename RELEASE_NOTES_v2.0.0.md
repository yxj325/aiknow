# AI知库 v2.0.0 Release Notes

> 发布日期: 2026-07-29

## 🎉 新特性

- **多格式文档加载器**: 支持 PDF / Word / Excel / Markdown / HTML / 纯文本
- **智能分块引擎**: Heading-aware / Semantic / Fixed 三种分块策略
- **语义检索系统**: BGE 中文嵌入 + MMR 重排序
- **多 LLM 支持**: OpenAI / Ollama 本地部署 / Mock 模式
- **FastAPI 服务**: 18 条 API 路由，支持 SSE 流式输出
- **对话式 Web UI**: 拖拽上传文档，开箱即用
- **Docker 一键部署**: Dockerfile + docker-compose.yml
- **团队管理系统**: 7 角色自主任务管理

## 🚀 快速开始

```bash
pip install -r aiknow/requirements.txt
python aiknow/run.py
# 访问 http://localhost:8000/ui
```

## 📦 模块结构

- `app/rag/` - RAG 引擎核心 (loader / chunker / embeddings / retriever / generator / pipeline)
- `app/api/` - FastAPI 服务
- `app/storage/` - SQLite + ChromaDB 存储层
- `tests/` - 19 单元测试 + 6 集成测试

## ⚙️ 系统要求

- Python 3.10+
- 可选: sentence-transformers (嵌入模型)
- 可选: OpenAI API Key 或 Ollama (LLM)

## 📄 License

MIT License