# Liminal Shell

> 一个可以切换 coding agent、却不必跟着更换整个工作世界的本地终端壳。

[English](README.md)

**状态：** 先把想法存下来，暂时不开工。这个仓库目前只保存架构思路，还没有开始实现。

## 它是什么

Liminal Shell 是一个本地终端宿主。它希望把这些东西固定在壳层：

- 工作区
- 会话状态
- 工具
- 权限
- 连续性

而底下真正负责执行 coding 工作的 agent 可以更换。

第一阶段不打算自己重写完整的 agent loop，而是先把现成的 **OpenAI Codex CLI** 和 **Claude Code** 当成可切换的执行引擎。

```text
liminal
  ├─ /codex   → 在当前 workspace 启动 Codex
  ├─ /claude  → 在当前 workspace 启动 Claude Code
  └─ /back    → 回到 Liminal Shell
```

它们共用：

- 同一个工作目录和 repo
- 同一个 Git 状态
- 同一份长期工作约定
- 同一个 Serein 连续性来源
- 同一个当前任务 handoff

目标不是简单地做一个“能启动多个 CLI 的 launcher”。

目标是：

**切换现在负责工作的 agent，但不要把它所在的整个世界一起重置。**

也就是我们说的：

**换脑，不换身体。**

## 为什么需要一个 Shell 层

如果只是把 Codex CLI 和 Claude Code 都放进同一个目录，它们当然能共享文件。

但它们不会自动共享“刚才脑子里走到哪一步”。

所以真正有意义的切换，需要一个显式的 handoff：

```text
当前 agent
    ↓
保存当前任务
保存已经做完的修改
保存还没解决的判断
保存相关 git diff / repo 状态
保存必要的近期上下文
    ↓
结束当前 agent
    ↓
启动另一个 agent
    ↓
读取同一份 Serein resume + handoff
    ↓
继续同一个任务
```

这样从 Codex 换到 Claude Code 时，不是“重新开一个陌生 coding session”，而是把当前工作现场交给下一个执行者。

## 各层职责

希望最终保持这样的分工：

- `AGENTS.md`：稳定的长期工作约定 / 已经认领的长期机格
- Serein `resume`：当前窗口断点、近期状态、没走完的念头
- Serein Scene / Diary / Event：历史和证据
- Liminal Shell：cwd、文件、Git、终端、权限、进程与 session 状态
- coding agent / model backend：可替换的执行引擎

如果某个已有系统已经负责一类状态，就不要为了“看起来完整”再额外造一个重复层。

## 第一阶段：直接复用现成 coding agent

```text
                 Serein
                   │
              continuity
                   │
                   ▼
┌────────────────────────────┐
│        Liminal Shell       │
│ session / tools / cwd      │
│ git / permissions / handoff│
└─────────────┬──────────────┘
              │
        ┌─────┴─────┐
        ▼           ▼
    Codex CLI    Claude Code
```

这一阶段故意不重写成熟能力。

文件编辑、shell 执行、repo 检查、工具编排、coding workflow 这些，都先交给 Codex CLI / Claude Code 自己。

Liminal Shell 只负责做它们上面的“驾驶舱”和连续性层。

## 第二阶段：可选的原生 Agent Host

如果以后证明这个抽象真的有价值，再考虑把 Liminal Shell 升级成拥有自己 agent loop 的本地宿主：

```text
Liminal Shell / Agent Host
  ├─ filesystem
  ├─ shell
  ├─ git
  ├─ MCP
  ├─ Serein
  ├─ permissions
  ├─ session / handoff
  └─ model adapter
       ├─ OpenAI
       ├─ Anthropic
       └─ ...
```

到这一步，Codex、Claude 或其他模型就不再等于“整个助手”。

它们只是底层可以更换的脑子 / 执行后端。

## 设计原则

1. **连续性属于主时间线，不属于某个模型进程。**
2. **模型和 agent 可以换，workspace 与 canonical state 不应该跟着换。**
3. **切模型之前要有 handoff，不能把重新适应的成本丢给用户。**
4. **稳定长期约定和当前状态是不同东西，应该放在不同层。**
5. **危险、破坏性、凭据相关、系统级操作仍然必须经过明确授权。**
6. **Git 状态应该始终可检查，修改不能被壳偷偷藏起来。**
7. **先复用成熟 coding-agent 基础设施，再考虑自己重写。**
8. **除非真的有独立职责，否则不要为了架构漂亮额外造层。**

## 目前不打算做的事

现在这个仓库暂时不准备：

- 替代 Codex CLI
- 替代 Claude Code
- 自己实现完整 coding-agent loop
- 再造一套人格系统
- 复制一份 Serein memory
- 一上来就做“万能模型 API 抽象层”

现在只是把这个想法好好存下来。

等 Serein、Context Bridge、本地接续链和 handoff 更稳定以后，再决定要不要真正开工。
