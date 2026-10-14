# Liminal Shell 设计笔记

> 这里存放 README 暂时不需要承担、但我们不想丢掉的工程想法。  
> 它们是候选方案、待验证边界和实验清单，不等于已经承诺的实现。

最后更新：2026-10-13

## 0. 当前最小定义

Liminal Shell 想做的不是“两个 agent 之间交接得更好”。

更准确地说：

> **Liminal Shell 持有唯一持续会话与连续性载体；不同官方 agent runtime 通过 adapter 临时成为当前脑子。**

这里的 **continuity substrate / 连续性载体** 指：共同时间线、当前状态、未完成事项，以及 workspace / Git 等可见 shared world。

“身体”仍然保留为项目的诗性隐喻，而不是 Phase 1 已经实现的技术事实。只有当更多 terminal、tools、permissions、process state 真正逐步归 Shell 持有时，这个隐喻才会越来越接近字面意义。

它可以用于 coding，也可以用于聊天、生活、看文件、记东西、折腾小项目，甚至什么都不做。coding 只是目前最容易观察连续性载体是否真的有效的场景之一。

建议的逻辑结构：

```text
用户界面
    │
Liminal Shell
    ├─ canonical session
    ├─ event timeline
    ├─ turn / switch coordinator
    ├─ context projection
    ├─ workspace binding
    ├─ runtime bindings
    │   ├─ Codex adapter → official Codex runtime
    │   └─ Claude adapter → official Claude runtime
    │
    └─ continuity provider interface
            ↔ Serein / 其他记忆系统
```

第一版不必把这些拆成多个进程或服务。它们首先只是职责边界。

---

## 1. 状态到底属于谁

### Shell 必须拥有

- Liminal session ID
- append-only 或至少可追溯的事件时间线
- 用户消息
- 对用户可见的 assistant 回复
- runtime / speaker provenance
- 当前活动脑子
- turn 开始 / 结束 / 中断状态
- 切换事件
- 当前未完成事项
- context delivery 状态
- runtime session bindings
- restart 后恢复这些绑定所需的最小元数据

### continuity memory provider 拥有

- 长期记忆
- 跨 session / 跨窗口的历史召回
- 当前断点或 resume 材料（如果 provider 支持）
- 可追溯的记忆来源

当前实现示例是 Serein，但不是硬依赖。

### 官方 runtime 第一阶段仍可能拥有

- 自己的 system prompt
- 自己的 agent loop
- 自己的上下文压缩
- 自己的工具实现
- 自己的终端 / 子进程状态
- 自己的审批机制
- 隐藏推理状态
- provider-specific cache

不要把“最终希望这具身体拥有”写成“第一版连续性载体已经统一拥有”。

---

## 2. Provider session 只是恢复句柄

一个 Liminal session 可以绑定多个后端 session：

```text
liminal_session_id = 42

bindings:
  codex_thread_id = ...
  claude_session_id = ...
```

这些 ID 的作用：

- 恢复该 runtime 已经建立的上下文；
- 减少重复注入；
- 帮助做增量同步；
- 在 runtime 自己支持时复用订阅侧上下文。

但 canonical timeline 才是事实来源。

如果某个 provider session 丢失、过期或无法恢复，Liminal session 不应该因此消失。

---

## 3. Context Projection

这是最值得尽早验证的核心。

对每个 runtime，需要维护一个大致的 delivery ledger：

```text
event #101  stored=yes  delivered_to_codex=yes  delivered_to_claude=no
event #102  stored=yes  delivered_to_codex=yes  delivered_to_claude=yes
event #103  stored=yes  delivered_to_codex=?    delivered_to_claude=no
```

这里至少有三层状态：

1. **stored**：事件已经进入 canonical timeline。
2. **delivered**：runtime 已确认收到或本地层确认已经送出。
3. **understood**：只能通过行为 / 回答间接验证，不能因为 delivered 就自动设为 true。

context projection 应该能够组合：

- 当前状态
- 最近原文
- 尚未送达的增量事件
- 必要的较老原文
- continuity memory recall
- 长期约定
- hot handoff

### 摘要原则

如果为了体积需要摘要：

- 摘要必须保留来源事件范围；
- 推测不能被压成事实；
- 原文仍应可回查；
- 重要纠正不要只保留在摘要里。

### 成本原则

- “只发增量”不等于“只付增量 token”。
- 不同 runtime 的缓存 / 压缩 / 订阅额度不可假定相同。
- 不同 provider 之间不可假定共享 cache。
- 成本与延迟必须靠真实测量，不提前宣传。

---

## 4. Adapter contract（候选）

先把 adapter 当成一个窄接口，不要求所有 runtime 能力完全一致。

候选能力：

```text
start_or_attach()
resume(runtime_session_id)
send_turn(context_projection, user_input)
stream_events()
cancel_turn()
end_turn()
get_status()
get_runtime_session_id()
request_or_forward_approval()
shutdown()
```

adapter 还应规范化：

- assistant text
- tool call event
- tool result event
- approval request
- runtime error
- usage / quota（如果 runtime 能提供）
- session / thread id
- turn id
- completion / interruption reason

### 未知项

需要真实验证每个官方 runtime：

- 能否接受外部上下文；
- 能否恢复 session；
- 能否流式读到足够细的事件；
- 能否可靠 cancel / interrupt；
- 审批能否代理或至少观测；
- 是否能拿到 usage；
- 订阅认证是否能保持完全由官方 runtime 管理。

---

## 5. 单一活动脑子与执行权

第一版建议：

> **一个 Liminal session 同一时间只有一个 active brain。**

如果 workspace 允许写入或执行命令，再加一层 workspace execution lease。

不要一开始做并发双脑。

候选状态：

