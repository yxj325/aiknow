# -*- coding: utf-8 -*-
"""
FastAPI 服务 - AI知库 API
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.pipeline import RAGPipeline
from app.storage.db import KnowledgeBase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_config(path: str = None) -> dict:
    if not path:
        path = os.environ.get("AIKNOW_CONFIG", "config.yaml")
        # 向上搜索
        search = Path(os.path.abspath(__file__)).parent.parent.parent / "config.yaml"
        if search.exists():
            path = str(search)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


config = load_config()
pipeline = RAGPipeline(config)
kb_store = KnowledgeBase(config.get("storage", {}).get("sqlite_path", "data/aiknow.db"))

app = FastAPI(title="AI知库 API", version="2.0.0",
              description="企业智能知识管家 - RAG知识库问答系统")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = os.environ.get("AIKNOW_UPLOAD", "data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"service": "AI知库 - 企业智能知识管家", "version": "2.0.0",
            "stats": pipeline.stats}


@app.get("/health")
async def health():
    return {"status": "ok", "chunks": len(pipeline._chunks)}


# ─── 知识库管理 ──────────────────────────────────
@app.post("/api/kb")
async def create_kb(name: str, description: str = ""):
    kb_id = kb_store.create_kb(name, description)
    return {"id": kb_id, "name": name, "message": "创建成功"}


@app.get("/api/kb")
async def list_kb():
    return kb_store.list_kbs()


@app.delete("/api/kb/{kb_id}")
async def delete_kb(kb_id: int):
    kb_store.delete_kb(kb_id)
    return {"message": "删除成功"}


# ─── 文档管理 ────────────────────────────────────
@app.post("/api/kb/{kb_id}/upload")
async def upload_document(kb_id: int, file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    chunks = pipeline.ingest(filepath)
    doc_id = kb_store.add_document(kb_id, file.filename, filepath,
                                    filetype=os.path.splitext(file.filename)[1],
                                    chunks=chunks)
    return {"id": doc_id, "filename": file.filename, "chunks": chunks, "message": "上传并索引成功"}


@app.get("/api/kb/{kb_id}/documents")
async def list_documents(kb_id: int):
    return kb_store.list_documents(kb_id)


# ─── 问答 ────────────────────────────────────────
@app.post("/api/ask")
async def ask(query: str, kb_id: int = None, session_id: str = "default"):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    result = pipeline.query(query)
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    tokens = result.get("tokens_used", 0)
    if kb_id:
        kb_store.save_conversation(kb_id, session_id, query, answer, sources, tokens)
    return {"query": query, "answer": answer, "sources": sources,
            "tokens_used": tokens, "stats": pipeline.stats}


@app.post("/api/ask/stream")
async def ask_stream(query: str, kb_id: int = None, session_id: str = "default"):
    """流式问答 - 使用SSE"""
    from fastapi.responses import StreamingResponse
    import asyncio
    async def event_stream():
        result = pipeline.query(query)
        answer = result.get("answer", "")
        for char in answer:
            yield f"data: {char}\n\n"
            await asyncio.sleep(0.01)
        yield f"data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/conversations/{session_id}")
async def get_conversations(session_id: str):
    return kb_store.get_conversations(session_id)


# ─── 管理 ────────────────────────────────────────
@app.post("/api/reset")
async def reset_knowledge_base():
    pipeline.reset()
    return {"message": "知识库已重置"}


@app.get("/api/stats")
async def get_stats():
    return pipeline.stats



@app.get("/ui", response_class=HTMLResponse)
@app.get("/web", response_class=HTMLResponse)
async def web_ui():
    return r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI知库 - 企业智能知识管家</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
body{background:#f0f2f5;min-height:100vh}
.app{display:flex;flex-direction:column;height:100vh}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:16px 24px;box-shadow:0 2px 8px rgba(0,0,0,.15)}
.header h1{font-size:20px;font-weight:600;display:flex;align-items:center;gap:8px}
.main{display:flex;flex:1;overflow:hidden}
.sidebar{width:260px;background:#fff;border-right:1px solid #e8e8e8;display:flex;flex-direction:column}
.chat-area{flex:1;display:flex;flex-direction:column}
.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.message{max-width:75%;padding:12px 16px;border-radius:12px;font-size:14px;line-height:1.6}
.user{background:#667eea;color:#fff;align-self:flex-end}
.bot{background:#fff;color:#333;align-self:flex-start;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.input-area{display:flex;padding:16px 20px;background:#fff;border-top:1px solid #e8e8e8;gap:8px}
.input-area input{flex:1;padding:10px 16px;border:1px solid #ddd;border-radius:8px;font-size:14px;outline:none}
.input-area input:focus{border-color:#667eea}
.input-area button{padding:10px 24px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:8px;cursor:pointer}
.kb-section{padding:16px;border-bottom:1px solid #e8e8e8}
.kb-section h3{font-size:13px;color:#666;margin-bottom:8px}
.upload-area{padding:16px;font-size:13px;color:#999}
.empty-state{flex:1;display:flex;align-items:center;justify-content:center;color:#ccc;font-size:16px}
</style>
</head>
<body>
<div class="app">
<div class="header"><h1>🧠 AI知库 <span style="font-size:13px;opacity:.8;margin-left:8px">企业智能知识管家</span></h1></div>
<div class="main">
<div class="sidebar">
<div class="kb-section"><h3>📚 知识库</h3><p id="kbStatus" style="font-size:13px;color:#999">默认知识库</p></div>
<div class="upload-area"><label for="fileInput" style="display:block;padding:8px;border:2px dashed #ddd;border-radius:8px;text-align:center;cursor:pointer">📤 上传文档</label>
<input type="file" id="fileInput" accept=".pdf,.docx,.md,.txt" multiple style="display:none">
<p id="status" style="margin-top:8px;font-size:12px;color:#999"></p></div>
</div>
<div class="chat-area">
<div class="messages" id="messages"><div class="empty-state">💬 上传文档后开始提问</div></div>
<div class="input-area">
<input type="text" id="queryInput" placeholder="输入问题..." onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">发送</button></div></div></div>
<script>
let sessionId='sess_'+Date.now();
document.getElementById('fileInput').onchange=async function(e){
  for(const f of e.target.files){
    document.getElementById('status').textContent='上传中: '+f.name;
    const fd=new FormData();fd.append('file',f);
    await fetch('/api/kb/1/upload',{method:'POST',body:fd});
    document.getElementById('status').textContent='✅ '+f.name+' 上传成功';
  }
};
async function send(){
  const inp=document.getElementById('queryInput');
  const q=inp.value.trim();if(!q)return;
  inp.value='';const m=document.getElementById('messages');
  const empty=m.querySelector('.empty-state');if(empty)empty.remove();
  m.innerHTML+='<div class="message user">'+q+'</div>';
  m.innerHTML+='<div class="message bot" id="loading">⏳ 思考中...</div>';
  const r=await fetch('/api/ask?query='+encodeURIComponent(q)+'&session_id='+sessionId);
  const d=await r.json();
  document.getElementById('loading').outerHTML='<div class="message bot">'+d.answer+'</div>';
  m.scrollTop=m.scrollHeight;
}
</script></body></html>"""

def main():
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8000)
    logger.info("启动 AI知库 API: http://%s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()


