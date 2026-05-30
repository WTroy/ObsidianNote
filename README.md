# 我的知识库

基于 Obsidian + 本地大模型构建的个人知识管理系统。笔记写好扔 Inbox，AI 自动帮你分类、打标签、加双链。

---

## 一、环境搭建

### 1.1 安装 Obsidian

1. 下载：https://obsidian.md/
2. 安装后打开，点击 **Open folder as vault**
3. 选择本 vault 目录：
   ```
   /Users/troy/Developer/ClaudeCode/vault
   ```
4. 输入名称（如"我的知识库"），点击 Create

### 1.2 安装社区插件

进入 Obsidian → 左下角设置齿轮 → 第三方插件 → 关闭安全模式 → 浏览

依次搜索并安装以下插件，每个装完点 **Enable**：

| 插件 | 用途 |
|------|------|
| **Dataview** | 用类 SQL 语法查询笔记，构建动态仪表盘 |
| **Templater** | 模板引擎，自动化笔记创建 |
| **Calendar** | 日历视图，配合日记使用 |
| **Obsidian Copilot** | AI 对话助手，支持 RAG 问答 |
| **Smart Connections** | 语义搜索，自动发现笔记关联 |

### 1.3 配置 Templater

设置 → 左侧栏找到 **Templater**：
- **Template folder**：`70-Templates`
- **Trigger Templater on new file creation**：开启

### 1.4 配置日记

设置 → 核心插件 → **日记**（Daily notes）→ 开启：
- **新日记存放位置**：`50-Daily`
- **日记模板**：`70-Templates/daily-note.md`

### 1.5 配置 Obsidian Copilot（AI 助手）

设置 → 左侧栏找到 **Copilot**：

**Chat Model（对话模型）**：
- Provider：OpenAI Compatible
- Base URL：`http://127.0.0.1:8000/v1`
- API Key：见 `90-System/config.json`
- Model Name：`gemma-4-e4b-it-8bit`

**Embedding Model（嵌入模型）**：
- Provider：OpenAI Compatible
- Base URL：`http://127.0.0.1:8000/v1`
- API Key：同上
- Model Name：`bge-m3-mlx-4bit`

**开启 Vault QA Mode**（对整个笔记库提问）

### 1.6 安装 Python 环境

```bash
conda activate obsidian
```

环境已预装 Python 3.12，无需额外安装依赖（脚本使用 Python 标准库）。

### 1.7 启动本地 LLM 服务

确保本地 LLM 服务已运行在 `http://127.0.0.1:8000`，提供以下模型：
- `gemma-4-e4b-it-8bit`（对话模型）
- `bge-m3-mlx-4bit`（嵌入模型）

---

## 二、目录结构

```
vault/
├── 00-Inbox/           收件箱：所有新笔记的第一站
├── 10-Projects/        项目：有明确目标和截止日期的事
├── 20-Areas/           领域：持续关注的责任区（健康、财务等）
├── 30-Resources/       资料：感兴趣的主题、参考资料、学习材料
├── 40-Archives/        归档：已完成或不再活跃的内容
├── 50-Daily/           日记：每日记录
├── 60-MOC/             内容地图：按主题组织的导航页
├── 70-Templates/       模板：笔记模板（不要手动编辑）
├── 80-Attachments/     附件：图片、PDF 等
├── 90-System/          系统：配置文件、日志等
├── Home.md             首页仪表盘（Dataview 动态展示）
├── organize.py         AI 自动整理脚本
├── scheduler.py        定时调度器
└── README.md           本文件
```

### 各目录详细说明

#### `00-Inbox/` — 收件箱

所有新笔记的第一站。不想分类、来不及整理的东西全扔这里。

- 快速想法、灵感、随手记录都放这里
- AI 整理脚本会自动把笔记移到对应目录
- 手动整理时：移到对应目录 + 加 `[[双链]]` + 加 `#标签`

#### `10-Projects/` — 项目

正在进行的、有明确目标和截止日期的事情。

- 用 `70-Templates/project.md` 模板创建
- 项目完成后移到 `40-Archives/`
- 示例：开发一个小程序、准备某个考试、策划一次旅行

#### `20-Areas/` — 领域

没有截止日期，但需要长期维护的领域。

- 可以建子文件夹
- 示例：`20-Areas/健康/`、`20-Areas/财务/`、`20-Areas/技术学习/`

#### `30-Resources/` — 资料

感兴趣的主题、参考资料、学习材料。

- 读书笔记用 `book-note.md` 模板
- 知识概念用 `knowledge-card.md` 模板
- 用 `[[双链]]` 把相关概念连起来

#### `40-Archives/` — 归档

从其他目录搬过来的已完成内容。

- 只进不出，不要从这里搬东西回去
- 定期清理不需要的

#### `50-Daily/` — 日记

每日记录，自动生成。

- 点日历侧边栏的日期自动生成（已配好模板）
- 写什么都可以：工作记录、心情、想法

#### `60-MOC/` — 内容地图

按主题组织的"导航页"，汇集某个主题下的所有相关笔记。

- 用 `MOC-模板.md` 创建
- 当某个主题的笔记超过 5 篇时，考虑建一个 MOC
- 示例：`MOC-自媒体.md` 链接所有自媒体相关笔记

#### `70-Templates/` — 模板

存放所有笔记模板，**不要手动编辑**。

