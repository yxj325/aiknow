# -*- coding: utf-8 -*-
# 研发团队管理系统 - 演示脚本

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team_system.project import Project
from team_system.tasks.task import Priority
from team_system.roles.role import RoleType


def demo():
    print(u"=" * 56)
    print(u"    研发团队管理系统 - 演示模式")
    print(u"    角色: 管家 | 创意 | 数据 | 监理 | 开发 | 测试 | 架构")
    print(u"=" * 56)

    project = Project(u"智慧校园App", u"校园信息化平台开发项目")
    print(u"\n第1步: 创建项目 -> %s" % project.name)
    print(u"   描述: %s" % project.description)

    print(u"\n第2步: 招募团队")
    project.recruit_team()

    print(u"\n第3步: 规划项目阶段")
    for phase_name in [u"需求分析", u"设计", u"开发", u"测试", u"部署上线"]:
        project.create_phase(phase_name)

    print(u"\n第4步: 创建需求阶段任务")
    t1 = project.add_task(u"用户需求调研", u"收集学生和教师需求",
                          priority=Priority.URGENT, phase_index=0, estimated_hours=16)
    t2 = project.add_task(u"产品功能定义", u"定义核心功能列表",
                          priority=Priority.HIGH, phase_index=0, estimated_hours=8)

    print(u"\n第5步: 任务分解 - %s [%s]" % (t1.title, t1.task_id))
    project.decompose_task(t1.task_id, [
        {"title": u"设计问卷调查", "estimated_hours": 4, "role_required": u"创意"},
        {"title": u"发放并收集问卷", "estimated_hours": 6},
        {"title": u"数据分析与报告", "estimated_hours": 6, "role_required": u"数据工程师"},
    ])

    print(u"\n第6步: 创建设计阶段任务")
    t3 = project.add_task(u"UI界面设计", u"App界面视觉设计",
                          priority=Priority.HIGH, phase_index=1, estimated_hours=24)

    print(u"\n第7步: 管家分配任务")
    project.assign_task(t1.task_id, role_type=RoleType.BUTLER)

    design_subtask = project.tasks.get_subtasks(t1.task_id)
    if design_subtask:
        project.assign_task(design_subtask[0].task_id, role_type=RoleType.CREATIVE)
        if len(design_subtask) > 2:
            project.assign_task(design_subtask[2].task_id, role_type=RoleType.DATA_ENGINEER)

    project.assign_task(t3.task_id, role_type=RoleType.CREATIVE)

    print(u"\n第8步: 开始执行任务")
    subtasks = project.tasks.get_subtasks(t1.task_id)
    for sub in subtasks:
        if sub.assignee_id and sub.status == TaskStatus.PENDING:
            project.start_task(sub.task_id)
            print(u"   %s 开始执行" % sub.title)

    print(u"\n第9步: 监理质量审查")
    project.supervisor_check()

    print(u"\n第10步: 完成任务流转")
    for sub in subtasks:
        if sub.status == TaskStatus.IN_PROGRESS:
            project.review_task(sub.task_id)
            project.complete_task(sub.task_id)
            print(u"   %s 已完成" % sub.title)

    if project.tasks.tasks[t1.task_id].status != TaskStatus.DONE:
        project.tasks.update_status(t1.task_id, TaskStatus.DONE)
        print(u"   父任务 %s 自动完成" % t1.title)

    print(u"\n第11步: 生成项目报告\n")
    print(project.report())

    print(u"\n第12步: 管家工作计划\n")
    print(project.butler_plan())

    print(u"\n" + "=" * 56)
    print(u"   演示完成！运行 python main.py 进入交互模式")
    print(u"=" * 56)


if __name__ == "__main__":
    demo()
