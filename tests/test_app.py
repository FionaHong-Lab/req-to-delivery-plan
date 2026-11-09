from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_runs_in_offline_mode() -> None:
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py")
    app.run()

    assert not app.exception
    assert any("离线示例模式" in info.value for info in app.info)
    assert len(app.tabs) == 8
