from pathlib import Path

from core.schema import DeliveryPlan


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_all_example_jsons_match_delivery_plan_schema() -> None:
    files = sorted(EXAMPLES_DIR.glob("*.json"))
    assert len(files) == 3

    for example_file in files:
        plan = DeliveryPlan.model_validate_json(example_file.read_text(encoding="utf-8"))
        assert plan.summary.one_sentence
        assert plan.scenarios
        assert plan.boundary
        assert plan.risks
        assert plan.acceptance
        assert plan.rollout.phases
        assert plan.launch_plan
        assert plan.open_questions
        assert len(plan.scenarios) >= 5
        assert len(plan.risks) >= 6
        assert len(plan.acceptance) >= 5
        assert len(plan.rollout.phases) >= 3
        assert len(plan.rollout.rollback) >= 3
        assert len(plan.launch_plan) >= 6
        assert len(plan.open_questions) >= 6
        assert {item.name for item in plan.scenarios} == {item.scenario for item in plan.boundary}


def test_boundaries_only_use_expected_owners() -> None:
    plan = DeliveryPlan.model_validate_json(
        (EXAMPLES_DIR / "ecommerce_returns.json").read_text(encoding="utf-8")
    )
    assert {item.owner for item in plan.boundary} == {"Workflow", "Agent", "Human"}
