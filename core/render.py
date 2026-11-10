"""将 DeliveryPlan 渲染为 Streamlit 页面和不含讲解内容的 Markdown。"""

from __future__ import annotations

from collections.abc import Sequence

from core.schema import DeliveryPlan


TAB_GUIDANCE = {
    "摘要": ("客户到底要解决什么问题，怎样判断成功？", "没有共同目标，后面的功能和指标会各说各话。", "先看业务目标、现状痛点，再看带“需确认”的示例目标值。"),
    "场景": ("一句需求被拆成哪些可执行的业务场景？", "不拆场景，团队无法确认谁在何时提供什么输入。", "按入口→校验→判断→人工例外→回写→复盘，查看触发、输入和系统。"),
    "边界": ("每个场景由 Workflow、Agent 还是 Human 主负责？", "不划边界，模型容易越权，团队也不知道出错由谁接手。", "Workflow 是固定规则；Agent 处理上下文判断；Human 负责高风险和不可逆决定。重点看交接条件。"),
    "风险": ("什么可能出错，谁负责预警和缓解？", "不提前看数据、模型、流程、合规和组织风险，上线后只能被动救火。", "先看概率×影响，再看预警信号、缓解措施和负责人。"),
    "验收": ("上线前怎样证明方案真的能用？", "没有样本、方法和通过标准，所谓“效果不错”无法被复核。", "每条都看定义、示例目标值、测试方法、样本量和通过标准。"),
    "灰度/回滚": ("先给多大范围使用，出问题怎样退回？", "没有小范围观察和回退路径，错误会直接扩大到全量。", "看进入条件、观察时长、负责人；再看三类回滚触发。"),
    "上线计划": ("从澄清到常态运行，谁在何时交付什么？", "没有退出标准，项目容易一直推进却没有真正的放行点。", "按周看交付物、参与方和每个阶段的退出标准。"),
    "待澄清": ("哪些业务事实还缺，必须问客户？", "把假设当事实，会让后续的规则、指标和责任全部失真。", "按业务、数据、系统、合规分组，优先确认会改变边界的问题。"),
}

INTERVIEW_TALKS = {
    "摘要": "我先不谈模型，先对齐客户真正要改善的业务问题。所有目标值都只是示例，必须回到客户基线确认。",
    "场景": "我把一句模糊需求拆成连续场景，方便业务、研发和运营确认输入、输出和依赖是否完整。",
    "边界": "这里不是把 AI 做满，而是把确定动作、判断动作和责任动作分开；交接点就是出错时谁接手。",
    "风险": "我会在上线前让风险有主人、有预警，而不是等投诉出现才讨论模型问题。",
    "验收": "验收不只看准确率，还要验证该转人工的有没有转、异常能不能退回、业务方是否愿意用。",
    "灰度/回滚": "先用小范围证据决定是否放大；一旦触发红线，先切回人工，再复盘原因。",
    "上线计划": "每个阶段都有交付物、参与方和退出标准，避免“开发完成”被误当成“可以上线”。",
    "待澄清": "这些不是没做完，而是我主动把会改变方案的假设列出来，带去和客户对齐。",
}

COLUMN_LABELS = {
    "metric": "指标",
    "current_value": "当前值",
    "example_target": "示例目标值",
    "name": "场景",
    "trigger": "触发",
    "inputs": "输入",
    "expected_output": "期望输出",
    "frequency_scale": "频次",
    "involved_systems": "涉及系统",
    "scenario": "场景",
    "owner": "归属",
    "reason": "理由",
    "failed_handoff_to": "失败时交给谁",
    "handoff_condition": "交接条件",
    "description": "风险",
    "risk_type": "类型",
    "probability": "概率",
    "impact": "影响",
    "mitigation": "缓解",
    "early_warning_signal": "预警",
    "owner_role": "负责人",
    "metric_definition": "定义",
    "test_method": "方法",
    "sample_size": "样本量",
    "pass_criteria": "通过标准",
    "stage": "阶段",
    "scope_percentage": "范围",
    "entry_condition": "进入条件",
    "observation_metrics": "观察指标",
    "observation_duration": "观察时长",
    "trigger_condition": "触发条件",
    "rollback_action": "回滚动作",
    "recovery_time": "恢复时长",
    "timeline": "时间",
    "deliverables": "交付物",
    "participants": "参与方",
    "exit_criteria": "退出标准",
    "category": "分组",
    "question": "问题",
}


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    return lines + ["| " + " | ".join(row) + " |" for row in rows]