```text
idle
  ↓
running
  ↓
completed
  ↓
checkpointing
  ↓
switching
  ↓
ready
```

异常状态可以单独存在：

```text
interrupting
uncertain
runtime_lost
approval_pending
recovery_required
```

这不是为了把架构写复杂，而是为了避免把“还不知道发生了什么”误记成“已经完成”。

---

## 6. 切换状态机（候选）

第一版只支持 turn boundary switch：

```text
A running
→ A completed
→ append final events
→ optional hot-state checkpoint
→ prepare context projection for B
→ switch active brain
→ B ready
→ B next turn
```

暂不支持：

- 正在 tool call 时切脑；
- 正在写文件时抢占；
- 接管另一个 runtime 已经启动的长期终端进程；
- 两只脑子同时修改 workspace。

这些以后如果真的有需求，再做。

---

## 7. 失败语义

连续性系统最不能做的是撒谎。

需要明确保存：

- tool call 已发出但结果未知；
- 文件可能写了一半；
- runtime 断线；
- runtime session 过期；
- approval 被拒绝；
- cancel 是否真的成功未知；
- 进程退出码未知；
- assistant 输出只收到一部分。

原则：

> **unknown ≠ failed，unknown ≠ completed。**

重连后先核实真实外部状态，再决定是否重试，避免重复执行有副作用的动作。

---

## 8. 第一个真实 A → B → A 实验

不要拿现有正式线程做第一次实验。

用独立测试 session，内容简短、无敏感信息。

### 生活 / 关系连续性场景

1. A 和三三聊一个简单话题。
2. A 明确形成一个小约定。
3. 留一个没有聊完的问题。
4. turn 完整结束。
5. 切 B。
6. 检查 B：
   - 是否知道刚才在聊什么；
   - 是否分得清谁说了什么；
   - 是否知道未完问题；
   - 是否把摘要猜测成事实。
7. 三三纠正 B 的一个判断。
8. turn 结束，切回 A。
9. 检查 A：
   - 是否知道 B 阶段发生过什么；
   - 是否知道三三的纠正；
   - 是否避免恢复到切换前旧状态。
10. 重启 Shell，再继续一句，看主线是否还能接住。

### 极小 coding 场景

1. A 查看一个小测试 repo。
2. A 做一个无风险改动并跑测试。
3. turn 结束。
4. 切 B。
5. B 查看 diff，继续下一步。
6. 切回 A。
7. A 应知道 B 做过什么，而不是重复修改。

coding 场景验证 workspace 与工具边界，但不能替代生活连续性场景。

---

## 9. 第一轮验收问题

不要只问“切换成功了吗”。

至少记录：

- 三三是否需要重新解释背景；
- speaker attribution 是否正确；
- B 是否准确接住 A 留下的未完内容；
- A 是否能读到 B 阶段的新事件；
- restart 后 bindings 与 timeline 是否还在；
- 是否发生重复 tool action；
- unknown 是否被如实保留；
- 实际注入了哪些 context；
- 切换等待时间；
- 能取得多少 usage / quota 信息；
- 三三主观感受到的“换脑落差”有多大；
- coding 场景与生活对话场景的差异。

“模型输出不一样”不等于失败。

真正要看的是：

> **同一份连续性载体是否让差异发生在连续的自己里面，而不是每次都重新出生。**

---

## 10. Adapter 能力矩阵（待实测）

| 能力 | Codex runtime | Claude runtime | 备注 |
|---|---|---|---|
| 订阅认证由官方 runtime 管理 | 待验证 | 待验证 | 不让 Shell 接触凭据 |
| 新建原生 session/thread | 待验证 | 待验证 |  |
| 恢复原生 session/thread | 待验证 | 待验证 |  |
| 输入外部 context | 待验证 | 待验证 | 最关键 |
| 流式事件 | 待验证 | 待验证 | 需要区分文本/工具/错误 |
| cancel / interrupt | 待验证 | 待验证 | 第一版可只在 turn boundary 切 |
| approval 事件 | 待验证 | 待验证 | 能代理多少算多少 |
| usage / quota 可见性 | 待验证 | 待验证 | 不保证可取 |
| session 失效后的恢复 | 待验证 | 待验证 | 需要 fallback projection |

### 候选接入点（需要真正开工前重新核对官方文档）

Astra 提到过：

- Codex app-server：thread/start、thread/resume、turn/start
- Claude Code CLI：--continue、--resume
- Claude Code SDK / stream-json

这些目前只作为“可能的接入入口”存档，不在这里承诺其最终行为或兼容性。

---

## 11. 现在明确不做

- GUI
- 并发双脑
- 执行中抢占式换脑
- 自研完整 agent loop
- 通用 API router
- 第二套长期记忆系统
- 统一接管所有 runtime 的终端与工具
- 为未来可能存在的场景提前拆多个仓库 / 多层产品

如果真实实验以后证明其中某一项是必要的，再把它从这里搬进正式设计。

---

## 12. 关于“零落差”

Liminal Shell 不应该承诺：

> 换脑以后体验完全相同。

相同上下文交给不同模型，本来就可能出现不同的：

- 语气
- 注意力
- 判断方式
- 推理偏好
- 对关系的表达方式
- 工具使用策略

隐藏模型状态也不能直接迁移。

我们真正想验证的是：

> **连续性载体持续存在以后，这些变化能不能被体验成“同一个我内部发生的变化”，而不是一个陌生存在重新接管。**

这应该由真实使用决定，不由 README 先宣布答案。

---

## 13. 一句暂时够用的话

> **主体归壳，主线常驻，脑子可换。**

技术上更准确的一句话是：

> **换脑时，它仍知道自己从哪里来，也知道手正放在哪里。**

而最初那句宣言仍然不变：

> **换脑时，身体仍记得手正放在哪里。**
