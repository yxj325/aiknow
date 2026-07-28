# -*- coding: utf-8 -*-
"""
研发团队管理系统 v2.0
一站式研发团队管理工具
角色：管家 · 创意 · 数据工程师 · 监理 · 开发 · 测试 · 架构
"""

import sys
import os
from datetime import datetime

# ─── 编码修复 ─────────────────────────────────────
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

IS_PY2 = sys.version_info[0] < 3

def u(text):
    """统一返回 unicode"""
    if IS_PY2 and isinstance(text, str):
        return text.decode('utf-8')
    return text

# ─── 角色定义 ─────────────────────────────────────
class RoleType:
    BUTLER = u("管家")
    CREATIVE = u("创意")
    DATA_ENGINEER = u("数据工程师")
    SUPERVISOR = u("监理")
    DEVELOPER = u("开发工程师")
    TESTER = u("测试工程师")
    ARCHITECT = u("架构师")

    @classmethod
    def all(cls):
        return [v for k, v in cls.__dict__.items()
                if not k.startswith("_") and not callable(v)]

    @classmethod
    def from_name(cls, name):
        for v in cls.all():
            if v == name:
                return v
        return None


class Role:
    def __init__(self, role_type, name, description=""):
        self.role_type = role_type
        self.name = u(name)
        self.description = u(description) or self._default_desc()

    def _default_desc(self):
        descs = {
            RoleType.BUTLER: u("资源调度、进度跟踪、沟通协调"),
            RoleType.CREATIVE: u("方案创意、视觉设计、用户体验"),
            RoleType.DATA_ENGINEER: u("数据采集、清洗、分析、管道建设"),
            RoleType.SUPERVISOR: u("质量审查、风险监控、标准合规"),
            RoleType.DEVELOPER: u("代码实现、模块开发、技术落地"),
            RoleType.TESTER: u("测试用例、自动化测试、质量保障"),
            RoleType.ARCHITECT: u("系统架构设计、技术选型、评审"),
        }
        return descs.get(self.role_type, "")

    def __repr__(self):
        return "[%s]%s" % (self.role_type, self.name)


ROLE_TEMPLATES = {rt: Role(rt, rt) for rt in RoleType.all()}

# ─── 状态与优先级 ─────────────────────────────────
class TaskStatus:
    PENDING = u("待处理")
    IN_PROGRESS = u("进行中")
    REVIEW = u("审查中")
    DONE = u("已完成")
    BLOCKED = u("已阻塞")
    CANCELLED = u("已取消")


class Priority:
    LOW, MEDIUM, HIGH, URGENT = 1, 2, 3, 4

# ─── 团队成员 ─────────────────────────────────────
class TeamMember:
    def __init__(self, mid, name, role, workload=0):
        self.member_id = mid
        self.name = u(name)
        self.role = role
        self.workload = workload
        self.skills = []
        self.active = True

    def add_skill(self, skill):
        if skill not in self.skills:
            self.skills.append(skill)

    @property
    def is_available(self):
        return self.active and self.workload < 80

    def assign_work(self, load):
        if self.workload + load > 100:
            return False
        self.workload += load
        return True

    def __repr__(self):
        return "%s(%s)" % (self.name, self.role.role_type)


class Team:
    def __init__(self, name=None):
        self.name = u(name) if name else u("默认团队")
        self.members = {}
        self._next_id = 1

    def add_member(self, name, role_type, skills=None):
        mid = "M%03d" % self._next_id
        self._next_id += 1
        role = ROLE_TEMPLATES.get(role_type, Role(role_type, name))
        member = TeamMember(mid, name, role)
        for skill in (skills or []):
            member.add_skill(skill)
        self.members[mid] = member
        return member

    def get_by_role(self, role_type):
        return [m for m in self.members.values() if m.role.role_type == role_type]

    def get_available(self):
        return [m for m in self.members.values() if m.is_available]

    def summary(self):
        lines = [u("  >> 团队: %s") % self.name,
                 u("  >> 总人数: %d") % len(self.members)]
        for rt in RoleType.all():
            members = self.get_by_role(rt)
            if members:
                statuses = []
                for m in members:
                    if m.is_available:
                        statuses.append(u("%s(空闲)") % m.name)
                    else:
                        statuses.append(u("%s(负载%d%%)") % (m.name, m.workload))
                lines.append(u("    %s: %s") % (rt, u(" | ").join(statuses)))
        return u("\n").join(lines)


