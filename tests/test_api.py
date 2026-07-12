from fastapi.testclient import TestClient

from src.jd_resume_agent.api import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_match_result():
    response = client.post(
        "/analyze",
        json={
            "jd_text": "要求 Python、Streamlit、FastAPI、pytest。",
            "resume_text": "项目使用 Python 和 Streamlit。",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["match_score"] == 50
    assert data["matched_skills"] == ["python", "streamlit"]
    assert data["missing_skills"] == ["fastapi", "pytest"]
    assert data["agent_steps"]


def test_analyze_endpoint_can_skip_llm_without_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    response = client.post(
        "/analyze",
        json={
            "jd_text": "Python",
            "resume_text": "Python",
            "enable_llm": True,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["analysis_mode"] == "rule_based"
    assert data["llm_status"] == "skipped"
