# AI知库 - 企业智能知识管家

> 🧠 面向中小企业的零成本 RAG 知识库问答系统
> 
> **投入：¥0 | 收益：部署即用 | 完全自主运营**

## ✨ 特性

- **多格式文档** — PDF / Word / Excel / Markdown / TXT / HTML
- **智能分块** — Heading-aware / Semantic / Fixed 三种策略
- **语义检索** — BGE嵌入 + MMR重排序，精准召回
- **多LLM支持** — OpenAI / Ollama本地部署 / 兼容API
- **Web界面** — 开箱即用的对话式UI
- **Docker部署** — 一键启动，5分钟上线

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化
python scripts/init.py

# 3. 启动服务
python run.py

# 4. 访问
# Web界面: http://localhost:8000/ui
# API文档: http://localhost:8000/docs
```

## 🐳 Docker部署

```bash
docker-compose up -d
# 默认无LLM运行，需配置 OPENAI_API_KEY
docker-compose run --rm -e OPENAI_API_KEY=sk-xxx aiknow
```

## 📊 项目状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 文档加载器 | ✅ 完成 | PDF/Word/Excel/MD/TXT/HTML |
| 智能分块 | ✅ 完成 | heading/semantic/fixed |
| BGE嵌入 | ✅ 完成 | 缓存、批量编码 |
| 语义检索 | ✅ 完成 | MMR重排序 |
| 答案生成 | ✅ 完成 | OpenAI/Ollama |
| RAG管道 | ✅ 完成 | 全链路编排 |
| API服务 | ✅ 完成 | FastAPI + SSE流式 |
| Web界面 | ✅ 完成 | 单页对话应用 |
| 存储层 | ✅ 完成 | SQLite + ChromaDB |
| 团队系统 | ✅ 完成 | 7角色自主管理 |

## 💰 收益模式

| 模式 | 定价 | 目标 |
|------|------|------|
| 开源版 | 免费 | 社区推广 |
| 企业私有化 | ¥3,000-8,000/次 | 中小企业 |
| SaaS云托管 | ¥99/月 | 持续收入 |
| 定制开发 | ¥10,000-50,000 | 大型企业 |

## 🏗️ 架构

```
aiknow/
├── app/
│   ├── rag/          # RAG引擎核心
│   │   ├── loader.py    # 文档加载
│   │   ├── chunker.py   # 智能分块
│   │   ├── embeddings.py # BGE嵌入
│   │   ├── retriever.py  # 语义检索
│   │   ├── generator.py  # LLM生成
│   │   └── pipeline.py   # 管道编排
│   ├── api/          # FastAPI服务
│   │   └── main.py      # API路由
│   ├── storage/      # 数据存储
│   │   └── db.py        # SQLite+ChromaDB
│   └── web_ui.py     # Web界面
├── scripts/          # 工具脚本
├── Dockerfile
└── docker-compose.yml
```

## 🤖 自主运营

本项目由「研发团队管理系统 v2.0」自主管理执行：

```bash
python aiknow/scripts/team_exec.py
```
