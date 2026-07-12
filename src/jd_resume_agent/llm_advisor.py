from __future__ import annotations

import json
import os
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


LLM_REQUIRED_FIELDS = [
    "resume_strengths",
    "gap_analysis",
    "rewrite_suggestions",
    "next_steps",
]


def llm_is_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def build_llm_prompt(jd_text: str, resume_text: str, rule_result: dict) -> str:
    return f"""
你是一个面向 AI Agent 实习求职的简历优化助手。

请根据岗位 JD、候选人简历和规则匹配结果，输出严格 JSON。
不要输出 Markdown，不要输出解释文字，只输出 JSON 对象。

JSON 字段必须包含：
- resume_strengths: string[]，简历优势
- gap_analysis: object[]，每项包含 skill、priority、action
- rewrite_suggestions: string[]，简历改写建议
- next_steps: string[]，下一步补强计划

要求：
- 不要虚构候选人没有做过的项目成果。
- 如果建议补充技能，要说明应通过小功能或项目证据验证。
- 建议要面向 AI Agent / LLM 应用实习。
- 语言使用中文，技术关键词可保留英文。

岗位 JD：
{jd_text}

候选人简历：
{resume_text}

规则匹配结果：
{json.dumps(rule_result, ensure_ascii=False)}
""".strip()


def parse_llm_json(content: str) -> dict[str, Any]:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    data = json.loads(cleaned)

    if not isinstance(data, dict):
        raise ValueError("LLM response must be a JSON object.")

    missing_fields = [field for field in LLM_REQUIRED_FIELDS if field not in data]
    if missing_fields:
        raise ValueError("LLM response missing fields: " + ", ".join(missing_fields))

    return data


def call_llm_advisor(jd_text: str, resume_text: str, rule_result: dict) -> dict:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("未配置 LLM_API_KEY，已使用规则版分析。")

    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/chat/completions")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    prompt = build_llm_prompt(jd_text, resume_text, rule_result)

    response = requests.post(
        base_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "你是严谨的简历优化 Agent，只输出合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return parse_llm_json(content)


def merge_llm_advice(rule_result: dict, llm_advice: dict) -> dict:
    merged = dict(rule_result)
    merged["analysis_mode"] = "llm_enhanced"
    merged["llm_status"] = "ok"

    for field in LLM_REQUIRED_FIELDS:
        merged[field] = llm_advice[field]

    return merged


def analyze_with_optional_llm(jd_text: str, resume_text: str, rule_result: dict) -> dict:
    if not llm_is_configured() or rule_result.get("status") != "ok":
        result = dict(rule_result)
        result["llm_status"] = "skipped"
        return result

    try:
        llm_advice = call_llm_advisor(jd_text, resume_text, rule_result)
    except Exception as exc:
        result = dict(rule_result)
        result["llm_status"] = "failed"
        result["llm_error"] = str(exc)
        return result

    return merge_llm_advice(rule_result, llm_advice)
