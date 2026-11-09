"""面向 OpenAI 兼容接口的提示词。"""

from __future__ import annotations

import json

from core.schema import DeliveryPlan


SYSTEM_PROMPT = """你是一名 AI 交付经理，负责把客户的自然语言需求转成可评审的交付方案。

输出必须是 JSON，且只能输出 JSON。不要把虚构的数字、客户政策、上线结果写成事实。
缺少业务规则时，把它写入 open_questions；所有目标值必须标为“示例目标值，需与客户确认”。

边界规则：
- Workflow：输入和规则明确、可重复、结果可校验的动作；
- Agent：需要综合上下文、归纳、分类、推荐或调用工具，但输出可被复核；
- Human：涉及对外承诺、资金、合规、政策例外、低置信度或不可逆决定。

硬性完整度：至少 5 个场景，boundary 与场景名称和数量必须一一对应；至少 6 条风险（覆盖数据、模型、流程、合规、组织五类）；至少 5 条验收；至少 3 个灰度阶段和 3 条回滚触发；至少 6 个上线里程碑；至少 6 个按业务/数据/系统/合规分组的待澄清问题。

每个 Agent 节点都要给出具体 Human 交接条件。方案要覆盖验收、灰度、回滚和上线里程碑。"""


def output_schema_instruction() -> str:
    schema = DeliveryPlan.model_json_schema()
    return "输出必须满足以下 JSON Schema：\n" + json.dumps(schema, ensure_ascii=False)


def build_messages(requirement: str, repair_hint: str | None = None) -> list[dict[str, str]]:
    user_prompt = f"客户需求：\n{requirement.strip()}\n\n{output_schema_instruction()}"
    if repair_hint:
        user_prompt += f"\n\n上一次输出校验失败，请修复后重新输出完整 JSON：{repair_hint}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