def plan_as_markdown(plan: DeliveryPlan) -> str:
    lines = ["# AI/Agent 交付方案", "", "> **示例数据声明**：本方案中的场景、目标值和安排仅用于演示；所有目标值需与客户确认。", "", "## 1. 需求摘要", f"- **一句话概括**：{plan.summary.one_sentence}", f"- **业务目标**：{plan.summary.business_goal}", "- **业务背景**："]
    lines += [f"  - {item}" for item in plan.summary.business_background] + ["- **现状痛点**:"] + [f"  - {item}" for item in plan.summary.pain_points]
    lines += _table(["指标", "当前值", "示例目标值"], [[m.metric, m.current_value, m.example_target] for m in plan.summary.key_metrics])
    lines += ["", "## 2. 场景拆解"] + _table(["场景", "触发", "输入", "期望输出", "频次", "涉及系统"], [[x.name, x.trigger, "；".join(x.inputs), x.expected_output, x.frequency_scale, "；".join(x.involved_systems)] for x in plan.scenarios])
    lines += ["", "## 3. Workflow / Agent / Human 边界"] + _table(["场景", "归属", "理由", "失败时交给谁", "交接条件"], [[x.scenario, x.owner, x.reason, x.failed_handoff_to, x.handoff_condition] for x in plan.boundary])
    lines += ["", "### 人机交接总规则"] + [f"- {x}" for x in plan.human_handoff_rules]
    lines += ["", "## 4. 风险清单"] + _table(["风险", "类型", "概率", "影响", "缓解", "预警", "负责人"], [[x.description, x.risk_type, x.probability, x.impact, x.mitigation, x.early_warning_signal, x.owner_role] for x in plan.risks])
    lines += ["", "## 5. 验收标准"] + _table(["指标", "定义", "示例目标值", "方法", "样本量", "通过标准"], [[x.metric, x.metric_definition, x.example_target, x.test_method, x.sample_size, x.pass_criteria] for x in plan.acceptance])
    lines += ["", "## 6. 灰度与回滚"] + _table(["阶段", "范围", "进入条件", "观察指标", "观察时长", "负责人"], [[x.stage, x.scope_percentage, x.entry_condition, "；".join(x.observation_metrics), x.observation_duration, x.owner_role] for x in plan.rollout.phases])
    lines += ["", "### 回滚计划"] + _table(["触发条件", "回滚动作", "恢复时长"], [[x.trigger_condition, x.rollback_action, x.recovery_time] for x in plan.rollout.rollback]) + ["", f"- **回滚后复盘**：{plan.rollout.post_rollback_review}"]
    lines += ["", "## 7. 上线里程碑"] + _table(["阶段", "时间", "交付物", "参与方", "退出标准"], [[x.stage, x.timeline, "；".join(x.deliverables), "；".join(x.participants), x.exit_criteria] for x in plan.launch_plan])
    lines += ["", "## 8. 待澄清问题"] + _table(["分组", "问题"], [[x.category, x.question] for x in plan.open_questions])
    return "\n".join(lines)


def table_records(items: Sequence[object]) -> list[dict[str, str]]:
    """把方案对象转成中文列名的表格行，列表字段用分号拼接。"""
    records: list[dict[str, str]] = []
    for item in items:
        row: dict[str, str] = {}
        for key, value in item.model_dump().items():  # type: ignore[attr-defined]
            label = COLUMN_LABELS.get(key, key)
            row[label] = "；".join(value) if isinstance(value, list) else str(value)
        records.append(row)
    return records


def _bullets(items: list[str]) -> None:
    import streamlit as st
    st.markdown("\n".join(f"- {item}" for item in items))


def _dataframe(items: Sequence[object]) -> None:
    import streamlit as st
    st.dataframe(table_records(items), width="stretch", hide_index=True)


def _guidance(label: str, show: bool) -> None:
    if not show:
        return
    import streamlit as st
    question, reason, how = TAB_GUIDANCE[label]
    st.info(f"**回答什么问题**：{question}\n\n**为什么要做**：{reason}\n\n**怎么读**：{how}")


def _talk(label: str, show: bool) -> None:
    if show:
        import streamlit as st
        st.caption("面试讲法")
        st.write(INTERVIEW_TALKS[label])


def render_plan(plan: DeliveryPlan, show_guidance: bool = True, default_tab: str | None = None) -> None:
    import streamlit as st
    labels = ["1. 摘要", "2. 场景", "3. 边界", "4. 风险", "5. 验收", "6. 灰度/回滚", "7. 上线计划", "8. 待澄清"]
    tabs = st.tabs(labels, default=default_tab if default_tab in labels else None)
    with tabs[0]:
        _guidance("摘要", show_guidance)
        st.subheader(plan.summary.one_sentence)
        st.write(plan.summary.business_goal)
        st.write("**业务背景**")
        _bullets(plan.summary.business_background)
        st.write("**现状痛点**")
        _bullets(plan.summary.pain_points)
        _dataframe(plan.summary.key_metrics)
        _talk("摘要", show_guidance)
    with tabs[1]:
        _guidance("场景", show_guidance)
        _dataframe(plan.scenarios)
        _talk("场景", show_guidance)
    with tabs[2]:
        _guidance("边界", show_guidance)
        _dataframe(plan.boundary)
        st.write("**人机交接总规则**")
        _bullets(plan.human_handoff_rules)
        _talk("边界", show_guidance)
    with tabs[3]:
        _guidance("风险", show_guidance)
        _dataframe(plan.risks)
        _talk("风险", show_guidance)
    with tabs[4]:
        _guidance("验收", show_guidance)
        _dataframe(plan.acceptance)
        _talk("验收", show_guidance)
    with tabs[5]:
        _guidance("灰度/回滚", show_guidance)
        st.subheader("灰度计划")
        _dataframe(plan.rollout.phases)
        st.subheader("回滚计划")
        _dataframe(plan.rollout.rollback)
        st.write(f"**回滚后复盘**：{plan.rollout.post_rollback_review}")
        _talk("灰度/回滚", show_guidance)
    with tabs[6]:
        _guidance("上线计划", show_guidance)
        _dataframe(plan.launch_plan)
        _talk("上线计划", show_guidance)
    with tabs[7]:
        _guidance("待澄清", show_guidance)
        _dataframe(plan.open_questions)
        _talk("待澄清", show_guidance)