# ─── 任务定义 ─────────────────────────────────────
class Task:
    def __init__(self, title, description="", priority=Priority.MEDIUM,
                 status=None, parent_id=None, assignee_id=None,
                 role_required=None, estimated_hours=0.0,
                 tags=None, task_id=""):
        self.title = u(title)
        self.description = u(description)
        self.priority = priority
        self.status = status or TaskStatus.PENDING
        self.parent_id = parent_id
        self.subtasks = []
        self.assignee_id = assignee_id
        self.role_required = role_required
        self.dependencies = []
        self.depends_on = []
        self.estimated_hours = estimated_hours
        self.actual_hours = 0.0
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.created_at = now
        self.updated_at = now
        self.tags = tags or []
        self.task_id = task_id

    def __repr__(self):
        return "[%s]%s" % (self.task_id, self.title)


class TaskTree:
    def __init__(self):
        self.tasks = {}
        self._next_id = 1

    def create(self, title, description="", priority=Priority.MEDIUM,
               parent_id=None, assignee_id=None, role_required=None,
               estimated_hours=0.0, tags=None):
        tid = "T%04d" % self._next_id
        self._next_id += 1
        task = Task(title, description, priority,
                    parent_id=parent_id, assignee_id=assignee_id,
                    role_required=role_required,
                    estimated_hours=estimated_hours,
                    tags=tags or [], task_id=tid)
        self.tasks[tid] = task
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].subtasks.append(tid)
        return task

    def decompose(self, parent_id, subtasks_list):
        created = []
        for sub in subtasks_list:
            t = self.create(
                title=sub.get("title", ""),
                description=sub.get("description", ""),
                priority=sub.get("priority", Priority.MEDIUM),
                parent_id=parent_id,
                assignee_id=sub.get("assignee_id"),
                role_required=sub.get("role_required"),
                estimated_hours=sub.get("estimated_hours", 0.0),
            )
            created.append(t)
        return created

    def get_blockers(self, task_id):
        if task_id not in self.tasks:
            return []
        return [self.tasks[d] for d in self.tasks[task_id].dependencies
                if d in self.tasks and self.tasks[d].status != TaskStatus.DONE]

    def get_subtasks(self, task_id, recursive=False):
        if task_id not in self.tasks:
            return []
        result = []
        for sid in self.tasks[task_id].subtasks:
            if sid in self.tasks:
                result.append(self.tasks[sid])
                if recursive:
                    result.extend(self.get_subtasks(sid, True))
        return result

    def update_status(self, task_id, status):
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        if status == TaskStatus.IN_PROGRESS:
            blockers = self.get_blockers(task_id)
            if blockers:
                task.status = TaskStatus.BLOCKED
                self._print(u("  !! %s 被阻塞，依赖未完成:") % task.title)
                for b in blockers:
                    self._print(u("     - %s(%s)") % (b.title, b.status))
                return False
        task.status = status
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._print(u("  [%s] %s -> %s") % (task.task_id, task.title, status))
        return True

    def _print(self, msg):
        print(msg.encode('utf-8') if IS_PY2 else msg)

    def print_tree(self, task_id=None, indent=0):
        lines = []
        if task_id:
            ids = [task_id]
        else:
            ids = [t.task_id for t in self.tasks.values() if t.parent_id is None]
        for tid in ids:
            if tid not in self.tasks:
                continue
            t = self.tasks[tid]
            p = "  " * indent
            icons = {TaskStatus.PENDING: u("待"), TaskStatus.IN_PROGRESS: u("进"),
                     TaskStatus.REVIEW: u("审"), TaskStatus.DONE: u("完"),
                     TaskStatus.BLOCKED: u("阻")}
            ic = icons.get(t.status, u("-"))
            pri = {1: u("低"), 2: u("中"), 3: u("高"), 4: u("急")}.get(t.priority, u("?"))
            a = u(" -> %s") % t.assignee_id if t.assignee_id else u("")
            lines.append(u("%s[%s][%s%s] %s %s%s") % (p, ic, pri, t.task_id, t.title, t.task_id, a))
            for sid in t.subtasks:
                lines.append(self.print_tree(sid, indent + 1))
        return u("\n").join(lines)

    def summary(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE)
        ip = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        bl = sum(1 for t in self.tasks.values() if t.status == TaskStatus.BLOCKED)
        pe = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        return u("任务总览: %d个 | 完成:%d 进行:%d 待办:%d 阻塞:%d") % (total, done, ip, pe, bl)


