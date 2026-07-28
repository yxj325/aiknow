# -*- coding: utf-8 -*-
"""研发团队管理系统 - 运行入口"""

import sys
import os
import codecs

# Fix encoding for Python 2
if sys.version_info[0] < 3:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team_system.project import Project
from team_system.tasks.task import Priority
from team_system.roles.role import RoleType


def demo():
    print(u"=" * 56)
    print(u"\U0001f3e2 \u7814\u53d1\u56e2\u961f\u7ba1\u7406\u7cfb\u7edf - \u6f14\u793a\u6a21\u5f0f")
    print(u"=" * 56)

    project = Project(u"\u667a\u6167\u6821\u56edApp", u"\u6821\u56ed\u4fe1\u606f\u5316\u5e73\u53f0\u5f00\u53d1\u9879\u76ee")
    print(u"\n\u7b2c1\u6b65: \u521b\u5efa\u9879\u76ee -> %s" % project.name)

    print(u"\n\u7b2c2\u6b65: \u62db\u52df\u56e2\u961f")
    project.recruit_team()

    print(u"\n\u7b2c3\u6b65: \u89c4\u5212\u9879\u76ee\u9636\u6bb5")
    for phase_name in [u"\u9700\u6c42\u5206\u6790", u"\u8bbe\u8ba1", u"\u5f00\u53d1", u"\u6d4b\u8bd5", u"\u90e8\u7f72\u4e0a\u7ebf"]:
        project.create_phase(phase_name)

    print(u"\n\u7b2c4\u6b65: \u521b\u5efa\u9700\u6c42\u9636\u6bb5\u4efb\u52a1")
    t1 = project.add_task(u"\u7528\u6237\u9700\u6c42\u8c03\u7814", u"\u6536\u96c6\u5b66\u751f\u548c\u6559\u5e08\u9700\u6c42",
                          priority=Priority.URGENT, phase_index=0, estimated_hours=16)
    t2 = project.add_task(u"\u4ea7\u54c1\u529f\u80fd\u5b9a\u4e49", u"\u5b9a\u4e49\u6838\u5fc3\u529f\u80fd\u5217\u8868",
                          priority=Priority.HIGH, phase_index=0, estimated_hours=8)

    print(u"\n\u7b2c5\u6b65: \u4efb\u52a1\u5206\u89e3 - %s [%s]" % (t1.title, t1.task_id))
    project.decompose_task(t1.task_id, [
        {"title": u"\u8bbe\u8ba1\u95ee\u5377\u8c03\u67e5", "estimated_hours": 4, "role_required": u"\u521b\u610f"},
        {"title": u"\u53d1\u653e\u5e76\u6536\u96c6\u95ee\u5377", "estimated_hours": 6},
        {"title": u"\u6570\u636e\u5206\u6790\u4e0e\u62a5\u544a", "estimated_hours": 6, "role_required": u"\u6570\u636e\u5de5\u7a0b\u5e08"},
    ])

    print(u"\n\u7b2c6\u6b65: \u521b\u5efa\u8bbe\u8ba1\u9636\u6bb5\u4efb\u52a1")
    t3 = project.add_task(u"UI\u754c\u9762\u8bbe\u8ba1", u"App\u754c\u9762\u89c6\u89c9\u8bbe\u8ba1",
                          priority=Priority.HIGH, phase_index=1, estimated_hours=24)

    print(u"\n\u7b2c7\u6b65: \u7ba1\u5bb6\u5206\u914d\u4efb\u52a1")
    project.assign_task(t1.task_id, role_type=RoleType.BUTLER)

    design_subtask = project.tasks.get_subtasks(t1.task_id)
    if design_subtask:
        project.assign_task(design_subtask[0].task_id, role_type=RoleType.CREATIVE)
        if len(design_subtask) > 2:
            project.assign_task(design_subtask[2].task_id, role_type=RoleType.DATA_ENGINEER)

    project.assign_task(t3.task_id, role_type=RoleType.CREATIVE)

    print(u"\n\u7b2c8\u6b65: \u5f00\u59cb\u6267\u884c\u4efb\u52a1")
    subtasks = project.tasks.get_subtasks(t1.task_id)
    for sub in subtasks:
        if sub.assignee_id and sub.status == TaskStatus.PENDING:
            project.start_task(sub.task_id)

    print(u"\n\u7b2c9\u6b65: \u76d1\u7406\u8d28\u91cf\u5ba1\u67e5")
    project.supervisor_check()

    print(u"\n\u7b2c10\u6b65: \u5b8c\u6210\u4efb\u52a1\u6d41\u8f6c")
    for sub in subtasks:
        if sub.status == TaskStatus.IN_PROGRESS:
            project.review_task(sub.task_id)
            project.complete_task(sub.task_id)

    if project.tasks.tasks[t1.task_id].status != TaskStatus.DONE:
        project.tasks.update_status(t1.task_id, TaskStatus.DONE)

    print(u"\n\u7b2c11\u6b65: \u751f\u6210\u9879\u76ee\u62a5\u544a\n")
    print(project.report())

    print(u"\n\u7b2c12\u6b65: \u7ba1\u5bb6\u5de5\u4f5c\u8ba1\u5212\n")
    print(project.butler_plan())

    print(u"\n" + "=" * 56)
    print(u"\u2705 \u6f14\u793a\u5b8c\u6210\uff01")
    print(u"=" * 56)


if __name__ == "__main__":
    demo()
