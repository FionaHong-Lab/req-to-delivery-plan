from pathlib import Path

from core.render import INTERVIEW_TALKS, TAB_GUIDANCE, plan_as_markdown
from core.schema import DeliveryPlan


def test_export_contains_only_plan_content_not_guidance() -> None:
    plan = DeliveryPlan.model_validate_json(
        (Path(__file__).resolve().parents[1] / "examples" / "ecommerce_returns.json").read_text(encoding="utf-8")
    )
    markdown = plan_as_markdown(plan)

    assert "示例数据声明" in markdown
    assert "面试讲法" not in markdown
    assert "回答什么问题" not in markdown
    assert all(text not in markdown for text in INTERVIEW_TALKS.values())
    assert len(TAB_GUIDANCE) == 8
