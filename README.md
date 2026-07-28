# 🧠 AI知库 - 企业智能知识管家

> RAG 知识库问答系统 · 零成本部署 · 开源免费

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

---

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 📄 **多格式支持** | PDF / Word / Excel / Markdown / TXT / HTML |
| ✂️ **智能分块** | Heading-aware / Semantic / Fixed 三种策略 |
| 🔍 **语义检索** | BGE嵌入 + MMR重排序，精准召回 |
| 🤖 **多LLM支持** | OpenAI / Ollama本地部署 / 兼容API |
| 🌐 **Web界面** | 开箱即用的对话式UI，无需额外配置 |
| 🐳 **Docker部署** | 一键启动，5分钟上线 |
| 🎯 **零依赖运行** | Mock模式无需GPU/API Key即可体验 |

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r aiknow/requirements.txt

# 2. 初始化
python aiknow/scripts/init.py

# 3. 启动服务
python aiknow/run.py

# 4. 访问
# Web界面: http://localhost:8000/ui
# API文档: http://localhost:8000/docs
```

> **无需API Key！** 系统默认以Mock模式运行，可直接体验完整RAG流程。

## 🐳 Docker部署

```bash
docker-compose -f aiknow/docker-compose.yml up -d
```

## 📊 项目结构

```
├── aiknow/
│   ├── app/
│   │   ├── rag/          # RAG引擎核心
│   │   │   ├── loader.py     # 文档加载器
│   │   │   ├── chunker.py    # 智能分块
│   │   │   ├── embeddings.py # 嵌入服务
│   │   │   ├── retriever.py  # 语义检索
│   │   │   ├── generator.py  # 答案生成
│   │   │   └── pipeline.py   # 管道编排
│   │   ├── api/          # FastAPI服务
│   │   ├── storage/      # 数据存储
│   │   └── web_ui.py     # Web界面
│   ├── scripts/          # 工具脚本
│   ├── tests/            # 单元测试
│   └── config.yaml       # 配置文件
├── team_system_v2.py     # 团队管理系统
├── butler_plan.py        # 项目规划
└── cli.py                # 交互式CLI
```

## 📈 测试

```bash
# 运行单元测试
python aiknow/tests/test_rag.py

# 运行API测试
python aiknow/tests/test_api.py
```

## 💰 收益模式

| 模式 | 定价 | 说明 |
|------|------|------|
| 开源版 | 免费 | 社区使用 |
| 企业私有化 | ¥3,000-8,000/次 | 提供部署+技术支持 |
| SaaS云托管 | ¥99/月 | 托管服务 |
| 定制开发 | ¥10,000-50,000 | 按需定制 |

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)