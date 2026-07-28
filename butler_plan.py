# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from team_system_v2 import Project, RoleType, TaskStatus, Priority

p = Project('AI知库 - 企业智能知识管家', '面向中小企业的一站式RAG知识库问答系统')
p.recruit_team()

# 第1阶段
p.create_phase('基础架构搭建')
p.add_task('项目初始化与工程结构', u'创建FastAPI项目骨架、目录、依赖管理', priority=Priority.URGENT, phase_index=0, estimated_hours=4)
p.add_task('数据库表设计与初始化', u'SQLite表创建、ChromaDB初始化', priority=Priority.URGENT, phase_index=0, estimated_hours=6)
p.add_task('Docker化基础设施', u'Dockerfile + docker-compose + Nginx', priority=Priority.MEDIUM, phase_index=0, estimated_hours=8)

# 第2阶段
p.create_phase('核心RAG引擎开发')
p.add_task('文档解析引擎', u'PDF/Word/Excel/MD/TXT解析+智能分块', priority=Priority.HIGH, phase_index=1, estimated_hours=16)
p.add_task('向量化与索引服务', u'BGE嵌入+ChromaDB读写+索引管理', priority=Priority.HIGH, phase_index=1, estimated_hours=12)
p.add_task('RAG问答管道', u'检索+排序+LLM生成+多轮对话+引用溯源', priority=Priority.URGENT, phase_index=1, estimated_hours=20)

# 第3阶段
p.create_phase('API服务开发')
p.add_task('知识库管理API', u'CRUD知识库+文档上传/删除+状态查询', priority=Priority.HIGH, phase_index=2, estimated_hours=10)
p.add_task('问答API', u'提问接口+流式输出SSE+历史对话', priority=Priority.HIGH, phase_index=2, estimated_hours=12)
p.add_task('系统设置API', u'LLM+嵌入+分块参数配置', priority=Priority.MEDIUM, phase_index=2, estimated_hours=6)

# 第4阶段
p.create_phase('前端界面开发')
p.add_task('前端项目初始化与布局', u'Next.js+Tailwind+路由+组件库', priority=Priority.HIGH, phase_index=3, estimated_hours=8)
p.add_task('知识库管理页面', u'列表/创建/删除知识库+文档拖拽上传', priority=Priority.HIGH, phase_index=3, estimated_hours=12)
p.add_task('智能问答对话页面', u'对话界面+流式渲染+引用+追问', priority=Priority.URGENT, phase_index=3, estimated_hours=16)
p.add_task('系统设置页面', u'LLM配置表单+模型测试+参数设置', priority=Priority.MEDIUM, phase_index=3, estimated_hours=8)

# 第5阶段
p.create_phase('测试验证与部署')
p.add_task('单元测试与集成测试', u'后端API+RAG管道+前端组件测试', priority=Priority.HIGH, phase_index=4, estimated_hours=16)
p.add_task('性能优化与安全加固', u'检索延迟优化+并发+安全', priority=Priority.HIGH, phase_index=4, estimated_hours=10)
p.add_task('文档编写与一键部署', u'API文档+用户手册+部署脚本', priority=Priority.MEDIUM, phase_index=4, estimated_hours=8)

# 分解关键子任务
doc_task = rag_task = None
for t in p.tasks.tasks.values():
    if t.title == u'文档解析引擎': doc_task = t
    if t.title == u'RAG问答管道': rag_task = t

if doc_task:
    p.decompose_task(doc_task.task_id, [
        {u'title': u'PDF解析模块(PyMuPDF)', u'estimated_hours': 4},
        {u'title': u'Word/Excel解析模块', u'estimated_hours': 4},
        {u'title': u'Markdown/纯文本解析', u'estimated_hours': 2},
        {u'title': u'智能分块策略(heading-aware)', u'estimated_hours': 4},
        {u'title': u'文档状态管理与异步管道', u'estimated_hours': 2},
    ])

if rag_task:
    p.decompose_task(rag_task.task_id, [
        {u'title': u'BGE嵌入集成与缓存', u'estimated_hours': 4},
        {u'title': u'ChromaDB语义检索', u'estimated_hours': 4},
        {u'title': u'MMR重排序', u'estimated_hours': 3},
        {u'title': u'LLM提示词模板', u'estimated_hours': 3},
        {u'title': u'多轮对话上下文管理', u'estimated_hours': 3},
        {u'title': u'引用溯源与格式化输出', u'estimated_hours': 3},
    ])

# 分配任务
assignments = [
    (u'项目初始化与工程结构', RoleType.BUTLER),
    (u'数据库表设计与初始化', RoleType.DATA_ENGINEER),
    (u'Docker化基础设施', RoleType.DEVELOPER),
    (u'文档解析引擎', RoleType.DEVELOPER),
    (u'向量化与索引服务', RoleType.DATA_ENGINEER),
    (u'RAG问答管道', RoleType.DEVELOPER),
    (u'知识库管理API', RoleType.DEVELOPER),
    (u'问答API', RoleType.DEVELOPER),
    (u'系统设置API', RoleType.DEVELOPER),
    (u'前端项目初始化与布局', RoleType.CREATIVE),
    (u'知识库管理页面', RoleType.CREATIVE),
    (u'智能问答对话页面', RoleType.CREATIVE),
    (u'系统设置页面', RoleType.CREATIVE),
    (u'单元测试与集成测试', RoleType.TESTER),
    (u'性能优化与安全加固', RoleType.ARCHITECT),
    (u'文档编写与一键部署', RoleType.BUTLER),
]
for title, role in assignments:
    for t in p.tasks.tasks.values():
        if t.title == title:
            p.assign_task(t.task_id, role_type=role)
            break

print('')
print(p.report())
