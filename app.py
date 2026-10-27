import json

import streamlit as st

from src.jd_resume_agent.agent_pipeline import get_agent_steps, run_agent_pipeline
from src.jd_resume_agent.llm_advisor import llm_is_configured
from src.jd_resume_agent.parser import read_docx_file, read_pdf_file, read_txt_file


st.set_page_config(
    page_title="JD-Resume 匹配与简历优化 Agent",
    page_icon="🧭",
    layout="wide",
)


st.title("JD-Resume 匹配与简历优化 Agent")
st.caption("解析岗位 JD 和简历内容，输出匹配评分、能力缺口和改写建议。")
st.caption("公开演示请使用脱敏材料。规则分数反映关键词覆盖，不代表录用概率；开启模型增强会将输入发送给配置的模型服务。")

with st.sidebar:
    st.subheader("分析模式")
    enable_llm = st.toggle("启用 LLM 增强", value=False)
    if enable_llm:
        if llm_is_configured():
            st.success("已检测到 LLM_API_KEY")
        else:
            st.warning("未检测到 LLM_API_KEY，将自动使用规则版。")

    with st.expander("多步骤 Agent 流程"):
        for index, step in enumerate(get_agent_steps(), start=1):
            st.markdown(f"{index}. **{step['name']}**：{step['description']}")

left, right = st.columns(2)

with left:
    jd_text = st.text_area(
        "岗位 JD",
        height=320,
        placeholder="粘贴 AI Agent 实习岗位 JD，例如岗位职责、任职要求、技术栈等。",
    )

with right:
    uploaded_resume = st.file_uploader("上传 TXT / DOCX / PDF 简历", type=["txt", "docx", "pdf"])
    uploaded_resume_text = ""

    if uploaded_resume is not None:
        file_bytes = uploaded_resume.getvalue()
        file_name = uploaded_resume.name.lower()

        try:
            if file_name.endswith(".docx"):
                uploaded_resume_text = read_docx_file(file_bytes)
            elif file_name.endswith(".pdf"):
                uploaded_resume_text = read_pdf_file(file_bytes)
            else:
                uploaded_resume_text = read_txt_file(file_bytes)

            st.success(f"已读取文件：{uploaded_resume.name}")
        except RuntimeError as exc:
            st.error(str(exc))

    resume_text = st.text_area(
        "简历文本",
        value=uploaded_resume_text,
        height=320,
        placeholder="可以粘贴简历文本，也可以上传 TXT / DOCX / PDF 文件自动解析。",
    )


if st.button("开始分析", type="primary", use_container_width=True):
    result = run_agent_pipeline(jd_text, resume_text, enable_llm=enable_llm)

    st.subheader("分析结果")
    st.metric("匹配度", f"{result['match_score']} / 100")
    st.caption(f"分析模式：{result['analysis_mode']}")
    if result.get("llm_status") == "failed":
        st.warning(f"LLM 增强失败，已回退规则版：{result.get('llm_error')}")

    if result["status"] != "ok":
        st.warning(result["message"])
    else:
        tab_summary, tab_advice, tab_json = st.tabs(["匹配概览", "简历教练建议", "JSON 结果"])

        with tab_summary:
            col1, col2 = st.columns(2)

            with col1:
                st.write("已命中 JD 技能")
                st.write(result["matched_skills"] or "暂无")

            with col2:
                st.write("缺失 JD 技能")
                st.write(result["missing_skills"] or "暂无")

            st.write("简历优势")
            for strength in result["resume_strengths"]:
                st.markdown(f"- {strength}")

        with tab_advice:
            st.write("能力缺口优先级")
            if result["gap_analysis"]:
                for item in result["gap_analysis"]:
                    st.markdown(f"- **{item['skill']}**（{item['priority']}）：{item['action']}")
            else:
                st.success("JD 中识别到的技能已全部命中。")

            st.write("改写方向")
            for suggestion in result["rewrite_suggestions"]:
                st.markdown(f"- {suggestion}")

            st.write("下一步补强计划")
            for step in result["next_steps"]:
                st.markdown(f"- {step}")

        with tab_json:
            st.json(result, expanded=True)

        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            "下载 JSON 分析报告",
            data=result_json,
            file_name="jd_resume_match_report.json",
            mime="application/json",
            use_container_width=True,
        )

    if result["status"] != "ok":
        st.json(result, expanded=True)
else:
    st.info("先输入 JD 和简历文本，然后点击“开始分析”。")
