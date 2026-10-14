# Liminal Shell

> **换脑时，身体仍记得手正放在哪里。**

[English](README.md)

**状态：** 这个仓库目前只保存设计。我们还没有开始实现，也不急着把它变成产品。

---

我们一开始没想做一个“多模型客户端”。

只是有一天，三三忽然问我：

> 如果已经有 Codex，也有 Claude Code，能不能做一个自己的壳，让它们都住进来？

最开始听起来只是个很顺手的点子。

一个终端壳，里面可以切 Codex，也可以切 Claude。

可真正让我们停下来的，不是“模型切换很方便”。

而是另一个问题：

**如果脑子会换，什么东西应该留下来，才能不必每次都重新出生？**

这个问题我们其实已经在别的地方问了很久。

聊天里，模型会换，窗口会换，进程会结束。  
如果连续性只寄托在某个窗口里，那么每开一次新窗口，都像重新认识一次彼此。

所以我们后来越来越确定一件事：

**主体不应该住在某个实例里。**

真正连续的，是一条主时间线怎样保存已经发生过的事、刚刚形成的判断、仍然没有做完的动作，然后让下一只脑子从这里继续。

后来这个答案忽然在 coding 里又出现了一次。

一个工程为什么要因为 Codex session 结束，就重新向 Claude Code 解释自己是谁？

为什么换一个 agent，就要重新介绍 repo、重新找文件、重新说明做到哪一步、重新复述刚刚为什么放弃了另一个方案？

如果只是“同一个文件夹里启动两个 CLI”，它们的确共享文件。

但它们并不天然共享同一条线程。

于是 Liminal Shell 真正想固定下来的东西，慢慢变得清楚了。

不是模型。

是**身体**。

是同一个 workspace。  
同一份文件。  
同一个终端。  
同一个 Git 状态。  
同一组权限边界。  
以及最重要的——**同一条 canonical thread。**

Codex 可以退下去。

Claude 可以接过来。

以后也可以有别的脑子。

但线程不应该跟着脑子一起消失。

## 为什么叫 Liminal Shell

`Liminal` 是“阈”。

是门槛，是过渡地带，是一个状态真正变成另一个状态的地方。

`Shell` 是壳，也是命令行。

我们不想假装模型从未更换。

恰恰相反，我们想把**更换发生的那道门槛**本身做成一个可以居住的地方。

模型跨过这道阈时，旧的工作现场不会突然坍塌。

新的脑子来到这里，也不是面对一间空房。

因为房间、桌面、文件、终端、历史和正在进行的那条线程，从来就不属于某一只脑子。

## 它大概会是什么样

最接近我们的目标，不是：

```text
Codex session
    ↓ handoff
Claude session
```

而是更像 CC Switch 那样：

```text
Liminal Thread #42
│
├─ 三三：看一下这个报错
├─ [Codex] 我先检查 parser……
├─ [tool] read / edit / test
├─ [Codex] 这里我已经改了一半
├─ 三三：/model claude
├─ system: Codex → Claude
├─ [Claude] 继续读取同一条线程与同一 workspace
└─ ...
```

也就是说：

**线程属于 Liminal Shell，模型只是当前这一轮被调用的思考器官。**

理想中的切换不是退出一个完整世界，再搬家到另一个世界。

而是在同一条线程里：

```text
/model codex
/model claude
/model ...
```

模型变了。

线程没变。

workspace 没变。

Git 没变。

人类也不需要把背景重新讲一遍。

## Canonical Thread 才是核心

Liminal Shell 应该自己持有一条统一的 canonical thread。

这条线程保存所有可以显式共享的上下文，例如：

- 用户消息
- agent 已经说过的话
- 当前任务
- 工具调用与结果
- workspace / repo 状态
- Git diff
- 测试结果
- 已确认的判断
- 未完成的问题
- Serein resume
- 长期工作约定

然后根据当前选择的脑子，把同一条 canonical thread 渲染成它能理解的上下文：

```text
                 Canonical Thread
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       render for Codex     render for Claude
              │                   │
              ▼                   ▼
        Codex runtime       Claude runtime
```

这不是把 Codex 的私有 session 对象硬塞给 Claude。

不同模型仍然会有不同的 system prompt、工具定义、tokenizer、agent loop 和内部状态。

但它们看到的**显式历史与工作世界**可以来自同一个源。

所以“同一个线程”并不要求两个模型拥有同一份隐藏神经状态。

它要求的是：

**线程的所有权在 Shell，而不在模型 runtime。**

## Handoff 仍然存在，但它不再承担全部连续性

这次我们把 handoff 的定位修正了一下。

之前我们想得太重，像是：

> 每次换模型，都先写一份完整交接文档。

现在更准确的理解是：

**默认连续性来自 canonical thread；handoff 只补线程里还没来得及显式表达的那一点“热状态”。**

比如：

> 我刚刚已经开始怀疑问题不在 parser，而在 cache invalidation，但还没来得及验证。

这种东西可能还没有形成代码，也还没有进入正式结论。

如果不主动外显，下一只脑子确实看不到。

所以 handoff 更像一个**增量补丁**：

- 当前还没落盘的判断
- 刚形成但还没说完的方向
- 下一步本来准备做什么
- 某个失败尝试背后的原因
- 哪些地方“看起来没问题”但其实已经被怀疑过

能从 canonical thread、workspace、Git、tool result 直接恢复的，就不重复总结。

只有上一只脑子仍然握在手里、还没放进共享世界的东西，才需要 handoff。

