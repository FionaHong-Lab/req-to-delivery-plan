"""需求→交付方案生成器：本地 Streamlit 演示入口。"""

from __future__ import annotations

import streamlit as st

from core.generator import GenerationResult, generate_plan, list_examples, load_example, online_mode_available, plan_as_json
from core.render import plan_as_markdown, render_plan


st.set_page_config(page_title="需求→交付方案生成器", page_icon="🧭", layout="wide")


EXAMPLE_LABELS = {
    "ecommerce_returns": "电商退换货客服 Agent（示例数据）",
    "b2b_lead": "B2B 销售线索分级与跟进（示例数据）",
    "manufacturing_quote": "制造业报价助手（示例数据）",
}


def initialize_state() -> None:
    if "result" not in st.session_state:
        st.session_state.result = GenerationResult(
            plan=load_example("ecommerce_returns"),
            mode="离线示例",
            message="当前展示虚构的离线示例数据。选择示例或粘贴需求后点击生成。",
        )


def main() -> None:
    initialize_state()
    online = online_mode_available()
    show_guidance = st.sidebar.toggle("讲解模式", value=True, help="关闭后仅展示方案本身，适合截图。")
    st.sidebar.caption("打开时显示每一部分的阅读说明和面试讲法。")
    st.title("需求 → AI/Agent 交付方案生成器")
    st.caption("面试演示工具｜所有内置内容均为虚构的示例数据，不代表真实客户或项目结果。")
    with st.expander("这个工具是做什么的", expanded=True):
        st.write("**输入**：一段客户提出的模糊 AI 需求。")
        st.write("**输出**：一份交付经理视角的落地方案（8 部分）。")
        st.write("**价值**：把“需求 → 能上线”中间的拆解过程标准化，先出一版再和客户对齐。")
    st.graphviz_chart("""digraph {
        rankdir=LR; node [shape=box style=rounded];
        demand [label="客户需求"]; summary [label="1 摘要"]; scenarios [label="2 场景拆解"];
        boundary [label="3 边界划分"]; risks [label="4 风险"]; acceptance [label="5 验收"];
        rollout [label="6 灰度/回滚"]; launch [label="7 上线计划"]; questions [label="8 待澄清"];
        demand -> summary -> scenarios -> boundary -> risks -> acceptance -> rollout -> launch -> questions;
    }""")
    st.markdown("**三步怎么用**：① 左侧选一个示例　② 点“展示示例方案”　③ 按 1→8 顺序看标签，重点看 3、4、6。")

    left, right = st.columns([1, 2], gap="large")
    examples = list_examples()

    with left:
        st.subheader("输入需求")
        mode_label = "在线模式" if online else "离线示例模式"
        st.info(f"当前：{mode_label}")
        source = st.radio("选择输入方式", ["内置示例", "粘贴需求"], horizontal=True)

        if source == "内置示例":
            example_ids = [example_id for example_id in EXAMPLE_LABELS if example_id in examples]
            selected_id = st.selectbox(
                "选择示例",
                options=example_ids,
                format_func=lambda key: EXAMPLE_LABELS.get(key, key),
            )
            st.text_area("示例需求（只读）", value=examples[selected_id], height=180, disabled=True)
            generate_clicked = st.button("展示示例方案", type="primary", width="stretch")
            if generate_clicked:
                st.session_state.result = GenerationResult(
                    plan=load_example(selected_id), mode="离线示例", message="正在展示虚构的预生成示例数据。"
                )
        else:
            requirement = st.text_area("粘贴客户需求", placeholder="例如：我们希望……", height=220)
            generate_clicked = st.button("生成交付方案", type="primary", width="stretch")
            if generate_clicked:
                if not requirement.strip():
                    st.warning("请先粘贴一段需求，或切换到内置示例。")
                else:
                    with st.spinner("正在生成并校验方案结构…"):
                        st.session_state.result = generate_plan(requirement)

        st.divider()
        st.caption("在线模式会从环境变量读取 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL；密钥不会写入代码。")

    with right:
        result: GenerationResult = st.session_state.result
        if result.mode == "在线生成":
            st.success("在线生成｜已通过输出结构校验")
        else:
            st.warning("离线示例｜以下为虚构的预生成方案，不是客户交付结果。")
        if result.message:
            st.caption(result.message)

        first, second = st.columns(2)
        with first:
            st.download_button("下载 Markdown", data=plan_as_markdown(result.plan), file_name="delivery-plan.md", mime="text/markdown", width="stretch")
        with second:
            st.download_button("下载 JSON", data=plan_as_json(result.plan), file_name="delivery-plan.json", mime="application/json", width="stretch")
        render_plan(result.plan, show_guidance=show_guidance, default_tab=st.query_params.get("tab"))

    with st.expander("术语小抄"):
        st.markdown("- **Workflow**：规则固定、可重复执行的流程动作。\n- **Agent**：需要理解上下文、归纳或提出建议的助手。\n- **Human-in-the-loop**：关键决定必须有人确认的机制。\n- **灰度**：先在小范围使用并观察，再决定是否放大。\n- **回滚**：发现红线后切回安全的人工或旧流程。\n- **验收样本**：用于证明方案能否通过的、有标准答案的案例。\n- **兜底**：系统无法可靠处理时的安全处理路径。\n- **交接点**：从系统交给明确责任人的条件和去向。")


if __name__ == "__main__":
    main()
