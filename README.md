# AI 考研数学助教 📐

基于 **小米 MiMo 大模型 API** 的智能考研数学辅导系统，专为考研数学（高等数学、线性代数、概率论与数理统计）备考设计。

## 项目背景与痛点

考研数学是研究生入学考试中区分度最高、备考最耗时的科目之一。考生在复习过程中普遍面临三大难题：

| 痛点 | 具体表现 | 传统方案的不足 |
|------|---------|--------------|
| **无人即时讲解** | 遇到难题只能硬啃答案解析，无人点拨思路 | 搜题软件只给答案，缺少逐步推导和思路拆解 |
| **缺乏专业批改** | 做完题不知道对错，错了不知错在哪一步、为什么错 | 拍照批改工具准确率低，无法定位具体步骤错误 |
| **题量不够、题型固化** | 做完一道题找不到难度相当的变式题来巩固 | 刷题书题目固定，无法根据薄弱点动态生成同类题 |

**AI 考研数学助教** 正是为解决这些问题而生——它不是一个简单的搜题工具，而是一个具备教学思维的 AI 辅导老师。

## 核心逻辑流

```
用户输入题目（文字描述 或 截图上传）
        │
        ▼
  选择辅导模式
  ┌────┬────┬────┬────┐
  │解题│批改│类似题│概念│
  └──┬─┴──┬─┴──┬─┴──┬─┘
     │    │    │    │
     ▼    ▼    ▼    ▼
  FastAPI 后端根据模式组装专业考研数学提示词
  （含解题规范：步骤编号、方法总结、易错提醒）
        │
        ▼
  调用小米 MiMo API（OpenAI 兼容接口）
  - 快速问答：mimo-v2-flash
  - 深度推理：mimo-v2-pro（旗舰推理模型，1M 上下文）
        │
        ▼
  AI 返回完整解答：
  ✅ 逐步推导 → ✅ 方法总结 → ✅ 易错提醒 → ✅ 相关知识
        │
        ▼
  前端 KaTeX 渲染 LaTeX 数学公式，清晰展示
        │
        ▼
  自动保存至 SQLite 数据库 ←→ 支持收藏标记、历史回顾
```

## 四大辅导模式

| 模式 | 触发场景 | AI 行为 |
|------|---------|--------|
| ✏️ **解题** | 遇到不会做的题 | 给出完整的逐步推导，标注每步依据，总结解法技巧，指出易错点 |
| ✅ **批改** | 自己做了一遍想确认对错 | 逐步骤审查解题过程，定位错误步骤并解释原因，给出评分和改进建议 |
| 📝 **类似题** | 想巩固某个考点 | 基于当前题目自动生成难度相当、考点一致的变式题，并附完整解答 |
| 📖 **概念讲解** | 对某个定理/公式理解不透 | 用通俗语言解释定义与性质，辅以典型例题和常见考法分析 |

## 特色功能

- **🖼 多模态输入**：拍下题目截图或手写解题过程，AI 自动识别并处理（基于 MiMo-V2-Omni 视觉能力）
- **🧠 深度思考模式**：一键切换旗舰推理模型（mimo-v2-pro），应对压轴题和复杂证明
- **📝 LaTeX 公式渲染**：数学公式以印刷级质量显示（KaTeX 引擎），告别 ASCII 乱码
- **💾 对话自动保存**：所有问答记录存入 SQLite，随时回溯复习
- **⭐ 收藏标记**：标记重点题目形成个人错题本，聚焦薄弱环节
- **🔌 轻量部署**：纯 Python 后端 + 原生前端，一条命令启动，无需复杂环境配置

## 快速开始

### 1. 获取 MiMo API Key

1. 打开 [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 注册登录
2. 创建 API Key，复制 `sk-` 开头的密钥
3. 申请 Token 额度（[100t.xiaomimimo.com](https://100t.xiaomimimo.com)）

### 2. 配置环境

```bash
# 克隆项目
git clone https://github.com/你的用户名/ai-math-tutor.git
cd ai-math-tutor

# 安装依赖
pip install -r backend/requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 MIMO_API_KEY
```

### 3. 启动

```bash
# 从项目根目录启动
python -m backend.main

# 或者用 uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

打开浏览器访问 **http://localhost:8000** 即可使用。

## 项目结构

```
ai-math-tutor/
├── backend/
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置（从 .env 读取）
│   ├── requirements.txt
│   ├── api/
│   │   ├── mimo.py        # MiMo API 客户端
│   │   └── routes.py      # REST API 路由
│   ├── models/
│   │   └── database.py    # SQLite 数据库
│   └── services/
│       └── prompts.py     # 提示词模板
├── frontend/
│   ├── index.html          # 主页面
│   ├── css/style.css       # 样式
│   └── js/app.js           # 前端逻辑
├── uploads/                # 上传的图片
├── .env.example
├── .gitignore
└── README.md
```

## API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送消息（支持上传图片） |
| POST | `/api/chat/json` | 发送消息（JSON 格式，纯文本） |
| GET | `/api/conversations` | 获取对话列表 |
| GET | `/api/conversations/:id` | 获取对话详情及消息 |
| DELETE | `/api/conversations/:id` | 删除对话 |
| POST | `/api/conversations/:id/bookmark` | 切换收藏状态 |
| GET | `/api/health` | 健康检查 |

## 技术栈

- **后端**: Python FastAPI + SQLite
- **前端**: 原生 HTML/CSS/JS + KaTeX + marked
- **AI**: 小米 MiMo API (OpenAI 兼容)
- **模型**: mimo-v2-flash (快速) / mimo-v2-pro (深度推理)

## 许可

MIT
