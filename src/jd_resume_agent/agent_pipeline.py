from __future__ import annotations

from dataclasses import dataclass

from src.jd_resume_agent.llm_advisor import analyze_with_optional_llm
from src.jd_resume_agent.matcher import analyze_resume_match


@dataclass(frozen=True)
class AgentStep:
    name: str
    description: str


AGENT_STEPS = [
    AgentStep("input_validation", "检查 JD 与简历文本是否为空。"),
    AgentStep("jd_resume_matching", "抽取 JD 与简历技能关键词，计算匹配度。"),
    AgentStep("gap_analysis", "生成命中技能、缺失技能、优势与补强建议。"),
    AgentStep("llm_enhancement", "在配置 API Key 时调用 LLM 优化建议，否则回退规则版。"),
    AgentStep("structured_output", "输出稳定 JSON，供页面、API 和下载报告复用。"),
]


def get_agent_steps() -> list[dict]:
    return [{"name": step.name, "description": step.description} for step in AGENT_STEPS]


def run_agent_pipeline(jd_text: str, resume_text: str, enable_llm: bool = False) -> dict:
    rule_result = analyze_resume_match(jd_text, resume_text)

    if enable_llm:
        result = analyze_with_optional_llm(jd_text, resume_text, rule_result)
    else:
        result = rule_result

    result["agent_steps"] = get_agent_steps()
    return result
