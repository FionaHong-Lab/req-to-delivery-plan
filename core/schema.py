"""交付方案的可校验数据合同。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class KeyMetric(BaseModel):
    metric: str = Field(min_length=2)
    current_value: str = Field(min_length=1)
    example_target: str = Field(min_length=1)


class Summary(BaseModel):
    one_sentence: str = Field(min_length=5)
    business_goal: str = Field(min_length=5)
    business_background: list[str] = Field(min_length=3, max_length=4)
    pain_points: list[str] = Field(min_length=3)
    key_metrics: list[KeyMetric] = Field(min_length=4)


class Scenario(BaseModel):
    name: str = Field(min_length=2)
    trigger: str = Field(min_length=2)
    inputs: list[str] = Field(min_length=1)
    expected_output: str = Field(min_length=2)
    frequency_scale: str = Field(min_length=1)
    involved_systems: list[str] = Field(min_length=1)


class BoundaryItem(BaseModel):
    scenario: str = Field(min_length=2)
    owner: Literal["Workflow", "Agent", "Human"]
    reason: str = Field(min_length=5)
    failed_handoff_to: str = Field(min_length=2)
    handoff_condition: str = Field(min_length=5)


class Risk(BaseModel):
    description: str = Field(min_length=5)
    risk_type: Literal["数据", "模型", "流程", "合规", "组织"]
    probability: Literal["低", "中", "高"]
    impact: Literal["低", "中", "高"]
    mitigation: str = Field(min_length=5)
    early_warning_signal: str = Field(min_length=3)
    owner_role: str = Field(min_length=2)


class AcceptanceItem(BaseModel):
    metric: str = Field(min_length=2)
    metric_definition: str = Field(min_length=5)
    example_target: str = Field(min_length=1)
    test_method: str = Field(min_length=5)
    sample_size: str = Field(min_length=1)
    pass_criteria: str = Field(min_length=5)


class RolloutPhase(BaseModel):
    stage: str = Field(min_length=2)
    scope_percentage: str = Field(min_length=1)
    entry_condition: str = Field(min_length=5)
    observation_metrics: list[str] = Field(min_length=1)
    observation_duration: str = Field(min_length=1)
    owner_role: str = Field(min_length=2)


class RollbackTrigger(BaseModel):
    trigger_condition: str = Field(min_length=5)
    rollback_action: str = Field(min_length=5)
    recovery_time: str = Field(min_length=1)


class RolloutPlan(BaseModel):
    phases: list[RolloutPhase] = Field(min_length=3)
    rollback: list[RollbackTrigger] = Field(min_length=3)
    post_rollback_review: str = Field(min_length=5)


class LaunchMilestone(BaseModel):
    stage: str = Field(min_length=2)
    timeline: str = Field(min_length=1)
    deliverables: list[str] = Field(min_length=1)
    participants: list[str] = Field(min_length=1)
    exit_criteria: str = Field(min_length=5)


class OpenQuestion(BaseModel):
    category: Literal["业务", "数据", "系统", "合规"]
    question: str = Field(min_length=5)


class DeliveryPlan(BaseModel):
    """需求→AI/Agent 交付方案的完整输出。"""

    summary: Summary
    scenarios: list[Scenario] = Field(min_length=5)
    boundary: list[BoundaryItem] = Field(min_length=5)
    human_handoff_rules: list[str] = Field(min_length=3)
    risks: list[Risk] = Field(min_length=6)
    acceptance: list[AcceptanceItem] = Field(min_length=5)
    rollout: RolloutPlan
    launch_plan: list[LaunchMilestone] = Field(min_length=6)
    open_questions: list[OpenQuestion] = Field(min_length=6)

    @model_validator(mode="after")
    def boundary_must_match_scenarios(self) -> "DeliveryPlan":
        scenario_names = [item.name for item in self.scenarios]
        boundary_names = [item.scenario for item in self.boundary]
        if len(scenario_names) != len(set(scenario_names)):
            raise ValueError("scenarios 的场景名不能重复")
        if len(boundary_names) != len(set(boundary_names)):
            raise ValueError("boundary 的场景名不能重复")
        if set(scenario_names) != set(boundary_names):
            raise ValueError("boundary 的场景名必须与 scenarios 一一对应")
        return self
