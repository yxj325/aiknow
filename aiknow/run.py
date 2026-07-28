# -*- coding: utf-8 -*-
"""
AI知库 - 启动入口
"""
import os
import sys
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print("🧠 AI知库 - 企业智能知识管家")
    print(f"   访问: http://localhost:{port}/ui")
    print(f"   API:  http://localhost:{port}/docs")
    uvicorn.run("app.api.main:app", host=host, port=port, reload=True)
