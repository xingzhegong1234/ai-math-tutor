# AI 考研数学助教 📐

基于 **小米 MiMo 大模型 API** 的智能考研数学辅导系统。支持解题、批改、生成类似题、概念讲解，可上传题目截图进行多模态识别。

## 功能

| 模式 | 说明 |
|------|------|
| ✏️ **解题** | 输入数学题，获得完整的步骤式解答 |
| ✅ **批改** | 上传你的解题过程，AI 帮你检查并评分 |
| 📝 **类似题** | 基于当前题目生成难度相当的变式题 |
| 📖 **概念** | 解释数学概念、定理和公式 |

- **图片上传**：拍下题目截图，AI 自动识别并解答
- **深度思考**：切换到旗舰推理模型处理复杂题目
- **对话历史**：自动保存，可收藏和回顾
- **LaTeX 公式渲染**：数学公式清晰显示
- **收藏管理**：标记重要题目便于复习

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
