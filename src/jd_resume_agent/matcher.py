from __future__ import annotations

import re


SKILL_KEYWORDS = [
    "python",
    "streamlit",
    "fastapi",
    "flask",
    "django",
    "llm",
    "大模型",
    "ai agent",
    "agent",
    "rag",
    "向量数据库",
    "embedding",
    "langchain",
    "llamaindex",
    "openai",
    "api",
    "json",
    "pytest",
    "git",
    "docker",
    "sql",
    "mysql",
    "mongodb",
    "redis",
    "pdf",
    "docx",
    "自然语言处理",
    "机器学习",
    "深度学习",
]

HIGH_PRIORITY_SKILLS = {
    "python",
    "fastapi",
    "streamlit",
    "llm",
    "大模型",
    "ai agent",
    "agent",
    "rag",
    "json",
    "pytest",
    "git",
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_skills(text: str) -> list[str]:
    normalized = normalize_text(text)
    found_skills: list[str] = []

    for skill in SKILL_KEYWORDS:
        keyword = skill.lower()

        if keyword.replace(" ", "").isascii():
            pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"
            if re.search(pattern, normalized):
                found_skills.append(skill)
        elif keyword in normalized:
            found_skills.append(skill)

    return found_skills


def build_resume_strengths(matched_skills: list[str], resume_skills: list[str]) -> list[str]:
    strengths: list[str] = []

    if matched_skills:
        strengths.append("简历已覆盖 JD 中的关键技能：" + "、".join(matched_skills) + "。")

    agent_related = [skill for skill in resume_skills if skill in {"ai agent", "agent", "rag", "llm", "大模型"}]
    if agent_related:
        strengths.append("简历中已经出现 AI Agent / LLM 应用相关关键词，适合继续强化项目结果表达。")

    engineering_related = [skill for skill in resume_skills if skill in {"python", "streamlit", "fastapi", "pytest", "git", "json"}]
    if len(engineering_related) >= 2:
        strengths.append("简历体现了一定工程实现能力，可以进一步补充可运行页面、接口、测试或报告下载等证据。")

    if not strengths:
        strengths.append("当前简历与 JD 的显性技能重合较少，建议先补充项目经历中的技术关键词。")

    return strengths


def build_gap_analysis(missing_skills: list[str]) -> list[dict]:
    gap_analysis = []

    for skill in missing_skills:
        priority = "high" if skill in HIGH_PRIORITY_SKILLS else "medium"
        action = f"如果你确实掌握 {skill}，请把它写进项目技术栈或职责描述；如果还不熟，先做一个最小 Demo。"
        gap_analysis.append(
            {
                "skill": skill,
                "priority": priority,
                "action": action,
            }
        )

    return gap_analysis


def build_rewrite_suggestions(missing_skills: list[str], matched_skills: list[str]) -> list[str]:
    suggestions: list[str] = []

    if matched_skills:
        suggestions.append(
            "把已匹配技能写成“动作 + 工具 + 结果”，例如：使用 Python 和 Streamlit 构建可运行的简历匹配页面，并输出结构化 JSON 报告。"
        )

    if missing_skills:
        suggestions.append(
            "优先补充 JD 中出现但简历未体现的技能："
            + "、".join(missing_skills[:5])
            + "。不要只堆关键词，要绑定到项目功能。"
        )

    suggestions.append("项目描述建议按四段组织：项目目标、技术架构、你的职责、可验证成果。")
    suggestions.append("面向 AI Agent 实习时，尽量突出文档解析、结构化输出、工具调用、测试和可复现运行步骤。")

    return suggestions


def build_next_steps(missing_skills: list[str], match_score: int) -> list[str]:
    next_steps: list[str] = []

    if match_score < 60:
        next_steps.append("先补齐 JD 中高频出现的 2-3 个核心技能，再重新计算匹配度。")
    else:
        next_steps.append("匹配度已有基础，下一步重点把项目结果写得更具体。")

    for skill in missing_skills[:3]:
        next_steps.append(f"围绕 {skill} 增加一个可验证的小功能或项目证据。")

    next_steps.append("保存 JSON 分析报告，作为后续接入 LLM API 和 FastAPI 接口的标准输出格式。")

    return next_steps


def analyze_resume_match(jd_text: str, resume_text: str) -> dict:
    if not jd_text.strip() or not resume_text.strip():
        return {
            "status": "missing_input",
            "message": "请先填写岗位 JD 和简历文本。",
            "analysis_mode": "rule_based",
            "match_score": 0,
            "jd_skills": [],
            "resume_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "resume_strengths": [],
            "gap_analysis": [],
            "rewrite_suggestions": [],
            "next_steps": ["输入两段文本后，再点击分析按钮。"],
        }

    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)
    matched_skills = [skill for skill in jd_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

    if not jd_skills:
        match_score = 0
    else:
        match_score = round(len(matched_skills) / len(jd_skills) * 100)

    return {
        "status": "ok",
        "message": "规则版结构化匹配完成。",
        "analysis_mode": "rule_based",
        "match_score": match_score,
        "jd_skills": jd_skills,
        "resume_skills": resume_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_strengths": build_resume_strengths(matched_skills, resume_skills),
        "gap_analysis": build_gap_analysis(missing_skills),
        "rewrite_suggestions": build_rewrite_suggestions(missing_skills, matched_skills),
        "next_steps": build_next_steps(missing_skills, match_score),
    }
