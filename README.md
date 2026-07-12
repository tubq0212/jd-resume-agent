# JD-Resume 匹配与简历优化 Agent

面向 AI Agent 实习求职场景，解析岗位 JD 与简历内容，输出匹配评分、命中技能、能力缺口、简历优势、改写方向和下一步补强计划。

当前项目是真实可运行版本：规则版默认可用，LLM 增强版可选启用。

## 已实现功能

- Streamlit 交互页面
- 岗位 JD 文本输入
- 简历文本粘贴输入
- TXT / DOCX / PDF 文件上传
- TXT 编码兼容读取：UTF-8 / UTF-8-SIG / GBK
- DOCX 文本解析：`python-docx`
- 文字型 PDF 文本解析：`pypdf`
- 扫描版 / 图片型 PDF 空文本提示
- JD 与简历技能关键词抽取
- 匹配度评分
- 已命中技能与缺失技能分析
- 简历优势分析
- 能力缺口优先级
- 简历改写方向建议
- 下一步补强计划
- 结构化 JSON 输出
- JSON 分析报告下载
- 可选 LLM 增强分析
- 无 API Key 时自动回退规则版
- 多步骤 Agent 流程追踪
- pytest 单元测试

## 技术栈

- Python
- Streamlit
- python-docx
- pypdf
- requests
- python-dotenv
- 结构化 JSON
- LLM API 可选增强
- pytest
- Git

## 项目结构

```text
jd-resume-agent/
  app.py
  requirements.txt
  README.md
  .env.example
  .gitignore
  src/
    jd_resume_agent/
      __init__.py
      agent_pipeline.py
      parser.py
      matcher.py
      llm_advisor.py
  tests/
    test_matcher.py
  outputs/
  work/
```

## 快速开始

进入项目目录：

```bash
cd /d D:\AI-Agent-Projects\jd-resume-agent
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动页面：

```bash
streamlit run app.py
```

打开浏览器：

```text
http://localhost:8501
```

## 使用方式

1. 在左侧输入岗位 JD。
2. 在右侧粘贴简历文本，或上传 TXT / DOCX / PDF 简历。
3. 点击“开始分析”。
4. 查看三个结果页：
   - 匹配概览
   - 简历教练建议
   - JSON 结果
5. 点击“下载 JSON 分析报告”保存结构化结果。

## 多步骤 Agent 流程

项目通过 `agent_pipeline.py` 显式组织分析流程：

1. `input_validation`：检查 JD 与简历文本是否为空。
2. `jd_resume_matching`：抽取 JD 与简历技能关键词，计算匹配度。
3. `gap_analysis`：生成命中技能、缺失技能、优势与补强建议。
4. `llm_enhancement`：在配置 API Key 时调用 LLM 优化建议，否则回退规则版。
5. `structured_output`：输出稳定 JSON，供页面、API 和下载报告复用。

页面侧边栏会展示这套流程，API 返回结果中也包含 `agent_steps` 字段。

## 示例数据

项目提供了两份示例输入，方便演示和测试：

```text
examples/sample_jd.txt
examples/sample_resume.txt
```

使用方式：

1. 打开 `examples/sample_jd.txt`，复制内容到页面左侧“岗位 JD”。
2. 打开 `examples/sample_resume.txt`，复制内容到页面右侧“简历文本”。
3. 点击“开始分析”。

也可以用这两份文本测试 FastAPI `/analyze` 接口。

## LLM 增强配置

默认情况下，项目使用规则版分析，不需要 API Key。

如果要启用 LLM 增强：

1. 复制 `.env.example` 为 `.env`
2. 填写你的 API Key
3. 重启 Streamlit
4. 在左侧侧边栏打开“启用 LLM 增强”

`.env` 示例：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/chat/completions
LLM_MODEL=deepseek-chat
```

注意：`.env` 已加入 `.gitignore`，不要把真实 Key 上传到 GitHub。

## 测试

运行全部测试：

```bash
python -m pytest
```

当前测试覆盖：

- 技能关键词抽取
- 匹配评分
- 结构化教练字段
- JSON 可序列化
- TXT 解析
- DOCX 解析
- PDF 依赖缺失提示
- PDF 空文本提示
- LLM Prompt 构造
- LLM JSON 字段校验
- 无 API Key 自动回退

## 当前能力边界

- PDF 只支持文字型 PDF。
- 扫描版或图片型 PDF 暂不做 OCR，会提示用户改用 DOCX / TXT。
- LLM 增强是可选功能，没有 API Key 时仍能完整运行规则版。
- 当前不会自动投递简历，不爬取招聘网站，不保证 offer。

## FastAPI 接口

启动 API 服务：

```bash
uvicorn src.jd_resume_agent.api:app --reload
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```

分析接口：

```text
POST http://127.0.0.1:8000/analyze
```

请求示例：

```json
{
  "jd_text": "要求熟悉 Python、Streamlit、FastAPI、pytest。",
  "resume_text": "项目使用 Python 和 Streamlit 搭建简历匹配 Demo。",
  "enable_llm": false
}
```

返回结果与 Streamlit 页面使用同一套结构化 JSON。

## 后续路线

- 接入真实 LLM API 并测试返回质量
- 增加 Markdown 报告导出
- 增加示例 JD 和示例简历
- 增加 GitHub Actions 自动运行测试
