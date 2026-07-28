# -*- coding: utf-8 -*-
"""研发团队管理系统 - 交互式 CLI"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")

IS_PY2 = sys.version_info[0] < 3

def u(text):
    if IS_PY2 and isinstance(text, str):
        return text.decode("utf-8")
    return text

from team_system_v2 import (
    Project, RoleType, TaskStatus, Priority
)


def print_(msg):
    text = u(msg)
    if IS_PY2:
        print(text.encode("utf-8"))
    else:
        print(text)


class InteractiveCLI:
    def __init__(self):
        self.project = None

    def run(self):
        print_(u("=" * 56))
        print_(u("  研发团队管理系统 - 交互模式"))
        print_(u("  输入 help 查看命令 | exit 退出"))
        print_(u("=" * 56))

        name = raw_input(u("项目名称: ").encode("utf-8")) if IS_PY2 else input(u("项目名称: "))
        self.project = Project(name or u("我的项目"))
        self.project.recruit_team()
        print_(u(""))

        self._help()
        while True:
            try:
                cmd = raw_input(u(">>> ").encode("utf-8")) if IS_PY2 else input(u(">>> "))
                cmd = cmd.strip()
                if not cmd:
                    continue
                self._handle(cmd)
            except (KeyboardInterrupt, EOFError):
                print_(u("再见！"))
                break
            except Exception as e:
                print_(u("错误: %s") % str(e))

    def _handle(self, cmd):
        parts = cmd.split()
        base = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        cmds = {
            "help": self._help,
            "h": self._help,
            "team": self._team,
            "phase": self._phase,
            "task": self._task,
            "decompose": self._decompose,
            "assign": self._assign,
            "start": self._start,
            "review": self._review,
            "done": self._done,
            "check": self._check,
            "plan": self._plan,
            "tree": self._tree,
            "report": self._report,
        }
        if base in cmds:
            cmds[base](args)
        else:
            print_(u("未知命令，输入 help 查看帮助"))

    def _help(self, args=None):
        print_(u("""
  命令列表:
     team           查看团队成员
     phase <名称>    添加项目阶段
     task <标题>     添加任务
     task -h <标题>  高优先级任务
     task -u <标题>  紧急任务
     decompose <ID>  分解任务
     assign <ID> <角色>  分配任务
     start <ID>      开始执行
     review <ID>     提交审查
     done <ID>       完成任务
     check           监理审查
     plan            管家计划
     tree            任务树
     report          项目报告
     help            帮助
     exit            退出
"""))

    def _team(self, args):
        print_(self.project.team.summary())

    def _phase(self, args):
        name = u(" ").join(args) if args else "阶段"
        self.project.create_phase(name)

    def _task(self, args):
        priority = Priority.MEDIUM
        title_parts = []
        i = 0
        while i < len(args):
            if args[i] == "-h":
                priority = Priority.HIGH
            elif args[i] == "-u":
                priority = Priority.URGENT
            else:
                title_parts.append(args[i])
            i += 1
        title = u(" ").join(title_parts) if title_parts else u("新任务")
        t = self.project.add_task(title, priority=priority)
        print_(u("已创建: %s [%s]") % (t.title, t.task_id))

    def _decompose(self, args):
        tid = args[0] if args else u("")
        if tid not in self.project.tasks.tasks:
            print_(u("任务不存在: %s") % tid)
            return
        print_(u("分解任务: %s" % self.project.tasks.tasks[tid].title))
        subs = []
        while True:
            title = raw_input(u("  子任务标题(空结束): ").encode("utf-8")) if IS_PY2 else input(u("  子任务标题(空结束): "))
            if not title.strip():
                break
            subs.append({u("title"): u(title), u("estimated_hours"): 0})
        if subs:
            self.project.decompose_task(tid, subs)

    def _assign(self, args):
        if len(args) < 1:
            print_(u("用法: assign <任务ID> [角色]"))
            return
        tid = args[0]
        role = u(" ").join(args[1:]) if len(args) > 1 else None
        if role:
            rt = RoleType.from_name(role)
            if rt:
                self.project.assign_task(tid, role_type=rt)
            else:
                print_(u("未知角色: %s") % role)
        else:
            self.project.assign_task(tid)

    def _start(self, args):
        if args:
            self.project.start_task(args[0])

    def _review(self, args):
        if args:
            self.project.review_task(args[0])

    def _done(self, args):
        if args:
            self.project.complete_task(args[0])

    def _check(self, args):
        self.project.supervisor_check()

    def _plan(self, args):
        bp = self.project.butler_plan()
        print_(bp)

    def _tree(self, args):
        tree = self.project.tasks.print_tree()
        print_(tree)

    def _report(self, args):
        r = self.project.report()
        print_(r)


if __name__ == "__main__":
    InteractiveCLI().run()