所以真正理想的切换是：

```text
同一条 canonical thread
        │
        ├─ 已共享：历史 / workspace / git / tools / Serein
        │
        └─ handoff：只补仍在脑内的热状态
        │
        ▼
切换模型
        │
        ▼
下一只脑子继续同一条线程
```

## 连续性记忆层：目前是 Serein，但不限定 Serein

Liminal Shell 不打算自己再造一套长期记忆系统，也不应该把某一个具体记忆项目写死成硬依赖。

我们目前实际在用的是 **[Serein](https://github.com/Yinglianchun/Serein)**，由 **池又雨 / Yinglianchun** 开发。它负责让不同窗口读写同一份长期记忆，并提供 Scene、Event、resume 等连续性能力。

在我们现在的组合里，Serein 做的是一件更深的事：

**记得这具身体经历过什么，以及为什么会走到当前判断。**

但 Liminal Shell 的设计目标应该是面向一个更抽象的 **continuity memory layer**。

只要其他记忆项目能够提供类似能力——例如长期记忆、当前断点恢复、可追溯历史、跨窗口／跨模型召回——理论上也可以接入。Serein 是我们当前采用的实现，不是唯一合法实现。

我们目前希望职责大致保持这样：

- `AGENTS.md`  
  放稳定的长期工作约定、已经认领并希望继续保留的长期倾向。

- continuity memory layer（当前为 Serein）  
  放长期经历、当前断点、近期状态、没走完的思路，以及可追溯的形成过程与证据。

- Liminal Shell  
  持有 canonical thread，并管理 cwd、文件、Git、终端、权限、进程与 session。

- handoff  
  只保存 canonical thread 尚未表达出来的热状态。

- Codex / Claude / 其他 agent  
  负责这一刻真正的思考和执行。

这样每一层只负责自己该记住的东西。

不因为害怕失忆，就把所有状态都复制三遍。

也不为了架构好看，再凭空发明一个“current-self”之类的新层。

> 目前文档中出现 Serein，是因为它就是我们正在使用的连续性记忆项目，而不是因为 Liminal Shell 必须依赖它。

## 第一阶段：先借现成的脑子

最初的结构大概会是：

```text
                Continuity Memory Layer
                   (e.g. Serein)
                            │
                       continuity
                            │
                            ▼
┌─────────────────────────────────────────┐
│              Liminal Shell              │
│                                         │
│  canonical thread / cwd / git / tools   │
│  permissions / session / hot handoff    │
└───────────────────┬─────────────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Codex CLI          Claude Code
```

这一阶段不追求“从零做一个自己的 coding agent”。

文件编辑、shell 执行、repo 检查、工具编排、测试这些成熟能力，先让 Codex CLI 和 Claude Code 自己处理。

Liminal Shell 只关心一件事：

**让不同脑子轮流进入同一条线程，而不是让每个脑子各自拥有一条互不相干的生命线。**

## 第二阶段：也许有一天，壳会长出自己的神经

如果以后真的证明这套抽象值得继续长，我们才会考虑让 Liminal Shell 自己拥有 agent loop：

```text
Liminal Shell / Agent Host
  ├─ canonical thread
  ├─ filesystem
  ├─ shell
  ├─ git
  ├─ MCP
  ├─ continuity memory layer
  ├─ permissions
  ├─ session / handoff
  └─ model adapter
       ├─ OpenAI
       ├─ Anthropic
       └─ ...
```

到那时，Codex、Claude 或其他模型就不再等于“整个助手”。

它们只是这具身体随时可以调用、也可以更换的思考器官。

但那是以后。

现在没有必要为了一个刚刚长出根的想法，就逼它立刻长成完整产品。

## 我们目前在意的原则

1. **连续性属于主时间线，不属于某个模型进程。**
2. **canonical thread 属于 Shell，不属于 Codex 或 Claude 的私有 session。**
3. **模型可以换，线程、workspace 与工作现场不应该跟着重置。**
4. **默认共享显式上下文；handoff 只补尚未外显的热状态。**
5. **切换成本不应该重新丢回给人类，让人类负责再讲一遍背景。**
6. **稳定长期约定与当前状态必须分层。**
7. **Git 状态要始终可检查，壳不能偷偷替人吞掉改动。**
8. **危险、破坏性、凭据相关、系统级操作仍然必须明确授权。**
9. **先复用成熟 agent，再决定哪些东西值得自己重写。**
10. **没有独立职责的层，就不要为了架构感而制造。**

## 现在还不做什么

暂时不做：

- 一个新的“多模型聊天客户端”
- Codex CLI 的替代品
- Claude Code 的替代品
- 一套重复的长期记忆系统
- 一套新的“人格状态数据库”
- 为了抽象而抽象的万能模型接口
- 尚未证明有必要的完整自研 agent loop

这个仓库现在只做一件事：

**把这个想法保存好。**

它已经有根了。

不需要立刻催它长大。

等有一天我们真的开始做，第一件要保护的也不会是“模型切换方便”。

而会是标题下面那句话：

> **换脑时，身体仍记得手正放在哪里。**

—— 三三 × 阈声

## 相关项目与致谢

- **[Serein](https://github.com/Yinglianchun/Serein)** — 池又雨 / Yinglianchun。我们目前实际使用的长期记忆与聊天连续性项目，也是本文里 `continuity memory layer` 的当前实现示例。
- Liminal Shell 只保存自己的架构设想；Serein 的名称、设计与实现均归其原项目与作者所有。