| 模板文件 | 用途 | 使用方式 |
|----------|------|----------|
| `daily-note.md` | 日记 | 日历自动调用 |
| `book-note.md` | 读书笔记 | `Cmd+Shift+T` 选模板 |
| `knowledge-card.md` | 知识卡片 | `Cmd+Shift+T` 选模板 |
| `meeting-note.md` | 会议记录 | `Cmd+Shift+T` 选模板 |
| `project.md` | 项目 | `Cmd+Shift+T` 选模板 |
| `weekly-review.md` | 周回顾 | `Cmd+Shift+T` 选模板 |

#### `80-Attachments/` — 附件

图片、PDF、音频等文件。Obsidian 会自动把粘贴的图片存到这里。

#### `90-System/` — 系统

| 文件 | 用途 |
|------|------|
| `config.json` | LLM 配置（API 地址、密钥、模型名） |
| `organize.log` | 整理脚本的运行日志 |

#### 自动管理目录（不用手动操作）

| 目录 | 来源 | 用途 |
|------|------|------|
| `copilot/` | Obsidian Copilot 插件 | AI 对话记录和内置提示词 |
| `.smart-env/` | Smart Connections 插件 | 笔记的向量嵌入数据 |
| `.obsidian/` | Obsidian 核心 | 应用配置和插件数据 |

---

## 三、LLM 配置

### 3.1 配置文件

所有 LLM 相关配置集中在 `90-System/config.json`：

```json
{
  "llm": {
    "api_url": "http://127.0.0.1:8000/v1/chat/completions",
    "api_key": "sk-xxx...",
    "model": "gemma-4-e4b-it-8bit"
  }
}
```

| 字段 | 说明 |
|------|------|
| `api_url` | LLM 服务的 API 地址（OpenAI 兼容格式） |
| `api_key` | API 密钥 |
| `model` | 对话模型名称 |

### 3.2 当前模型

| 模型 | 用途 | 端口 |
|------|------|------|
| `gemma-4-e4b-it-8bit` | 对话、问答、笔记分析 | `127.0.0.1:8000` |
| `bge-m3-mlx-4bit` | 嵌入向量、语义搜索 | `127.0.0.1:8000` |

### 3.3 更换模型

修改 `90-System/config.json` 中的 `model` 字段即可，无需重启其他服务。

---

## 四、操作手册

### 4.1 日常写笔记

1. 在 Obsidian 中按 `Cmd+N` 新建笔记
2. 写好内容，保存到 `00-Inbox/`
3. 完成，不用管分类

### 4.2 写日记

1. 点击左侧 Calendar 侧边栏上的今天日期
2. 自动生成带模板的日记文件
3. 写当天的记录

### 4.3 使用模板

1. 新建笔记
2. 按 `Cmd+Shift+T`（或 `Cmd+P` → 输入 "Templater: Insert Template"）
3. 选择模板：book-note、knowledge-card、meeting-note、project、weekly-review

### 4.4 AI 自动整理

#### 手动执行

```bash
conda activate obsidian

# 查看建议（不动文件）
python organize.py --dry-run

# 交互式整理（每篇确认）
python organize.py

# 全自动整理
python organize.py --auto
```

#### 自动执行

调度器 `scheduler.py` 已配置为每天凌晨 1:00 自动执行 `organize.py --auto`。

```bash
# 启动调度器（后台运行）
conda activate obsidian
nohup python scheduler.py > /dev/null 2>&1 &

# 查看是否在运行
ps aux | grep scheduler.py

# 停止调度器
pkill -f scheduler.py

# 查看运行日志
cat 90-System/organize.log
```

#### 整理效果

AI 会自动完成：
- **分类**：把笔记移到 `10-Projects`、`20-Areas`、`30-Resources` 或 `40-Archives`
- **打标签**：在 frontmatter 中添加 2-4 个标签
- **加双链**：在笔记末尾添加相关笔记的 `[[双链]]`
- **写摘要**：在 frontmatter 中添加一句话摘要

### 4.5 AI 对话问答

1. 点击右侧边栏的 Copilot 图标
2. 直接打字聊天（使用 `gemma-4-e4b-it-8bit` 模型）
3. 切换到 **Vault QA** 模式可以对整个笔记库提问

#### Copilot 常用操作

| 操作 | 方法 |
|------|------|
| 对话问答 | Copilot 侧边栏打字 |
| 选中文本提问 | 选中文字 → `Cmd+P` → Copilot Chat |
| 总结/翻译 | 选中文本 → Copilot 侧边栏 → 用 `/` 命令 |

### 4.6 语义搜索（Smart Connections）

打开任意笔记，右侧 Smart Connections 面板会自动显示语义相关的笔记。

### 4.7 首页仪表盘

点击 `Home.md` 查看：
- 最近修改的笔记
- 进行中的项目
- 正在读的书
- 本周日记
- Inbox 里待整理的笔记

### 4.8 知识图谱

按 `Cmd+G` 打开 Graph View，可视化查看所有笔记之间的链接关系。

---

## 五、快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+N` | 新建笔记 |
| `Cmd+O` | 快速打开笔记（模糊搜索） |
| `Cmd+Shift+T` | 插入模板 |
| `Cmd+Shift+D` | 打开今天的日记 |
| `Cmd+P` | 命令面板（万能入口） |
| `Cmd+E` | 切换编辑/预览模式 |
| `Cmd+G` | 打开知识图谱 |

---

## 六、使用流程总结

```
写笔记 → 放 00-Inbox
            ↓
    每天凌晨 1:00 自动整理（或手动 python organize.py --auto）
            ↓
    AI 自动：分类 + 打标签 + 加双链 + 写摘要
            ↓
    笔记出现在对应目录，Graph View 中有连线
```

核心理念：**你只管写，AI 帮你整理。**
