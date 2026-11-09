"""在线生成、Pydantic 校验、一次重试与离线回退。"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from core.prompts import build_messages
from core.schema import DeliveryPlan


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
DEFAULT_EXAMPLE_ID = "ecommerce_returns"


@dataclass(frozen=True)
class GenerationResult:
    plan: DeliveryPlan
    mode: str
    message: str | None = None


def load_env_file() -> None:
    """仅把本地 .env 中尚未设置的值读进当前进程环境。"""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def online_mode_available() -> bool:
    load_env_file()
    return bool(os.getenv("LLM_API_KEY", "").strip())


def load_example(example_id: str) -> DeliveryPlan:
    example_path = EXAMPLES_DIR / f"{example_id}.json"
    return DeliveryPlan.model_validate_json(example_path.read_text(encoding="utf-8"))


def list_examples() -> dict[str, str]:
    examples: dict[str, str] = {}
    for markdown_path in sorted(EXAMPLES_DIR.glob("*.md")):
        examples[markdown_path.stem] = markdown_path.read_text(encoding="utf-8")
    return examples


def _extract_json(content: str) -> str:
    stripped = content.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    return fenced.group(1) if fenced else stripped


def _request_plan(requirement: str, repair_hint: str | None = None) -> DeliveryPlan:
    api_key = os.environ["LLM_API_KEY"]
    base_url = os.getenv("LLM_BASE_URL", "").strip() or None
    model = os.getenv("LLM_MODEL", "").strip() or "gpt-4.1-mini"
    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(
        model=model,
        messages=build_messages(requirement, repair_hint),
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("模型未返回可读取的内容")
    return DeliveryPlan.model_validate_json(_extract_json(content))


def generate_plan(requirement: str, fallback_example_id: str = DEFAULT_EXAMPLE_ID) -> GenerationResult:
    """无 key 时回退；在线输出校验失败后重试一次，再回退。"""
    if not online_mode_available():
        return GenerationResult(
            plan=load_example(fallback_example_id),
            mode="离线示例",
            message="未检测到 LLM_API_KEY，已展示虚构的离线示例数据。",
        )

    errors: list[str] = []
    for attempt in range(2):
        try:
            return GenerationResult(plan=_request_plan(requirement, errors[-1] if errors else None), mode="在线生成")
        except Exception as exc:  # 将接口错误和 schema 错误统一纳入一次修复重试
            errors.append(f"第 {attempt + 1} 次：{exc}")

    return GenerationResult(
        plan=load_example(fallback_example_id),
        mode="离线示例",
        message="在线生成或结构校验失败，已回退到虚构示例数据。原因：" + "；".join(errors),
    )


def plan_as_json(plan: DeliveryPlan) -> str:
    return json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2)
