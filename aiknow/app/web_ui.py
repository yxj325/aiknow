# -*- coding: utf-8 -*-
"""
AI知库 Web UI - 单页应用
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI知库 - 企业智能知识管家</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
body{background:#f0f2f5;min-height:100vh;display:flex;flex-direction:column}
.app{display:flex;flex-direction:column;height:100vh}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,.15)}
.header h1{font-size:20px;font-weight:600;display:flex;align-items:center;gap:8px}
.header .subtitle{font-size:12px;opacity:.8;margin-left:8px}
.sidebar{width:280px;background:#fff;border-right:1px solid #e8e8e8;display:flex;flex-direction:column;flex-shrink:0}
.main{display:flex;flex:1;overflow:hidden}
.chat-area{flex:1;display:flex;flex-direction:background:#f8f9fa}
.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.message{max-width:75%;padding:12px 16px;border-radius:12px;font-size:14px;line-height:1.6;animation:fadeIn .3s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.user{background:#667eea;color:#fff;align-self:flex-end;border-bottom-right-radius:4px}
.bot{background:#fff;color:#333;align-self:flex-start;border-bottom-left-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.bot .sources{font-size:12px;color:#999;margin-top:8px;padding-top:8px;border-top:1px solid #eee}
.bot .sources span{display:inline-block;background:#f0f2f5;padding:2px 8px;border-radius:4px;margin:2px}
.input-area{display:flex;padding:16px 20px;background:#fff;border-top:1px solid #e8e8e8;gap:8px}
.input-area input{flex:1;padding:10px 16px;border:1px solid #ddd;border-radius:8px;font-size:14px;outline:none;transition:border .2s}
.input-area input:focus{border-color:#667eea}
.input-area button{padding:10px 24px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;transition:opacity .2s}
.input-area button:hover{opacity:.9}
.input-area button:disabled{opacity:.5;cursor:not-allowed}
.kb-section{padding:16px}
.kb-section h3{font-size:14px;color:#666;margin-bottom:8px}
.kb-list{list-style:none;display:flex;flex-direction:column;gap:4px}
.kb-list li{padding:8px 12px;border-radius:6px;cursor:pointer;font-size:13px;transition:background .2s}
.kb-list li:hover{background:#f0f2f5}
.kb-list li.active{background:#667eea;color:#fff}
.upload-area{padding:12px 16px;border-top:1px solid #e8e8e8}
.upload-area label{display:block;padding:8px;text-align:center;border:2px dashed #ddd;border-radius:8px;cursor:pointer;font-size:13px;color:#999;transition:all .2s}
.upload-area label:hover{border-color:#667eea;color:#667eea}
.typing-indicator{display:flex;gap:4px;padding:4px 0}
.typing-dot{width:8px;height:8px;background:#ccc;border-radius:50%;animation:bounce 1.4s infinite ease-in-out}
.typing-dot:nth-child(2){animation-delay:.2s}
.typing-dot:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:scale(.6)}40%{transform:scale(1)}}
.empty-state{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#bbb;gap:8px}
.empty-state .icon{font-size:48px}
.empty-state p{font-size:14px}
</style>
</head>
<body>
<div class="app">
<div class="header">
<div><h1>🧠 AI知库 <span class="subtitle">企业智能知识管家</span></h1></div>
<div style="font-size:13px;opacity:.9" id="kbName">默认知识库</div>
</div>
<div class="main">
<div class="sidebar">
<div class="kb-section">
<h3>📚 知识库列表</h3>
<ul class="kb-list" id="kbList">
<li class="active" onclick="selectKB('default',this)">📁 默认知识库</li>
</ul>
</div>
<div class="upload-area">
<label for="fileInput">📤 上传文档（PDF/Word/MD/TXT）</label>
<input type="file" id="fileInput" accept=".pdf,.docx,.doc,.xlsx,.xls,.md,.txt" multiple style="display:none">
<div style="margin-top:8px;font-size:12px;color:#999;text-align:center" id="uploadStatus"></div>
</div>
<div class="kb-section" style="flex:1;overflow-y:auto">
<h3>📋 已索引文档</h3>
<ul class="kb-list" id="docList"></ul>
</div>
</div>
<div class="chat-area">
<div class="messages" id="messages">
<div class="empty-state">
<div class="icon">💬</div>
<p>上传文档后，向AI知库提问</p>
</div>
</div>
<div class="input-area">
<input type="text" id="queryInput" placeholder="输入问题，基于知识库智能回答..." onkeydown="if(event.key==='Enter')sendQuery()">
<button id="sendBtn" onclick="sendQuery()">发送</button>
</div>
</div>
</div>
</div>
<script>
let currentKB = "default";
let sessionId = "sess_" + Date.now();

// 加载知识库列表
async function loadKBs() {
    try {
        const r = await fetch("/api/kb");
        const kbs = await r.json();
        const list = document.getElementById("kbList");
        list.innerHTML = `<li class="${currentKB==='default'?'active':''}" onclick="selectKB('default',this)">📁 默认知识库</li>`;
        kbs.forEach(kb => {
            const li = document.createElement("li");
            li.textContent = "📁 " + kb.name;
            li.onclick = () => selectKB(kb.id, li);
            if (kb.id == currentKB) li.className = "active";
            list.appendChild(li);
        });
    } catch(e) {}
}

async function selectKB(id, el) {
    document.querySelectorAll("#kbList li").forEach(l => l.className = "");
    el.className = "active";
    currentKB = id;
    document.getElementById("kbName").textContent = el.textContent;
    loadDocuments();
}

async function loadDocuments() {
    if (currentKB === "default") return;
    try {
        const r = await fetch(`/api/kb/${currentKB}/documents`);
        const docs = await r.json();
        const list = document.getElementById("docList");
        list.innerHTML = docs.map(d => `<li>📄 ${d.filename} <span style="color:#999;font-size:11px">(${d.chunk_count}块)</span></li>`).join("");
    } catch(e) {}
}

// 上传文档
document.getElementById("fileInput").onchange = async function(e) {
    const status = document.getElementById("uploadStatus");
    for (const file of e.target.files) {
        status.textContent = `上传中: ${file.name}...`;
        const form = new FormData();
        form.append("file", file);
        try {
            const kbId = currentKB === "default" ? 1 : currentKB;
            const r = await fetch(`/api/kb/${kbId}/upload`, {method:"POST", body:form});
            const data = await r.json();
            status.textContent = `✅ ${data.filename} (${data.chunks}块)`;
            loadDocuments();
        } catch(err) {
            status.textContent = `❌ ${file.name} 失败`;
        }
    }
};

// 问答
async function sendQuery() {
    const input = document.getElementById("queryInput");
    const btn = document.getElementById("sendBtn");
    const query = input.value.trim();
    if (!query) return;

    input.value = "";
    btn.disabled = true;
    addMessage("user", query);

    const typingId = addTyping();

    try {
        const r = await fetch(`/api/ask?query=${encodeURIComponent(query)}&kb_id=${currentKB}&session_id=${sessionId}`);
        const data = await r.json();
        removeTyping(typingId);
        const sources = data.sources || [];
        addMessage("bot", data.answer, sources);
    } catch(e) {
        removeTyping(typingId);
        addMessage("bot", "抱歉，请求失败，请重试。");
    }
    btn.disabled = false;
}

function addMessage(role, text, sources) {
    const msgs = document.getElementById("messages");
    const empty = msgs.querySelector(".empty-state");
    if (empty) empty.remove();

    const div = document.createElement("div");
    div.className = "message " + role;
    div.textContent = text;

    if (sources && sources.length) {
        const src = document.createElement("div");
        src.className = "sources";
        src.innerHTML = "📎 来源: " + sources.map(s => `<span>${s.source || s.page || "?"}</span>`).join("");
        div.appendChild(src);
    }

    // 支持markdown风格的代码块和链接
    div.innerHTML = div.innerHTML
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');

    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
}

function addTyping() {
    const msgs = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "message bot";
    div.id = "typing_" + Date.now();
    div.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div.id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

loadKBs();
</script>
</body>
</html>"""


from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn


def create_app() -> FastAPI:
    from .main import app
    @app.get("/ui", response_class=HTMLResponse)
    async def web_ui():
        return HTML
    @app.get("/web", response_class=HTMLResponse)
    async def web_ui_alt():
        return HTML
    return app


def serve(host: str = "0.0.0.0", port: int = 8000):
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    serve()
