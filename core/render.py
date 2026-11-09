"""将 DeliveryPlan 渲染为 Streamlit 页面和可下载 Markdown。"""

from __future__ import annotations

from core.schema import DeliveryPlan


def plan_as_markdown(plan: DeliveryPlan) -> str:
    lines = ["# AI/Agent 交付方案", "", "## 1. 需求摘要", f"- **一句话概括**：{plan.summary.one_sentence}", f"- **业务目标**：{plan.summary.business_goal}", "- **关键指标**："]
    lines.extend(f"  - {metric}" for metric in plan.summary.key_metrics)

    lines.extend(["", "## 2. 场景拆解", "| 场景 | 触发条件 | 输入 | 期望输出 | 频次/量级 |", "| --- | --- | --- | --- | --- |"])
    lines.extend(f"| {item.name} | {item.trigger} | {'；'.join(item.inputs)} | {item.expected_output} | {item.frequency_scale} |" for item in plan.scenarios)

    lines.extend(["", "## 3. Workflow / Agent / Human 边界", "| 场景 | 归属 | 理由 | 人机交接点 |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {item.scenario} | {item.owner} | {item.reason} | {item.handoff} |" for item in plan.boundary)

    lines.extend(["", "## 4. 风险清单", "| 风险 | 类型 | 概率 | 影响 | 缓解措施 | 负责人 |", "| --- | --- | --- | --- | --- |"])
    lines.extend(f"| {item.description} | {item.risk_type} | {item.probability} | {item.impact} | {item.mitigation} | {item.owner_role} |" for item in plan.risks)

    lines.extend(["", "## 5. 验收标准", "| 指标 | 目标值 | 测试方法 | 样本量 |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {item.metric} | {item.target} | {item.test_method} | {item.sample_size} |" for item in plan.acceptance)

    lines.extend(["", "## 6. 灰度与回滚", "| 阶段 | 范围比例 | 进入条件 | 观察指标 |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {item.stage} | {item.scope_percentage} | {item.entry_condition} | {'；'.join(item.observation_metrics)} |" for item in plan.rollout.phases)
    lines.extend(["", "### 回滚计划", f"- **触发条件**：{plan.rollout.rollback.trigger_condition}", f"- **回滚动作**：{plan.rollout.rollback.rollback_action}", f"- **恢复时长**：{plan.rollout.rollback.recovery_time}"])

    lines.extend(["", "## 7. 上线里程碑", "| 阶段 | 时间 | 交付物 | 参与方 |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {item.stage} | {item.timeline} | {'；'.join(item.deliverables)} | {'；'.join(item.participants)} |" for item in plan.launch_plan)

    lines.extend(["", "## 8. 待澄清问题"])
    lines.extend(f"- {question}" for question in plan.open_questions)
    lines.extend(["", "> 注：本工具输出为方案草稿；规则、阈值、指标与上线决定须由客户责任人确认。"])
    return "\n".join(lines)


def render_plan(plan: DeliveryPlan, default_tab: str | None = None) -> None:
    import streamlit as st

    labels = ["1. 摘要", "2. 场景", "3. 边界", "4. 风险", "5. 验收", "6. 灰度/回滚", "7. 上线计划", "8. 待澄清"]
    tabs = st.tabs(labels, default=default_tab if default_tab in labels else None)

    with tabs[0]:
        st.subheader(plan.summary.one_sentence)
        st.write(plan.summary.business_goal)
        st.caption("关键指标")
        st.write(" · ".join(plan.summary.key_metrics))
    with tabs[1]:
        st.dataframe([item.model_dump() for item in plan.scenarios], use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe([item.model_dump() for item in plan.boundary], use_container_width=True, hide_index=True)
    with tabs[3]:
        st.dataframe([item.model_dump() for item in plan.risks], use_container_width=True, hide_index=True)
    with tabs[4]:
        st.dataframe([item.model_dump() for item in plan.acceptance], use_container_width=True, hide_index=True)
    with tabs[5]:
        st.subheader("灰度计划")
        st.dataframe([item.model_dump() for item in plan.rollout.phases], use_container_width=True, hide_index=True)
        st.subheader("回滚计划")
        st.dataframe([plan.rollout.rollback.model_dump()], use_container_width=True, hide_index=True)
    with tabs[6]:
        st.dataframe([item.model_dump() for item in plan.launch_plan], use_container_width=True, hide_index=True)
    with tabs[7]:
        for question in plan.open_questions:
            st.markdown(f"- {question}")
