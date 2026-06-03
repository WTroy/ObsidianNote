---
title: Claude Code为什么它就是比别人好用？
source: 有道云笔记
imported: true
---

⼀⽂了解  Anthropic 的  Claude Code 源码：为什么它就是⽐别⼈好⽤？
2026 年 3 ⽉ 31 ⽇，安全研究者  Chaofan Shou 发现  Anthropic 发布到  npm 的  Claude Code 包中， source map ⽂件没
有被剥离。
这意味着：Claude Code 的完整  TypeScript 源码， 51.2 万⾏， 1903 个⽂件，就这样暴露在了公⽹上。
我当然不可能在短短数⼩时内看完这么多代码，因此，我带着三个问题去读这份源码：
读完之后，我的第⼀反应是：这不是⼀个  AI 编程助⼿，这是⼀个操作系统。
想象你雇了⼀个远程程序员，给他你电脑的远程访问权限。
你会怎么做？
如果你是  Cursor 的做法：你让他坐在你旁边，每次他要敲命令之前你看⼀眼，点个 " 允许 " 。简单粗暴，但你得⼀直盯
着。
如果你是  GitHub Copilot Agent 的做法：你给他⼀台全新的虚拟机，让他在⾥⾯随便折腾。搞完了把代码提交上来，
你审核后再合并。安全，但他看不到你本地的环境。
如果你是  Claude Code 的做法：
你让他直接⽤你的电脑 ⸺ 但你给他配了⼀套极其精密的安检系统。他能做什么、不能做什么、哪些操作需要你点头、
哪些可以⾃⼰来、甚⾄他想⽤  rm -rf 都要经过 9 层审查才能执⾏。
这就是三种完全不同的安全哲学：
⼀⽂了解  Anthropic 的  Claude Code 源码：为什么它就是⽐别⼈好⽤？
2026 年 3 ⽉ 31 ⽇，安全研究者  Chaofan Shou 发现  Anthropic 发布到  npm 的  Claude Code 包中， source map ⽂件没
有被剥离。
这意味着：Claude Code 的完整  TypeScript 源码， 51.2 万⾏， 1903 个⽂件，就这样暴露在了公⽹上。
我当然不可能在短短数⼩时内看完这么多代码，因此，我带着三个问题去读这份源码：
读完之后，我的第⼀反应是：这不是⼀个  AI 编程助⼿，这是⼀个操作系统。
想象你雇了⼀个远程程序员，给他你电脑的远程访问权限。
你会怎么做？
如果你是  Cursor 的做法：你让他坐在你旁边，每次他要敲命令之前你看⼀眼，点个 " 允许 " 。简单粗暴，但你得⼀直盯
着。
如果你是  GitHub Copilot Agent 的做法：你给他⼀台全新的虚拟机，让他在⾥⾯随便折腾。搞完了把代码提交上来，
你审核后再合并。安全，但他看不到你本地的环境。
如果你是  Claude Code 的做法：
Claude Code 和其他  AI 编程⼯具到底有什么本质区别？
为什么它写代码的 " ⼿感 " 就是⽐别⼈好？
51 万⾏代码⾥，到底藏着什么？
⼀、先讲⼀个故事：如果你要雇⼀个远程程序员
Claude Code 和其他  AI 编程⼯具到底有什么本质区别？
为什么它写代码的 " ⼿感 " 就是⽐别⼈好？
51 万⾏代码⾥，到底藏着什么？
⼀、先讲⼀个故事：如果你要雇⼀个远程程序员

你让他直接⽤你的电脑 ⸺ 但你给他配了⼀套极其精密的安检系统。他能做什么、不能做什么、哪些操作需要你点头、
哪些可以⾃⼰来、甚⾄他想⽤  rm -rf 都要经过 9 层审查才能执⾏。
这就是三种完全不同的安全哲学：
为什么  Anthropic 选了最难的那条路？
因为只有这样， AI 才能⽤你的终端、你的环境、你的配置来⼲活 ⸺ 这才是 " 真正帮你写代码 " ，⽽不是 " 在⼀个⼲净房间
⾥给你写⼀段代码然后复制过来 " 。
但代价是什么？他们为此写了  51 万⾏代码。
⼤多数⼈以为  AI 编程⼯具是这样的：
plaintext
Claude Code 实际是这样的：
plaintext
⼆、你以为的  Claude Code vs 实际的  Claude Code
⽤户输⼊  → 调⽤  LLM API → 返回结果  → 显示给⽤户1
⽤户输⼊1
→ 动态组装  7 层系统提示词2
→ 注⼊  Git 状态、项⽬约定、历史记忆3
→ 42 个⼯具各⾃附带使⽤⼿册4
→ LLM 决定使⽤哪个⼯具5
→ 9 层安全审查（ AST 解析、 ML 分类器、沙箱检查 ... ）6
→ 权限竞争解析（本地键盘  / IDE / Hook / AI 分类器  同时竞争）7
→ 200ms 防误触延迟8
→ 执⾏⼯具9
→ 结果流式返回10
→ 上下⽂接近极限？ → 三层压缩（微压缩  → ⾃动压缩  → 完全压缩）11
→ 需要并⾏？ → ⽣成⼦  Agent 蜂群12