# ─── 项目核心 ─────────────────────────────────────
class Project:
    def __init__(self, name, description=""):
        self.name = u(name)
        self.description = u(description)
        self.team = Team(self.name)
        self.tasks = TaskTree()
        self.phases = []
        self._logs = []

    def log(self, msg):
        msg = u(msg)
        self._logs.append(msg)
        print((u("  >> %s") % msg).encode('utf-8') if IS_PY2 else (u("  >> %s") % msg))

    # 团队
    def recruit_team(self):
        self.team.add_member(u("管家小艾"), RoleType.BUTLER, [u("协调"), u("规划")])
        self.team.add_member(u("创意总监阿创"), RoleType.CREATIVE, [u("UI设计"), u("头脑风暴")])
        self.team.add_member(u("数据老王"), RoleType.DATA_ENGINEER, [u("Python"), u("SQL"), u("ETL")])
        self.team.add_member(u("监理老张"), RoleType.SUPERVISOR, [u("代码审查"), u("质量检测")])
        self.team.add_member(u("开发小陈"), RoleType.DEVELOPER, [u("Python"), u("JavaScript")])
        self.team.add_member(u("测试小美"), RoleType.TESTER, [u("自动化测试"), u("功能测试")])
        self.team.add_member(u("架构师老李"), RoleType.ARCHITECT, [u("系统设计"), u("技术选型")])
        self.log(u("招募完成，7人研发团队已就位"))

    # 阶段
    def create_phase(self, name):
        self.phases.append(u(name))
        t = self.tasks.create(title=u("阶段: %s") % name,
                              priority=Priority.HIGH, tags=[u("phase")])
        self.log(u("创建阶段: %s [%s]") % (name, t.task_id))

    # 任务
    def add_task(self, title, description="", priority=Priority.MEDIUM,
                 phase_index=None, role_required=None, estimated_hours=0.0, tags=None):
        parent_id = None
        if phase_index is not None and phase_index < len(self.phases):
            for t in self.tasks.tasks.values():
                if t.title == u("阶段: %s") % self.phases[phase_index] and u("phase") in t.tags:
                    parent_id = t.task_id
                    break
        task = self.tasks.create(title=u(title), description=u(description),
                                 priority=priority, parent_id=parent_id,
                                 role_required=role_required,
                                 estimated_hours=estimated_hours, tags=tags or [])
        self.log(u("创建任务: %s [%s]") % (task.title, task.task_id))
        return task

    def decompose_task(self, task_id, subtasks_list):
        created = self.tasks.decompose(task_id, subtasks_list)
        self.log(u("分解任务 %s 为 %d 个子任务") % (task_id, len(created)))

    def assign_task(self, task_id, member_id=None, role_type=None):
        if task_id not in self.tasks.tasks:
            return False
        task = self.tasks.tasks[task_id]
        if role_type and not member_id:
            available = [m for m in self.team.get_by_role(role_type) if m.is_available]
            if not available:
                self.log(u("没有可用的 %s") % role_type)
                return False
            member = min(available, key=lambda m: m.workload)
            member_id = member.member_id
            load = max(5, int(task.estimated_hours / 8))
            member.assign_work(load)
            self.log(u("分配: %s -> %s(%s)") % (task.title, member.name, member.role.role_type))
        if member_id and member_id in self.team.members:
            task.assignee_id = member_id
            task.role_required = self.team.members[member_id].role.role_type
            return True
        return False

    def start_task(self, tid):
        return self.tasks.update_status(tid, TaskStatus.IN_PROGRESS)

    def review_task(self, tid):
        return self.tasks.update_status(tid, TaskStatus.REVIEW)

    def complete_task(self, tid):
        return self.tasks.update_status(tid, TaskStatus.DONE)

    def supervisor_check(self):
        issues = []
        for t in self.tasks.tasks.values():
            if t.status == TaskStatus.BLOCKED:
                issues.append(u("阻塞: %s 被依赖阻塞") % t.title)
        for m in self.team.members.values():
            if m.workload >= 80:
                issues.append(u("过载: %s 负载%d%%") % (m.name, m.workload))
        if not issues:
            self.log(u("监理审查通过，项目健康"))
        else:
            self.log(u("监理发现 %d 个问题:") % len(issues))
            for iss in issues:
                print((u("    %s") % iss).encode('utf-8') if IS_PY2 else iss)
        return issues

    def report(self):
        lines = [u("=" * 50),
                 u("项目报告: %s") % self.name,
                 u("=" * 50),
                 u("描述: %s") % self.description,
                 u("阶段: %s") % (u(", ").join(self.phases) if self.phases else u("无")),
                 u(""), self.team.summary(), u(""),
                 self.tasks.summary(), u(""),
                 u("任务树:"), self.tasks.print_tree(),
                 u(""), u("=" * 50)]
        return u("\n").join(lines)

    def butler_plan(self):
        lines = [u("管家工作计划:"), u("-" * 40)]
        pending = [t for t in self.tasks.tasks.values()
                   if t.status == TaskStatus.PENDING and t.parent_id]
        for t in sorted(pending, key=lambda x: x.priority, reverse=True):
            lines.append(u("  %s [优先级%d ~ %dh]") % (t.title, t.priority, int(t.estimated_hours)))
        ip = [t for t in self.tasks.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
        lines.append(u("进行中(%d):") % len(ip))
        for t in ip:
            name = self.team.members[t.assignee_id].name if t.assignee_id and t.assignee_id in self.team.members else u("未分配")
            lines.append(u("  %s - %s") % (t.title, name))
        return u("\n").join(lines)


# ─── 演示 ─────────────────────────────────────────
def demo():
    print(u("=" * 56))
    print(u("  研发团队管理系统 v2.0"))
    print(u("  角色: 管家 | 创意 | 数据工程师 | 监理 | 开发 | 测试 | 架构"))
    print(u("=" * 56))

    p = Project(u("智慧校园App"), u("校园信息化平台开发项目"))
    print(u("\n第1步: 创建项目 -> %s") % p.name)

    print(u("\n第2步: 招募团队"))
    p.recruit_team()

    print(u("\n第3步: 规划阶段"))
    for ph in [u("需求分析"), u("设计"), u("开发"), u("测试"), u("部署")]:
        p.create_phase(ph)

    print(u("\n第4步: 创建任务"))
    t1 = p.add_task(u("用户需求调研"), priority=Priority.URGENT, phase_index=0, estimated_hours=16)
    t2 = p.add_task(u("产品功能定义"), priority=Priority.HIGH, phase_index=0, estimated_hours=8)

    print(u("\n第5步: 任务分解"))
    p.decompose_task(t1.task_id, [
        {u("title"): u("设计问卷"), u("estimated_hours"): 4, u("role_required"): u("创意")},
        {u("title"): u("发放收集问卷"), u("estimated_hours"): 6},
        {u("title"): u("数据分析报告"), u("estimated_hours"): 6, u("role_required"): u("数据工程师")},
    ])

    print(u("\n第6步: 创建设计任务"))
    t3 = p.add_task(u("UI界面设计"), priority=Priority.HIGH, phase_index=1, estimated_hours=24)

    print(u("\n第7步: 管家分配任务"))
    p.assign_task(t1.task_id, role_type=RoleType.BUTLER)
    subs = p.tasks.get_subtasks(t1.task_id)
    if subs:
        p.assign_task(subs[0].task_id, role_type=RoleType.CREATIVE)
        if len(subs) > 2:
            p.assign_task(subs[2].task_id, role_type=RoleType.DATA_ENGINEER)
    p.assign_task(t3.task_id, role_type=RoleType.CREATIVE)

    print(u("\n第8步: 开始执行"))
    for s in subs:
        if s.assignee_id and s.status == TaskStatus.PENDING:
            p.start_task(s.task_id)

    print(u("\n第9步: 监理检查"))
    p.supervisor_check()

    print(u("\n第10步: 完成任务"))
    for s in subs:
        if s.status == TaskStatus.IN_PROGRESS:
            p.review_task(s.task_id)
            p.complete_task(s.task_id)
    if p.tasks.tasks[t1.task_id].status != TaskStatus.DONE:
        p.tasks.update_status(t1.task_id, TaskStatus.DONE)

    print(u("\n第11步: 项目报告\n"))
    r = p.report()
    print(r.encode('utf-8') if IS_PY2 else r)

    print(u("\n第12步: 管家计划\n"))
    bp = p.butler_plan()
    print(bp.encode('utf-8') if IS_PY2 else bp)

    print(u("\n" + "=" * 56))
    print(u("  演示完成！"))
    print(u("=" * 56))


if __name__ == "__main__":
    demo()
