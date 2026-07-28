# -*- coding: utf-8 -*-
"""AI知库 API 集成测试"""
import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'aiknow')
os.environ['AIKNOW_CONFIG'] = 'config.yaml'

from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

tests = [
    ("GET", "/health", None, "健康检查"),
    ("POST", "/api/kb", {"name": "测试知识库", "description": "API测试"}, "创建知识库"),
    ("GET", "/api/kb", None, "列表知识库"),
    ("GET", "/api/stats", None, "引擎状态"),
    ("POST", "/api/ask", {"query": "RAG技术是什么？"}, "问答接口"),
    ("GET", "/ui", None, "Web界面"),
]

for method, path, params, label in tests:
    try:
        data = {}
        if params:
            data = params
        if method == "GET":
            r = client.get(path)
        else:
            r = client.post(path, params=data if isinstance(data, dict) else {})
        
        result = r.json() if r.headers.get("content-type","").startswith("application/json") else {"html": f"{len(r.text)} bytes"}
        status = "OK" if r.status_code in (200, 201) else "FAIL"
        print(f"  [{status}] {label}: {r.status_code}")
        if isinstance(result, dict) and "answer" in result:
            print(f"    回答: {result['answer'][:60]}...")
        elif "html" in result:
            pass
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")

print()
print("API 集成测试完成。")
print(f"总路由: {len(app.routes)}")
