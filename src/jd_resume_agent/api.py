from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.jd_resume_agent.agent_pipeline import run_agent_pipeline


app = FastAPI(title="JD-Resume Matching API")


class AnalyzeRequest(BaseModel):
    jd_text: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=1)
    enable_llm: bool = False


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return run_agent_pipeline(
        request.jd_text,
        request.resume_text,
        enable_llm=request.enable_llm,
    )
