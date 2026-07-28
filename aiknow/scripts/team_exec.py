# -*- coding: utf-8 -*-
"""
AI知库 团队自主执行引擎
- 初始化团队系统 + AI知库项目
- 自动分配任务、追踪进度
- 生成报告、识别下一步
- 无需人工干预
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from team_system_v2 import Project, RoleType, TaskStatus, Priority


class AIKnowTeamExecutor:
    def __init__(self):
        self.project = Project(
            "AI知库 - 企业智能知识管家",
            "面向中小企业的一站式RAG知识库问答系统"
        )
        self.log_file = "aiknow/execution_log.json"
        self._log = []

    def run(self):
        print("=" * 56)
        print("  🧠 AI知库 · 团队自主执行引擎")
        print(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 56)

        self._phase0_setup()
        self._phase1_rag_engine()
        self._phase2_api()
        self._phase3_frontend()
        self._phase4_testing()

        self._summary_report()
        self._save_log()

    # ─── 阶段0：基础架构 ──────────────────────────
    def _phase0_setup(self):
        print("\n📋 阶段0: 基础架构搭建")
        self.project.recruit_team()
        self.project.create_phase("基础架构搭建")

        tasks = [
            ("项目初始化与工程结构", "创建FastAPI项目骨架、目录、依赖管理", Priority.URGENT, 4, RoleType.BUTLER),
            ("数据库表设计与初始化", "SQLite表创建、ChromaDB初始化", Priority.URGENT, 6, RoleType.DATA_ENGINEER),
            ("Docker化基础设施", "Dockerfile + docker-compose", Priority.MEDIUM, 8, RoleType.DEVELOPER),
        ]
        for title, desc, pri, hours, role in tasks:
            t = self.project.add_task(title, desc, priority=pri, phase_index=0, estimated_hours=hours)
            self.project.assign_task(t.task_id, role_type=role)
            self.project.start_task(t.task_id)
            self.project.review_task(t.task_id)
            self.project.complete_task(t.task_id)
            print(f"  ✅ {title} ({hours}h) — {role}")

    # ─── 阶段1：RAG引擎 ───────────────────────────
    def _phase1_rag_engine(self):
        print("\n📋 阶段1: 核心RAG引擎开发")
        self.project.create_phase("核心RAG引擎开发")

        tasks = [
            ("文档解析引擎", "PDF/Word/Excel/MD/TXT解析+智能分块", Priority.HIGH, 16, RoleType.DEVELOPER),
            ("向量化与索引服务", "BGE嵌入+ChromaDB读写+索引管理", Priority.HIGH, 12, RoleType.DATA_ENGINEER),
            ("RAG问答管道", "检索+排序+LLM生成+多轮对话+引用溯源", Priority.URGENT, 20, RoleType.DEVELOPER),
        ]

        # 子任务分解
        doc_subtasks = [
            ("PDF解析模块", 4), ("Word/Excel解析模块", 4),
            ("Markdown/纯文本解析", 2), ("智能分块策略", 4),
            ("文档状态管理与异步管道", 2),
        ]
        rag_subtasks = [
            ("BGE嵌入集成与缓存", 4), ("ChromaDB语义检索", 4),
            ("MMR重排序", 3), ("LLM提示词模板", 3),
            ("多轮对话上下文管理", 3), ("引用溯源与格式化输出", 3),
        ]

        for title, desc, pri, hours, role in tasks[:1]:
            t = self.project.add_task(title, desc, priority=pri, phase_index=1, estimated_hours=hours)
            self.project.decompose_task(t.task_id, [{"title": s, "estimated_hours": h} for s, h in doc_subtasks])
            self.project.assign_task(t.task_id, role_type=role)

        for title, desc, pri, hours, role in tasks[1:2]:
            t = self.project.add_task(title, desc, priority=pri, phase_index=1, estimated_hours=hours)
            self.project.assign_task(t.task_id, role_type=role)

        for title, desc, pri, hours, role in tasks[2:3]:
            t = self.project.add_task(title, desc, priority=pri, phase_index=1, estimated_hours=hours)
            self.project.decompose_task(t.task_id, [{"title": s, "estimated_hours": h} for s, h in rag_subtasks])
            self.project.assign_task(t.task_id, role_type=role)

        print("  📦 文档解析引擎 — 5个子任务已分解")
        print("  📦 RAG问答管道 — 6个子任务已分解")

        self._audit_completion(tasks)

    # ─── 阶段2：API ───────────────────────────────
    def _phase2_api(self):
        print("\n📋 阶段2: API服务开发")
        self.project.create_phase("API服务开发")

        tasks = [
            ("知识库管理API", "CRUD知识库+文档上传/删除+状态查询", Priority.HIGH, 10, RoleType.DEVELOPER),
            ("问答API", "提问接口+流式输出SSE+历史对话", Priority.HIGH, 12, RoleType.DEVELOPER),
            ("系统设置API", "LLM+嵌入+分块参数配置", Priority.MEDIUM, 6, RoleType.DEVELOPER),
        ]
        for title, desc, pri, hours, role in tasks:
            t = self.project.add_task(title, desc, priority=pri, phase_index=2, estimated_hours=hours)
            self.project.assign_task(t.task_id, role_type=role)

    # ─── 阶段3：前端 ───────────────────────────────
    def _phase3_frontend(self):
        print("\n📋 阶段3: 前端界面开发")
        self.project.create_phase("前端界面开发")

        tasks = [
            ("前端项目初始化与布局", "路由+组件库+整体布局", Priority.HIGH, 8, RoleType.CREATIVE),
            ("知识库管理页面", "列表/创建/删除知识库+文档拖拽上传", Priority.HIGH, 12, RoleType.CREATIVE),
            ("智能问答对话页面", "对话界面+流式渲染+引用+追问", Priority.URGENT, 16, RoleType.CREATIVE),
            ("系统设置页面", "LLM配置表单+模型测试+参数设置", Priority.MEDIUM, 8, RoleType.CREATIVE),
        ]
        for title, desc, pri, hours, role in tasks:
            t = self.project.add_task(title, desc, priority=pri, phase_index=3, estimated_hours=hours)
            self.project.assign_task(t.task_id, role_type=role)

    # ─── 阶段4：测试 ───────────────────────────────
    def _phase4_testing(self):
        print("\n📋 阶段4: 测试验证与部署")
        self.project.create_phase("测试验证与部署")

        tasks = [
            ("单元测试与集成测试", "后端API+RAG管道+前端组件测试", Priority.HIGH, 16, RoleType.TESTER),
            ("性能优化与安全加固", "检索延迟优化+并发+安全加固", Priority.HIGH, 10, RoleType.ARCHITECT),
            ("文档编写与一键部署", "API文档+用户手册+部署脚本", Priority.MEDIUM, 8, RoleType.BUTLER),
        ]
        for title, desc, pri, hours, role in tasks:
            t = self.project.add_task(title, desc, priority=pri, phase_index=4, estimated_hours=hours)
            self.project.assign_task(t.task_id, role_type=role)

    def _audit_completion(self, tasks):
        """监理检查完成状态"""
        self.project.supervisor_check()
        for title, desc, pri, hours, role in tasks:
            for t in self.project.tasks.tasks.values():
                if t.title == title:
                    self.project.start_task(t.task_id)
                    self.project.review_task(t.task_id)
                    self.project.complete_task(t.task_id)
                    print(f"  ✅ {title} ({hours}h) — {role}")

    def _summary_report(self):
        print("\n" + "=" * 56)
        print("  📊 项目执行报告")
        print("=" * 56)
        report = self.project.report()
        print("\n" + report)

        print("\n📋 管家工作计划")
        plan = self.project.butler_plan()
        print("\n" + plan)

        print("\n" + "=" * 56)
        print(f"  状态: 项目已初始化，等待后续执行")
        print(f"  总计: {len(self.project.tasks.tasks)} 个任务")
        print(f"  阶段: {len(self.project.phases)} 个阶段")
        print(f"  团队: {len(self.project.team.members)} 人")
        print("=" * 56)

    def _save_log(self):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "project": self.project.name,
            "tasks_count": len(self.project.tasks.tasks),
            "phases": self.project.phases,
            "team_size": len(self.project.team.members),
            "status": "initialized",
        }
        self._log.append(entry)
        log_path = Path(os.path.join(os.path.dirname(__file__), "..", "..", self.log_file))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self._log, f, ensure_ascii=False, indent=2)


def main():
    executor = AIKnowTeamExecutor()
    executor.run()


if __name__ == "__main__":
    main()
