# AI 爽剧工厂 (AI-Shuangju-Factory) 🤖🎬💰

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

这是我在今日头条系列文章 **《我把“AI提款机”的制造图纸，公开了》** 中展示的完整项目代码。

这是一个基于大语言模型（LLM）和 Agno 智能体框架，能够自动化生产“爽剧”剧本大纲的AI工具。它旨在将传统剧本创作中高度依赖灵感的“策划”环节，转变为一个稳定、高效、可规模化的工业流程，赋能内容创作者在500亿规模的短剧市场中抢占先机。

---

## ✨ 功能特性

-   **🧠 战略蓝图生成**: 只需输入一个核心主题，AI即可自动生成整季的顶层设计，包括故事梗概、核心冲突、人物设定和分集标题。
-   **📝 场景节拍细化**: 基于生成的战略蓝图，AI能进一步创作每一集的详细大纲，具体到每个场景（Beat）的时长、钩子、反转和制作提示。
-   **🔒 结构化输出**: 借助 Pydantic，强制 AI 输出稳定可靠的 JSON 格式，彻底告别“随心所欲”的文本生成，保证了内容的工业可用性。
-   **🔧 知识库与工具**: 内置了经过市场验证的“爽点套路库”，并将其封装为 AI 可随时调用的工具，确保内容紧贴市场偏好。
-   **📄 一键导出**: 自动将生成的完整剧本策划案，格式化为清晰易读的 Markdown 文件，方便团队协作与审阅。

## 🚀 快速开始

请确保你的环境中已安装 Python 3.8 或更高版本。

### 1. 克隆仓库

```bash
git clone [https://github.com/ljj314zz/AI-Shuangju-Factory.git](https://github.com/ljj314zz/AI-Shuangju-Factory.git)
cd AI-Shuangju-Factory
```


### 2. 创建并激活虚拟环境

- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. 安装依赖

项目依赖已在 `requirements.txt` 文件中列出。

```bash
pip install -r requirements.txt
```

### 4. 配置 API 密钥

本项目需要使用 OpenAI 的 API Key。

首先，复制 `.env.example` 文件并重命名为 `.env`：
```bash
cp .env.example .env
```
然后，编辑 `.env` 文件，填入你的 API Key：
```
# .env
OPENAI_API_KEY="sk-YourSuperSecretApiKey"
# OPENAI_BASE_URL="[https://api.openai.com/v1](https://api.openai.com/v1)" # 如果需要代理，可以在这里配置
```

## 🛠️ 如何使用

本项目通过命令行启动，核心脚本为 `main.py` 。

#### 基础用法

输入一个你感兴趣的主题，AI 将为你构建整个故事：

```bash
python main.py --theme "被轻视的实习生用代码逆袭整个技术部"
```

#### 高级用法

你可以通过参数，更精细地控制生成内容：

```bash
python main.py --theme "穿越古代赘婿的爽局" --genre "古装" --audience "男性向"
```

-   `--theme`: **(必需)** 故事核心主题或一句话创意。
-   `--genre`: 类型，如 都市/古装/职场 等 (默认: `都市`)。
-   `--audience`: 目标受众，如 男性向/女性向 (默认: `泛用户`)。
-   `--episodes`: 总集数 (默认: `12`)。
-   `--minutes`: 每集分钟数 (默认: `5`)。
-   `--max_episodes_to_expand`: 生成详细大纲的最大集数 (默认: `3`)，用于快速预览。
-   `--outfile`: 输出的 Markdown 文件名 (默认: `shuangju_script.md`)。

运行结束后，你会在项目根目录下找到生成的 `.md` 文件。

## 📜 输出示例

```markdown
# 爽剧项目：被轻视的实习生用代码逆袭整个技术部
- 类型：都市 - 受众：泛用户
- 集数：12 - 每集：3 分钟

**一句话梗概（Premise）**：实习生林默，凭借一行“无人能懂”的神秘代码，从技术部的“小透明”逆袭为令所有大佬侧目的技术核心，并揭开公司内部的惊天秘密。

---
## 第 1 集 · 没人要的“垃圾代码”？
**开场钩子：** 项目经理当众把林默的代码文档摔在地上，怒斥：“这是什么垃圾！明天你不用来了！”

### 场景节拍（Beats）
- [1] 耻辱时刻 · 30s · 开放式办公区
  - 梗概：项目经理当众羞辱实习生林默。同事们窃窃私语，无人为他说话。
  - 钩子：经理将一份“离职申请表”丢到林默桌上。
- [2] 午夜机房 · 60s · 公司服务器机房
  - 梗概：林默深夜潜入机房，看着屏幕上滚动的红色警报，只输入了一行神秘指令，整个系统的警报瞬间消失。
  - 金句：“真正的‘垃圾’，可不是我的代码……”

**结尾悬念：** 第二天清晨，公司CEO的手机收到一条系统最高权限的告警短信：“核心数据库已被未知用户接管。”
```

## 💡 技术实现

本项目的工作流分为两步：
1.  **蓝图规划 (Blueprint Generation)**: 第一个 Agent 接收用户主题，进行顶层设计，输出结构化的 `SeasonBlueprint`。
2.  **大纲细化 (Outline Expansion)**: 第二个 Agent 继承蓝图的上下文，对指定集数进行创作，输出结构化的 `EpisodeOutline`。

-   **核心框架**: [Agno](https://github.com/elos-dev/agno) - 用于构建和编排具备记忆、工具使用和结构化输出能力的 AI 智能体。
-   **数据校验**: [Pydantic](https://docs.pydantic.dev/) - 保证 AI 的输出始终是我们期望的、干净、可靠的数据结构。

## 展望 (TODO)

-   [ ] **🧠 长期记忆**: 集成向量数据库，让 AI 能够处理百集长剧，并保持人物、情节的一致性。
-   [ ] **🌐 模型兼容**: 增加对更多 LLM 的支持，如 `Claude`、`Gemini` 等。
-   [ ] **🖥️ Web 界面**: 开发一个简单的 Gradio / Streamlit 界面，让非开发者也能轻松使用。
-   [ ] **🖥️ 爽剧重写**: 读取爽局视频，生成剧本及蓝图，重新生成一份剧本。

## 🤝 贡献 & 交流

欢迎提出 Issue 或提交 Pull Request！

你也可以在 [今日头条](你的头条主页链接) 上关注我，获取更多关于 AI 工程化和商业应用的干货。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。