# Streamlit Community Cloud 部署

使用 GitHub 登录 https://share.streamlit.io/ 并完成注册后，创建应用，选择：

- Repository：tubq0212/jd-resume-agent
- Branch：main
- Main file path：app.py
- Python：3.12

第一次部署无需填写 Secrets，默认使用规则分析。部署成功后平台会分配固定的 streamlit.app 网址，也可在可用范围内设置自定义子域名。免费应用闲置后可能休眠，不依赖个人电脑，但唤醒需要等待。

## 可选模型配置

只有计划使用模型增强时才在应用的 Secrets 后台设置 LLM_API_KEY、LLM_BASE_URL 和 LLM_MODEL；不要把真实值写进仓库或发给他人。规则分析不需要模型密钥，先验证基础功能再考虑开启模型。

输入内容用于当前分析；若开启模型增强，文本会发送给所配置的模型服务。演示时优先使用脱敏材料。匹配分数是关键词规则结果，不代表录用概率。

## 上线后检查

1. 输入一段 JD 和简历，检查评分、命中技能、缺失技能及建议。
2. 用脱敏 TXT/DOCX/PDF 检查解析，再下载 JSON 报告。
3. 不填写输入，检查提示。
4. 用手机打开网址，检查输入、上传和下载操作。

requirements.txt 是安装入口，.streamlit/config.toml 已关闭使用情况统计并限制单文件上传大小。不要上传 .env 或 .streamlit/secrets.toml。
