from pathlib import Path

from core.render import INTERVIEW_TALKS, TAB_GUIDANCE, plan_as_markdown, table_records
from core.schema import DeliveryPlan


def _ecommerce_plan() -> DeliveryPlan:
    return DeliveryPlan.model_validate_json(
        (Path(__file__).resolve().parents[1] / "examples" / "ecommerce_returns.json").read_text(encoding="utf-8")
    )


def test_export_contains_only_plan_content_not_guidance() -> None:
    markdown = plan_as_markdown(_ecommerce_plan())

    assert "示例数据声明" in markdown
    assert "面试讲法" not in markdown
    assert "回答什么问题" not in markdown
    assert all(text not in markdown for text in INTERVIEW_TALKS.values())
    assert len(TAB_GUIDANCE) == 8


def test_table_records_use_chinese_headers_and_join_lists() -> None:
    plan = _ecommerce_plan()

    metric_rows = table_records(plan.summary.key_metrics)
    assert list(metric_rows[0].keys()) == ["指标", "当前值", "示例目标值"]
    assert "metric" not in metric_rows[0]

    scenario_rows = table_records(plan.scenarios)
    assert list(scenario_rows[0].keys()) == ["场景", "触发", "输入", "期望输出", "频次", "涉及系统"]
    assert "；" in scenario_rows[0]["输入"]
    assert isinstance(scenario_rows[0]["输入"], str)

    boundary_rows = table_records(plan.boundary)
    assert "失败时交给谁" in boundary_rows[0]
    assert "failed_handoff_to" not in boundary_rows[0]
