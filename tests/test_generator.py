from core.generator import generate_plan


def test_missing_key_falls_back_to_offline_example(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    result = generate_plan("这是一个仅用于测试离线回退的虚构需求。")

    assert result.mode == "离线示例"
    assert result.plan.boundary
    assert "虚构" in (result.message or "")