相信⼤家都很好奇上⾯的是什么，不着急，让我们逐个拆开看。
打开  src/constants/prompts.ts ，你会看到这个函数：
typescript
注意到那个  SYSTEM_PROMPT_DYNAMIC_BOUNDARY 了吗？
这是⼀个缓存分界线。分界线上⾯的内容是静态的， Claude API 可以缓存它们，节省  token 费⽤。分界线下⾯的内容
是动态的 ⸺ 你当前的  Git 分⽀、你的  CLAUDE.md 项⽬配置、你之前告诉它的偏好记忆 …… 每次对话都不⼀样。
这意味着什么？
Anthropic 把提示词当成了编译器的输出来优化。静态部分是 " 编译后的⼆进制 " ，动态部分是 " 运⾏时参数 " 。这样做的
好处是：
→ 循环直到任务完成13
三、第⼀个秘密：提示词不是写出来的，是 " 拼装 " 出来的
export async function getSystemPrompt(1

```yaml
tools: Tools,
model: string,
additionalWorkingDirectories?: string[],
mcpClients?: MCPServerConnection[],
): Promise<string[]> {
return [
```

// --- 静态内容（可缓存） ---8
getSimpleIntroSection(outputStyleConfig),9
getSimpleSystemSection(),10
getSimpleDoingTasksSection(),11
getActionsSection(),12
getUsingYourToolsSection(enabledTools),13
getSimpleToneAndStyleSection(),14
getOutputEfficiencySection(),15
// === 缓存边界  ===17
...(shouldUseGlobalCacheScope() ? [SYSTEM_PROMPT_DYNAMIC_BOUNDARY] : []),18
// --- 动态内容（每次不同） ---20
...resolvedDynamicSections,21

```
].filter(s => s !== null)
}
```

省钱1.

：静态部分⾛缓存，不重复计费
：缓存命中直接跳过这些  token 的处理
：动态部分让每次对话都能感知当前环境
更让我震惊的是：每个⼯具⽬录下都有⼀个  prompt.ts ⽂件 ⸺这是专⻔写给  LLM 看的使⽤⼿册。
看看  BashTool 的（ src/tools/BashTool/prompt.ts ，约  370 ⾏）：
plaintext
这不是写给⼈看的⽂档，这是写给  AI 看的⾏为准则。每次  Claude Code 启动时，这些规则都会被注⼊到系统提示词
中。
这就是为什么  Claude Code 从不会擅⾃  git push --force ，⽽某些⼯具会 ⸺不是模型更聪明，是提示词⾥已经把规矩
讲清楚了。
⽽且  Anthropic 内部版本和你⽤的不⼀样
typescript
ant 就是  Anthropic 内部员⼯。他们的版本有更详细的代码⻛格指引（ " 不写注释除⾮  WHY 不明显 " ）、更激进的输出
策略（ " 倒⾦字塔写作法 " ），以及⼀些仍在  A/B 测试的实验功能（ Verification Agent 、 Explore & Plan Agent ）。
这说明  Anthropic ⾃⼰就是  Claude Code 最⼤的⽤户。他们在⽤⾃⼰的产品来开发⾃⼰的产品。
快
灵活
⛏ 每个⼯具都有独⽴的 " 使⽤⼿册 "
Git Safety Protocol:1
- NEVER update the git config2
- NEVER run destructive git commands (push --force, reset --hard, 3
checkout .) unless the user explicitly requests4
- NEVER skip hooks (--no-verify) unless the user explicitly requests5
- CRITICAL: Always create NEW commits rather than amending6
代码⾥⼤量出现这样的分⽀：

```yaml
const minimalUniquenessHint =
process.env.USER_TYPE === 'ant'
? '\n- Use the smallest old_string that\'s clearly unique'
: ''
```

四、第⼆个秘密： 42 个⼯具，但你只看到了冰⼭⼀⻆

打开  src/tools.ts ，会看到⼯具注册中⼼：
typescript
42 个⼯具，但⼤部分你从未直接看到过。因为很多⼯具是延迟加载的 ⸺ 只有当  LLM 需要时，才通过  ToolSearchTool
按需注⼊。
为什么这样做呢？
因为每多⼀个⼯具，系统提示词就要多⼀段描述， token 就要多花⼀份钱。 如果你只是想让  Claude Code 帮你改⼀⾏
代码，它不需要加载 " 定时任务调度器 " 和 " 团队协作管理器 " 。
还有⼀个更聪明的设计：
typescript
设置  CLAUDE_CODE_SIMPLE=true ， Claude Code 就只剩三个⼯具： Bash 、读⽂件、改⽂件。这是给极简主义者的
后⻔。
typescript
export function getAllBaseTools(): Tools {1
return [2
AgentTool,3
BashTool,4
FileReadTool, FileEditTool, FileWriteTool,5
GlobTool, GrepTool,6
WebFetchTool, WebSearchTool,7
TodoWriteTool, NotebookEditTool,8
// ... ⼤量条件加载的⼯具  ...9
...(isToolSearchEnabledOptimistic() ? [ToolSearchTool] : []),10

```java
]
}
if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
const simpleTools: Tool[] = [BashTool, FileReadTool, FileEditTool]
return filterToolsByDenyRules(simpleTools, permissionContext)
}
```

 所有⼯具都从同⼀个⼯⼚出来

```yaml
const TOOL_DEFAULTS = {
isEnabled: () => true,
```

注意那些默认值： isConcurrencySafe 默认  false ， isReadOnly 默认  false 。
这叫  fail-closed 设计 ⸺ 如果⼀个⼯具的作者忘了声明安全属性，系统会假设它是 " 不安全的、会写⼊的 " 。 宁可过度
保守，也不漏掉⼀个⻛险。
typescript
FileEditTool 会检查你是否已经⽤  FileReadTool 读过这个⽂件。如果没有，直接报错，不让改。
这就是为什么  Claude Code 不会像某些⼯具那样 " 凭空写⼀段代码覆盖你的⽂件 "⸺ 它被强制要求先理解再修改。
⽤过  Claude Code 的⼈都有⼀个感受：它好像真的认识你。
你告诉它 " 不要在测试中  mock 数据库 " ，下次对话它就不会再  mock 。你告诉它 " 我是后端⼯程师， React 新⼿ " ，它解
释前端代码时就会⽤后端的类⽐。
这背后是⼀个完整的记忆系统。
typescript

```python
isConcurrencySafe: (_input?) => false,    // 默认：不安全
isReadOnly: (_input?) => false,            // 默认：会写⼊
isDestructive: (_input?) => false,
}
export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
return { ...TOOL_DEFAULTS, userFacingName: () => def.name, ...def }
}
```

  **" 先读后改 " 的铁律 **
function getPreReadInstruction(): string {1
return '\n- You must use your `Read` tool at least once in the 2
conversation before editing. This tool will error if you attempt 3
an edit without reading the file.'4
}5
五、第三个秘密：记忆系统 ⸺ 为什么它能 " 记住你 "
  ⽤  AI 来检索记忆

```
const SELECT_MEMORIES_SYSTEM_PROMPT =
`You are selecting memories that will be useful to Claude Code.2
Return a list of filenames for the memories that will clearly
```

Claude Code ⽤  另⼀个  AI（ Claude Sonnet ）来决定 " 哪些记忆和当前对话相关 " 。
不是关键词匹配，不是向量搜索 ⸺ 是让⼀个⼩模型快速扫描所有记忆⽂件的标题和描述，选出最多  5 个最相关的，然
后把它们的完整内容注⼊到当前对话的上下⽂中。
策略是 " 精确度优先于召回率 " ⸺ 宁可漏掉⼀个可能有⽤的记忆，也不塞进⼀个不相关的记忆污染上下⽂。
这是最让我觉得科幻的部分。
代码中有⼀个叫  KAIROS 的特性标志。在这个模式下，⻓会话中的记忆不是存在结构化⽂件⾥，⽽是存在按⽇期的追加
式⽇志中。然后，有⼀个  /dream 技能会在 " 夜间 " （低活跃期）运⾏，把这些原始⽇志蒸馏成结构化的主题⽂件。
plaintext
AI 在 " 睡觉 " 的时候整理记忆。 这已经不是⼯程了，这是仿⽣学。
当你让  Claude Code 做⼀个复杂任务时，它可能悄悄做了这件事：
typescript
be useful (up to 5).4
- If you are unsure if a memory will be useful, do not include it.5
- If a list of recently-used tools is provided, do not select 6
memories that are usage reference for those tools. DO still 7

```sql
select memories containing warnings, gotchas, or known issues.`
```

⏰KAIROS 模式：夜间 " 做梦 "
logs/2026/03/2026-03-30.md  ←  今天的原始⽇志1
↓ /dream 蒸馏2
memory/user_preferences.md  ←  结构化的⽤户偏好⽂件3
memory/project_context.md   ←  结构化的项⽬背景⽂件4
六、第五个秘密：它不是⼀个  Agent ，是⼀群
// AgentTool 的输⼊  schema1
z.object({2

```yaml
description: z.string().describe('A short (3-5 word) description'),
prompt: z.string().describe('The task for the agent to perform'),
subagent_type: z.string().optional(),
model: z.enum(['sonnet', 'opus', 'haiku']).optional(),
run_in_background: z.boolean().optional(),
})
```

它⽣成了⼀个⼦  Agent。
⽽且⼦  Agent 有严格的 " ⾃我意识 " 注⼊，防⽌它递归⽣成更多⼦  Agent ：
typescript
这段代码在说：" 你是⼀个⼯⼈，不是经理。别想着再雇⼈，⾃⼰⼲活。 "
👤 Coordinator 模式：经理模式
在协调器模式下， Claude Code 变成⼀个纯粹的任务编排者，⾃⼰不⼲活，只分配：
plaintext
核⼼原则写在代码注释⾥：
"Parallelism is your superpower" 只读研究任务：并⾏跑。  写⽂件任务：按⽂件分组串⾏跑（避免冲突）。
🗣 **Prompt Cache 的极致优化 **
为了最⼤化⼦  Agent 的缓存命中率，所有  fork ⼦代理的⼯具结果都使⽤相同的占位符⽂本：
plaintext
export function buildChildMessage(directive: string): string {1
return `STOP. READ THIS FIRST.2
You are a forked worker process. You are NOT the main agent.4
RULES (non-negotiable):6
1. Your system prompt says "default to forking." IGNORE IT — 7
that's for the parent. You ARE the fork. 8
Do NOT spawn sub-agents; execute directly.9
2. Do NOT converse, ask questions, or suggest next steps10
3. USE your tools directly: Bash, Read, Write, etc.11
4. Keep your report under 500 words.12
5. Your response MUST begin with "Scope:". No preamble.`13
}14
Phase 1: Research    → 3 个  worker 并⾏搜索代码库1
Phase 2: Synthesis   → 主  Agent 综合理解所有发现2
Phase 3: Implementation → 2 个  worker 分别修改不同⽂件3
Phase 4: Verification   → 1 个  worker 跑测试4
'Fork started — processing in background'1

为什么？因为  Claude API 的  prompt cache 是基于字节级前缀匹配的。如果  10 个⼦  Agent 的前缀字节完全⼀致，那
么只有第⼀个需要 " 冷启动 " ，后⾯  9 个直接命中缓存。
这是⼀个每次调⽤节省⼏美分的优化，但在⼤规模使⽤下，能省下⼤量成本。
所有  LLM 都有上下⽂窗⼝限制。对话越⻓，历史消息越多，最终⼀定会超出限制。
Claude Code 为此设计了三层压缩：
typescript
微压缩只动旧的⼯具调⽤结果 ⸺ 把 "10 分钟前读的那个 500 ⾏⽂件的内容 "替换成   Old tool result content
cleared 。
提示词和对话主线完全保留。
当  token 消耗接近上下⽂窗⼝的  87% （窗⼝⼤⼩  - 13,000 buffer ），⾃动触发。有⼀个熔断器：连续  3 次压缩失败后
停⽌尝试，避免死循环。
让  AI 对整段对话⽣成摘要，然后⽤摘要替换所有历史消息。⽣成摘要时有⼀个严厉的前置指令：
typescript
七、第六个秘密：三层压缩，让对话 " 永不超限 "
  第⼀层：微压缩 ⸺ 最⼩代价
export async function microcompactMessages(messages, toolUseContext,

```
querySource) {
```

// 时间触发：如果上次交互已过很久，服务器缓存已冷2

```java
const timeBasedResult = maybeTimeBasedMicrocompact(messages, querySource)
if (timeBasedResult) return timeBasedResult
```

// 缓存编辑路径：通过  API 的缓存编辑功能直接删除旧内容6
if (feature('CACHED_MICROCOMPACT')) {7
return await cachedMicrocompactPath(messages, querySource)8

```
}
}
```

 第⼆层：⾃动压缩 ⸺ 主动收缩
  第三层：完全压缩 ⸺AI 总结

```
const NO_TOOLS_PREAMBLE = `CRITICAL: Respond with TEXT ONLY.
Do NOT call any tools.2
```

为什么要这么严厉？因为如果总结过程中  AI ⼜去调⽤⼯具，就会产⽣更多的  token 消耗，适得其反。这段提示词就是
在说：" 你的任务是总结，别⼲别的。 "
压缩后的  token 预算：
这些数字不是拍脑袋定的 ⸺ 它们是在 " 保留⾜够上下⽂继续⼯作 " 和 " 腾出⾜够空间接收新消息 " 之间的平衡点。
51 万⾏代码⾥，真正调⽤  LLM API 的部分可能不到  5% 。其余  95% 是什么？
如果你正在做  AI Agent 产品，这才是你真正要解决的问题。不是模型够不够聪明，是你的脚⼿架够不够结实。
不是写⼀段漂亮的  prompt 就完事了。Claude Code 的提示词是：
这是⼯程化的提示词管理，不是⼿⼯艺。
每⼀个外部依赖都有对应的失败策略：
- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.3
- Tool calls will be REJECTED and will waste your only turn.`4
⽂件恢复： 50,000 tokens
每个⽂件上限： 5,000 tokens
技能内容： 25,000 tokens
⼋、读完这份源码，我学到了什么
 AI Agent 的  90% ⼯作量在 "AI" 之外
安全检查（ 18 个⽂件只为⼀个  BashTool ）
权限系统（ allow/deny/ask/passthrough 四态决策）
上下⽂管理（三层压缩  + AI 记忆检索）
错误恢复（熔断器、指数退避、 Transcript 持久化）
多  Agent 协调（蜂群编排  + 邮箱通信）
UI 交互（ 140 个  React 组件  + IDE Bridge ）
性能优化（ prompt cache 稳定性  + 启动时并⾏预取）
  好的提示词⼯程是系统⼯程
7 层动态组装
每个⼯具附带独⽴的使⽤⼿册
缓存边界精确划分
内部版本和外部版本有不同的指令集
⼯具排序固定以保持缓存稳定
  为失败⽽设计

42 个⼯具  = 系统调⽤  权限系统  = ⽤户权限管理  技能系统  = 应⽤商店  MCP 协议  = 设备驱动  Agent 蜂群  = 进程管理  上
下⽂压缩  = 内存管理  Transcript 持久化  = ⽂件系统
这不是⼀个 " 聊天机器⼈加⼏个⼯具 " ，这是⼀个以  LLM 为内核的操作系统。
51 万⾏代码。 1903 个⽂件。 18 个安全⽂件只为⼀个  Bash ⼯具。
9 层审查只为让  AI 安全地帮你敲⼀⾏命令。
这就是  Anthropic 的答案：要让  AI 真正有⽤，你不能把它关在笼⼦⾥，也不能放它裸奔。你得给它建⼀套完整的信任
体系。
⽽这套信任体系的代价，是  51 万⾏代码。
为什么  Anthropic 选了最难的那条路？
因为只有这样， AI 才能⽤你的终端、你的环境、你的配置来⼲活 ⸺ 这才是 " 真正帮你写代码 " ，⽽不是 " 在⼀个⼲净房间
⾥给你写⼀段代码然后复制过来 " 。
但代价是什么？他们为此写了  51 万⾏代码。
⼤多数⼈以为  AI 编程⼯具是这样的：
plaintext
Claude Code 实际是这样的：
plaintext
  Anthropic 把  Claude Code 当操作系统在做
总结
⼆、你以为的  Claude Code vs 实际的  Claude Code
⽤户输⼊  → 调⽤  LLM API → 返回结果  → 显示给⽤户1
⽤户输⼊1
→ 动态组装  7 层系统提示词2
→ 注⼊  Git 状态、项⽬约定、历史记忆3
→ 42 个⼯具各⾃附带使⽤⼿册4
→ LLM 决定使⽤哪个⼯具5
→ 9 层安全审查（ AST 解析、 ML 分类器、沙箱检查 ... ）6
→ 权限竞争解析（本地键盘  / IDE / Hook / AI 分类器  同时竞争）7
→ 200ms 防误触延迟8
→ 执⾏⼯具9
→ 结果流式返回10
→ 上下⽂接近极限？ → 三层压缩（微压缩  → ⾃动压缩  → 完全压缩）11
→ 需要并⾏？ → ⽣成⼦  Agent 蜂群12

相信⼤家都很好奇上⾯的是什么，不着急，让我们逐个拆开看。
打开  src/constants/prompts.ts ，你会看到这个函数：
注意到那个  SYSTEM_PROMPT_DYNAMIC_BOUNDARY 了吗？
这是⼀个缓存分界线。分界线上⾯的内容是静态的， Claude API 可以缓存它们，节省  token 费⽤。分界线下⾯的内容
是动态的 ⸺ 你当前的  Git 分⽀、你的  CLAUDE.md 项⽬配置、你之前告诉它的偏好记忆 …… 每次对话都不⼀样。
这意味着什么？
Anthropic 把提示词当成了编译器的输出来优化。静态部分是 " 编译后的⼆进制 " ，动态部分是 " 运⾏时参数 " 。这样做的
好处是：
：静态部分⾛缓存，不重复计费
→ 循环直到任务完成13
三、第⼀个秘密：提示词不是写出来的，是 " 拼装 " 出来的
export async function getSystemPrompt(1

```yaml
tools: Tools,
model: string,
additionalWorkingDirectories?: string[],
mcpClients?: MCPServerConnection[],
): Promise<string[]> {
return [
```

// --- 静态内容（可缓存） ---8
getSimpleIntroSection(outputStyleConfig),9
getSimpleSystemSection(),10
getSimpleDoingTasksSection(),11
getActionsSection(),12
getUsingYourToolsSection(enabledTools),13
getSimpleToneAndStyleSection(),14
getOutputEfficiencySection(),15
// === 缓存边界  ===17
...(shouldUseGlobalCacheScope() ? [SYSTEM_PROMPT_DYNAMIC_BOUNDARY] : []),18
// --- 动态内容（每次不同） ---20
...resolvedDynamicSections,21

```
].filter(s => s !== null)
}
```

省钱1.

：缓存命中直接跳过这些  token 的处理
：动态部分让每次对话都能感知当前环境
更让我震惊的是：每个⼯具⽬录下都有⼀个  prompt.ts ⽂件 ⸺这是专⻔写给  LLM 看的使⽤⼿册。
看看  BashTool 的（ src/tools/BashTool/prompt.ts ，约  370 ⾏）：
plaintext
这不是写给⼈看的⽂档，这是写给  AI 看的⾏为准则。每次  Claude Code 启动时，这些规则都会被注⼊到系统提示词
中。
这就是为什么  Claude Code 从不会擅⾃  git push --force ，⽽某些⼯具会 ⸺不是模型更聪明，是提示词⾥已经把规矩
讲清楚了。
⽽且  Anthropic 内部版本和你⽤的不⼀样
typescript
ant 就是  Anthropic 内部员⼯。他们的版本有更详细的代码⻛格指引（ " 不写注释除⾮  WHY 不明显 " ）、更激进的输出
策略（ " 倒⾦字塔写作法 " ），以及⼀些仍在  A/B 测试的实验功能（ Verification Agent 、 Explore & Plan Agent ）。
这说明  Anthropic ⾃⼰就是  Claude Code 最⼤的⽤户。他们在⽤⾃⼰的产品来开发⾃⼰的产品。
打开  src/tools.ts ，会看到⼯具注册中⼼：
快
灵活
⛏ 每个⼯具都有独⽴的 " 使⽤⼿册 "
Git Safety Protocol:1
- NEVER update the git config2
- NEVER run destructive git commands (push --force, reset --hard, 3
checkout .) unless the user explicitly requests4
- NEVER skip hooks (--no-verify) unless the user explicitly requests5
- CRITICAL: Always create NEW commits rather than amending6
代码⾥⼤量出现这样的分⽀：

```yaml
const minimalUniquenessHint =
process.env.USER_TYPE === 'ant'
? '\n- Use the smallest old_string that\'s clearly unique'
: ''
```

四、第⼆个秘密： 42 个⼯具，但你只看到了冰⼭⼀⻆

typescript
42 个⼯具，但⼤部分你从未直接看到过。因为很多⼯具是延迟加载的 ⸺ 只有当  LLM 需要时，才通过  ToolSearchTool
按需注⼊。
为什么这样做呢？
因为每多⼀个⼯具，系统提示词就要多⼀段描述， token 就要多花⼀份钱。 如果你只是想让  Claude Code 帮你改⼀⾏
代码，它不需要加载 " 定时任务调度器 " 和 " 团队协作管理器 " 。
还有⼀个更聪明的设计：
typescript
设置  CLAUDE_CODE_SIMPLE=true ， Claude Code 就只剩三个⼯具： Bash 、读⽂件、改⽂件。这是给极简主义者的
后⻔。
typescript
export function getAllBaseTools(): Tools {1
return [2
AgentTool,3
BashTool,4
FileReadTool, FileEditTool, FileWriteTool,5
GlobTool, GrepTool,6
WebFetchTool, WebSearchTool,7
TodoWriteTool, NotebookEditTool,8
// ... ⼤量条件加载的⼯具  ...9
...(isToolSearchEnabledOptimistic() ? [ToolSearchTool] : []),10

```java
]
}
if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
const simpleTools: Tool[] = [BashTool, FileReadTool, FileEditTool]
return filterToolsByDenyRules(simpleTools, permissionContext)
}
```

 所有⼯具都从同⼀个⼯⼚出来

```yaml
const TOOL_DEFAULTS = {
isEnabled: () => true,
isConcurrencySafe: (_input?) => false,    // 默认：不安全
```

注意那些默认值： isConcurrencySafe 默认  false ， isReadOnly 默认  false 。
这叫  fail-closed 设计 ⸺ 如果⼀个⼯具的作者忘了声明安全属性，系统会假设它是 " 不安全的、会写⼊的 " 。 宁可过度
保守，也不漏掉⼀个⻛险。
typescript
FileEditTool 会检查你是否已经⽤  FileReadTool 读过这个⽂件。如果没有，直接报错，不让改。
这就是为什么  Claude Code 不会像某些⼯具那样 " 凭空写⼀段代码覆盖你的⽂件 "⸺ 它被强制要求先理解再修改。
⽤过  Claude Code 的⼈都有⼀个感受：它好像真的认识你。
你告诉它 " 不要在测试中  mock 数据库 " ，下次对话它就不会再  mock 。你告诉它 " 我是后端⼯程师， React 新⼿ " ，它解
释前端代码时就会⽤后端的类⽐。
这背后是⼀个完整的记忆系统。
typescript

```python
isReadOnly: (_input?) => false,            // 默认：会写⼊
isDestructive: (_input?) => false,
}
export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
return { ...TOOL_DEFAULTS, userFacingName: () => def.name, ...def }
}
```

  **" 先读后改 " 的铁律 **
function getPreReadInstruction(): string {1
return '\n- You must use your `Read` tool at least once in the 2
conversation before editing. This tool will error if you attempt 3
an edit without reading the file.'4
}5
五、第三个秘密：记忆系统 ⸺ 为什么它能 " 记住你 "
  ⽤  AI 来检索记忆

```
const SELECT_MEMORIES_SYSTEM_PROMPT =
`You are selecting memories that will be useful to Claude Code.2
Return a list of filenames for the memories that will clearly
be useful (up to 5).4
```

Claude Code ⽤  另⼀个  AI（ Claude Sonnet ）来决定 " 哪些记忆和当前对话相关 " 。
不是关键词匹配，不是向量搜索 ⸺ 是让⼀个⼩模型快速扫描所有记忆⽂件的标题和描述，选出最多  5 个最相关的，然
后把它们的完整内容注⼊到当前对话的上下⽂中。
策略是 " 精确度优先于召回率 " ⸺ 宁可漏掉⼀个可能有⽤的记忆，也不塞进⼀个不相关的记忆污染上下⽂。
这是最让我觉得科幻的部分。
代码中有⼀个叫  KAIROS 的特性标志。在这个模式下，⻓会话中的记忆不是存在结构化⽂件⾥，⽽是存在按⽇期的追加
式⽇志中。然后，有⼀个  /dream 技能会在 " 夜间 " （低活跃期）运⾏，把这些原始⽇志蒸馏成结构化的主题⽂件。
plaintext
AI 在 " 睡觉 " 的时候整理记忆。 这已经不是⼯程了，这是仿⽣学。
当你让  Claude Code 做⼀个复杂任务时，它可能悄悄做了这件事：
typescript
它⽣成了⼀个⼦  Agent。
- If you are unsure if a memory will be useful, do not include it.5
- If a list of recently-used tools is provided, do not select 6
memories that are usage reference for those tools. DO still 7

```sql
select memories containing warnings, gotchas, or known issues.`
```

⏰KAIROS 模式：夜间 " 做梦 "
logs/2026/03/2026-03-30.md  ←  今天的原始⽇志1
↓ /dream 蒸馏2
memory/user_preferences.md  ←  结构化的⽤户偏好⽂件3
memory/project_context.md   ←  结构化的项⽬背景⽂件4
六、第五个秘密：它不是⼀个  Agent ，是⼀群
// AgentTool 的输⼊  schema1
z.object({2

```yaml
description: z.string().describe('A short (3-5 word) description'),
prompt: z.string().describe('The task for the agent to perform'),
subagent_type: z.string().optional(),
model: z.enum(['sonnet', 'opus', 'haiku']).optional(),
run_in_background: z.boolean().optional(),
})
```

⽽且⼦  Agent 有严格的 " ⾃我意识 " 注⼊，防⽌它递归⽣成更多⼦  Agent ：
typescript
这段代码在说：" 你是⼀个⼯⼈，不是经理。别想着再雇⼈，⾃⼰⼲活。 "
👤 Coordinator 模式：经理模式
在协调器模式下， Claude Code 变成⼀个纯粹的任务编排者，⾃⼰不⼲活，只分配：
plaintext
核⼼原则写在代码注释⾥：
"Parallelism is your superpower" 只读研究任务：并⾏跑。  写⽂件任务：按⽂件分组串⾏跑（避免冲突）。
🗣 **Prompt Cache 的极致优化 **
为了最⼤化⼦  Agent 的缓存命中率，所有  fork ⼦代理的⼯具结果都使⽤相同的占位符⽂本：
plaintext
为什么？因为  Claude API 的  prompt cache 是基于字节级前缀匹配的。如果  10 个⼦  Agent 的前缀字节完全⼀致，那
么只有第⼀个需要 " 冷启动 " ，后⾯  9 个直接命中缓存。
export function buildChildMessage(directive: string): string {1
return `STOP. READ THIS FIRST.2
You are a forked worker process. You are NOT the main agent.4
RULES (non-negotiable):6
1. Your system prompt says "default to forking." IGNORE IT — 7
that's for the parent. You ARE the fork. 8
Do NOT spawn sub-agents; execute directly.9
2. Do NOT converse, ask questions, or suggest next steps10
3. USE your tools directly: Bash, Read, Write, etc.11
4. Keep your report under 500 words.12
5. Your response MUST begin with "Scope:". No preamble.`13
}14
Phase 1: Research    → 3 个  worker 并⾏搜索代码库1
Phase 2: Synthesis   → 主  Agent 综合理解所有发现2
Phase 3: Implementation → 2 个  worker 分别修改不同⽂件3
Phase 4: Verification   → 1 个  worker 跑测试4
'Fork started — processing in background'1

这是⼀个每次调⽤节省⼏美分的优化，但在⼤规模使⽤下，能省下⼤量成本。
所有  LLM 都有上下⽂窗⼝限制。对话越⻓，历史消息越多，最终⼀定会超出限制。
Claude Code 为此设计了三层压缩：
typescript
微压缩只动旧的⼯具调⽤结果 ⸺ 把 "10 分钟前读的那个 500 ⾏⽂件的内容 "替换成   Old tool result content
cleared 。
提示词和对话主线完全保留。
当  token 消耗接近上下⽂窗⼝的  87% （窗⼝⼤⼩  - 13,000 buffer ），⾃动触发。有⼀个熔断器：连续  3 次压缩失败后
停⽌尝试，避免死循环。
让  AI 对整段对话⽣成摘要，然后⽤摘要替换所有历史消息。⽣成摘要时有⼀个严厉的前置指令：
typescript
七、第六个秘密：三层压缩，让对话 " 永不超限 "
  第⼀层：微压缩 ⸺ 最⼩代价
export async function microcompactMessages(messages, toolUseContext,

```
querySource) {
```

// 时间触发：如果上次交互已过很久，服务器缓存已冷2

```java
const timeBasedResult = maybeTimeBasedMicrocompact(messages, querySource)
if (timeBasedResult) return timeBasedResult
```

// 缓存编辑路径：通过  API 的缓存编辑功能直接删除旧内容6
if (feature('CACHED_MICROCOMPACT')) {7
return await cachedMicrocompactPath(messages, querySource)8

```
}
}
```

 第⼆层：⾃动压缩 ⸺ 主动收缩
  第三层：完全压缩 ⸺AI 总结

```
const NO_TOOLS_PREAMBLE = `CRITICAL: Respond with TEXT ONLY.
Do NOT call any tools.2
- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.3
```

为什么要这么严厉？因为如果总结过程中  AI ⼜去调⽤⼯具，就会产⽣更多的  token 消耗，适得其反。这段提示词就是
在说：" 你的任务是总结，别⼲别的。 "
压缩后的  token 预算：
这些数字不是拍脑袋定的 ⸺ 它们是在 " 保留⾜够上下⽂继续⼯作 " 和 " 腾出⾜够空间接收新消息 " 之间的平衡点。
51 万⾏代码⾥，真正调⽤  LLM API 的部分可能不到  5% 。其余  95% 是什么？
如果你正在做  AI Agent 产品，这才是你真正要解决的问题。不是模型够不够聪明，是你的脚⼿架够不够结实。
不是写⼀段漂亮的  prompt 就完事了。Claude Code 的提示词是：
这是⼯程化的提示词管理，不是⼿⼯艺。
每⼀个外部依赖都有对应的失败策略：
- Tool calls will be REJECTED and will waste your only turn.`4
⽂件恢复： 50,000 tokens
每个⽂件上限： 5,000 tokens
技能内容： 25,000 tokens
⼋、读完这份源码，我学到了什么
 AI Agent 的  90% ⼯作量在 "AI" 之外
安全检查（ 18 个⽂件只为⼀个  BashTool ）
权限系统（ allow/deny/ask/passthrough 四态决策）
上下⽂管理（三层压缩  + AI 记忆检索）
错误恢复（熔断器、指数退避、 Transcript 持久化）
多  Agent 协调（蜂群编排  + 邮箱通信）
UI 交互（ 140 个  React 组件  + IDE Bridge ）
性能优化（ prompt cache 稳定性  + 启动时并⾏预取）
  好的提示词⼯程是系统⼯程
7 层动态组装
每个⼯具附带独⽴的使⽤⼿册
缓存边界精确划分
内部版本和外部版本有不同的指令集
⼯具排序固定以保持缓存稳定
  为失败⽽设计

42 个⼯具  = 系统调⽤  权限系统  = ⽤户权限管理  技能系统  = 应⽤商店  MCP 协议  = 设备驱动  Agent 蜂群  = 进程管理  上
下⽂压缩  = 内存管理  Transcript 持久化  = ⽂件系统
这不是⼀个 " 聊天机器⼈加⼏个⼯具 " ，这是⼀个以  LLM 为内核的操作系统。
51 万⾏代码。 1903 个⽂件。 18 个安全⽂件只为⼀个  Bash ⼯具。
9 层审查只为让  AI 安全地帮你敲⼀⾏命令。
这就是  Anthropic 的答案：要让  AI 真正有⽤，你不能把它关在笼⼦⾥，也不能放它裸奔。你得给它建⼀套完整的信任
体系。
⽽这套信任体系的代价，是  51 万⾏代码。
  Anthropic 把  Claude Code 当操作系统在做
总结
