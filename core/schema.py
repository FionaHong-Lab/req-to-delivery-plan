"""交付方案的可校验数据合同。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Summary(BaseModel):
    one_sentence: str = Field(min_length=5, description="需求一句话概括")
    business_goal: str = Field(min_length=5)
    key_metrics: list[str] = Field(min_length=1)


class Scenario(BaseModel):
    name: str = Field(min_length=2)
    trigger: str = Field(min_length=2)
    inputs: list[str] = Field(min_length=1)
    expected_output: str = Field(min_length=2)
    frequency_scale: str = Field(min_length=1)


class BoundaryItem(BaseModel):
    scenario: str = Field(min_length=2)
    owner: Literal["Workflow", "Agent", "Human"]
    reason: str = Field(min_length=5)
    handoff: str = Field(min_length=5)


class Risk(BaseModel):
    description: str = Field(min_length=5)
    risk_type: Literal["数据", "模型", "流程", "合规", "组织"]
    probability: Literal["低", "中", "高"]
    impact: Literal["低", "中", "高"]
    mitigation: str = Field(min_length=5)
    owner_role: str = Field(min_length=2)


class AcceptanceItem(BaseModel):
    metric: str = Field(min_length=2)
    target: str = Field(min_length=1)
    test_method: str = Field(min_length=5)
    sample_size: str = Field(min_length=1)


class RolloutPhase(BaseModel):
    stage: str = Field(min_length=2)
    scope_percentage: str = Field(min_length=1)
    entry_condition: str = Field(min_length=5)
    observation_metrics: list[str] = Field(min_length=1)


class RollbackPlan(BaseModel):
    trigger_condition: str = Field(min_length=5)
    rollback_action: str = Field(min_length=5)
    recovery_time: str = Field(min_length=1)


class RolloutPlan(BaseModel):
    phases: list[RolloutPhase] = Field(min_length=1)
    rollback: RollbackPlan


class LaunchMilestone(BaseModel):
    stage: str = Field(min_length=2)
    timeline: str = Field(min_length=1)
    deliverables: list[str] = Field(min_length=1)
    participants: list[str] = Field(min_length=1)


class DeliveryPlan(BaseModel):
    """需求→AI/Agent 交付方案的完整输出。"""

    summary: Summary
    scenarios: list[Scenario] = Field(min_length=1)
    boundary: list[BoundaryItem] = Field(min_length=1)
    risks: list[Risk] = Field(min_length=1)
    acceptance: list[AcceptanceItem] = Field(min_length=1)
    rollout: RolloutPlan
    launch_plan: list[LaunchMilestone] = Field(min_length=1)
    open_questions: list[str] = Field(min_length=1)
