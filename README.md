# JD-Resume 匹配与简历优化 Agent

把岗位 JD 与简历放在一起，检查技能关键词覆盖情况，并给出修改建议。可以粘贴文本，也可以上传 TXT、DOCX 或文字型 PDF，分析结果支持下载为 JSON。

[在线使用](https://jd-resume-agent-rnhcdfpzivrbdjubjrtbcj.streamlit.app/) · [云端配置](CLOUD_DEPLOYMENT.md)

## 分析过程

默认按关键词表抽取技能，以“简历命中的 JD 技能数 / JD 中识别到的技能数”计算分数，再整理缺失项和修改建议。例如，JD 包含 Python、FastAPI、pytest，简历只写了 Python，覆盖分数约为 33。

页面中的“启用 LLM 增强”会调用配置的模型服务，补充优势、缺口和改写建议；匹配分数仍由规则计算。未配置密钥或模型调用失败时，保留规则结果。

`agent_pipeline.py` 是固定的分析流水线，组织输入校验、匹配、建议和输出步骤，不是多个独立 Agent 之间的自主协作。

## 本地运行

```powershell
git clone https://github.com/tubq0212/jd-resume-agent.git
cd jd-resume-agent
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

打开 `http://localhost:8501`。可以用 `examples/sample_jd.txt` 和 `examples/sample_resume.txt` 试用；两份文件均为虚构样例。

启用模型前，将 `.env.example` 复制为 `.env`，填写密钥、完整聊天接口地址和模型名称：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/chat/completions
LLM_MODEL=deepseek-chat
```

`LLM_BASE_URL` 需要包含 `/chat/completions` 路径。修改后重启页面，再打开“启用 LLM 增强”。云端应用在 Streamlit 的 Secrets 中填写同名配置。

## 代码入口

| 文件 | 用途 |
| --- | --- |
| `app.py` | Streamlit 页面与报告下载 |
| `src/jd_resume_agent/parser.py` | TXT、DOCX、PDF 文本提取 |
| `src/jd_resume_agent/matcher.py` | 关键词表、评分和规则建议 |
| `src/jd_resume_agent/llm_advisor.py` | 模型请求、JSON 校验与失败回退 |
| `src/jd_resume_agent/agent_pipeline.py` | 组织分析步骤 |
| `src/jd_resume_agent/api.py` | 复用同一流程的 FastAPI 接口 |

需要单独启动 API 时运行：

```powershell
.venv\Scripts\python.exe -m uvicorn src.jd_resume_agent.api:app --reload
```

`POST /analyze` 接收 `jd_text`、`resume_text` 和可选的 `enable_llm`；`GET /health` 返回服务状态。Streamlit 云端演示只部署页面，未单独部署这组 API。

## 使用限制

- 分数表示词表范围内的技能覆盖，不能判断实际能力、项目真实性或录用概率。当前词表主要面向 Python 和 LLM 应用岗位。
- 扫描件 PDF 暂不支持 OCR；提取不到文字时需要改用文本或 DOCX。
- 规则建议会重复，不会替用户核实经历；模型建议也需要人工检查。
- 开启模型增强会将输入文本发送给所配置的服务商。公开演示请使用脱敏内容。

## 测试

```powershell
.venv\Scripts\python.exe -m pytest -q
```

测试覆盖文本解析、关键词匹配、评分、模型结果校验、规则回退和接口响应，不需要真实模型密钥。
