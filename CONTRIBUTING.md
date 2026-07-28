# 贡献指南

## 开发环境

```bash
pip install -r aiknow/requirements.txt
python aiknow/scripts/init.py
```

## 代码规范

- 遵循 PEP 8
- 中文字符串使用 Unicode
- 模块级 docstring 说明功能

## 提交流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交改动 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 测试

```bash
python aiknow/tests/test_rag.py  # RAG引擎测试
python aiknow/tests/test_api.py  # API测试
```

所有测试通过后方可合并。