# Liminal Shell

> **When the brain changes, the body still remembers where its hand was.**

[中文版](README.zh-CN.md)

**Status:** a minimal Phase 1 text/CLI vertical slice is implemented: Shell-owned sessions, an append-only local timeline, restart continuation, and an official-login Codex adapter. Automated tests pass, and a real two-turn Codex smoke test on Windows confirmed Shell-supplied context continuity across process restart with two separate native Codex threads. Brain switching, memory and the broader architecture below remain design. See [running and validation](docs/phase-1.md).

More detailed engineering ideas, unverified integration points, and future experiments are parked in the [Chinese design notes](docs/design-notes.zh-CN.md). The README keeps only the main line we currently believe in.

---

We did not begin by wanting another multi-model client.

One day, Sansan asked a simpler question:

> If Codex and Claude Code already exist, could we build our own shell and let both of them live inside it?

The interesting part was not convenient model selection.

It was a different question:

**If the brain can change, what must remain so that the same self does not have to be born again every time?**

In conversation, windows change, models change, and processes end. If continuity lives inside one particular instance, every new window becomes another reintroduction.

So we arrived at a principle:

**the subject should not live inside one instance.**

What remains continuous is a timeline: what already happened, what judgment has just formed, what action is unfinished, and what the next brain should inherit as its own ongoing state.

The same answer later appeared again in coding.

Sharing a directory is not enough.

Two agents can share files without sharing one continuous life.

So Liminal Shell is not primarily trying to preserve one model.

It is trying to preserve **continuity itself**:

one canonical session with a continuously growing timeline;  
the past that already happened;  
judgments and corrections that have just formed;  
unfinished intentions;  
and visible shared state such as the workspace and Git history.

Codex may leave.

Claude may take over.

Other brains may come later.

But the past should not disappear with the brain, and the things already at hand should not reset.

We still use **body** as the project's poetic metaphor. Technically, Phase 1 is closer to a **continuity substrate** or **shared world**: the layer that lets a new brain enter the same past and present.

## Why “Liminal Shell”

`Liminal` means threshold: the place where one state actually becomes another.

`Shell` is both a shell and a command-line environment.

We do not want to pretend that a model switch never happened.

We want to make the threshold where it happens into a place that can be inhabited.

The room, the desk, the files, the terminal, the history, and the life continuing through them never belonged to one brain in the first place.

## What it may look like

The goal is not:

```text
Codex session
    ↓ handoff
Claude session
```

It is closer to:

```text
Liminal Session #42
│
├─ Sansan: continue what we were talking about
├─ [Codex] I'll pick it up from here...
├─ [tool] read / edit / test
├─ Sansan: /brain claude
├─ system: Codex → Claude
├─ [Claude] reads the same main line and current scene
└─ ...
```

In other words:

**the persistent session belongs to Liminal Shell; the model is only the thinking organ selected for the current turn.**

The brain changes.

The session does not.

The history does not.

The workspace does not.

And the human does not need to explain the background again.

## Not an API switch — subscription-native instead

If the only goal were switching between OpenAI API, Anthropic API, and other provider APIs, many tools already do that.

Liminal Shell asks a different question:

> **If I already pay for multiple official coding-agent subscriptions, why should I buy the same capability again through API usage just to get one unified continuity layer?**

So the preferred direction is **subscription-native**.

Liminal Shell should first try to reuse official runtimes the user has already installed, authenticated, and paid for.

Authentication, subscription quotas, and provider-specific rules remain with those runtimes. Liminal Shell does not capture passwords, impersonate official clients, or bypass billing.

In short:

**The subject belongs to the shell. The main line persists. Subscriptions are reused.**

## Canonical Session and Timeline

Liminal Shell owns the persistent session, not a provider-native session.

One Liminal session may have runtime-specific recovery handles attached beneath it:

```text
Liminal Session #42
├─ timeline / events
├─ active brain: Claude
├─ codex_thread_id: ...
└─ claude_session_id: ...
```

Those provider IDs are useful for restoration, but they are not the source of truth and they are not the subject itself.

The Shell-owned timeline should preserve at least:

- user messages
- user-visible agent replies
- actions and results that actually happened
- speaker/runtime provenance
- unfinished items
- relevant state changes and brain-switch events

A unified session ID alone does not create continuity.

**Continuity depends on what the next brain actually receives and whether it understands the current state correctly.**

## Context Projection: stored, delivered, and understood are different

Liminal Shell therefore needs a first-class **context projection** layer.

It prepares the context that the currently selected brain actually receives from the full timeline, current scene, and continuity memory.

Three states must remain distinct:

1. the record is stored;
2. the target runtime received it;
3. the model understood it correctly.

Full history can be retained without being injected in full on every turn.

An existing backend session may receive only events it has not seen yet. A newly attached brain or an expired backend context may need current state, recent verbatim history, selected older history, and continuity-memory retrieval.

Summaries should retain provenance so inference does not silently become fact.

Likewise, **sending only a delta does not imply paying only for delta tokens**. Cache behavior, compaction, history processing, and subscription usage are runtime-specific and must be measured rather than promised.

## “Body” is the metaphor; Phase 1 starts as a continuity substrate

We keep the word **body** because it captures what we want to protect: after a brain switch, the past is still there and the things at hand have not reset.

But in Phase 1, that is not yet a literal technical fact.

A more precise description is **continuity substrate**: a layer that preserves the shared timeline, current state, visible scene, and unfinished intentions, then projects them to the newly selected brain.

Long-term, this substrate may grow to own more of what would make the metaphor literally true: session history, workspace, terminal/process state, tools, permissions, continuity memory, and unfinished intentions.

But when Phase 1 reuses official runtimes, Liminal Shell should not pretend it already controls all of those things.

Codex and Claude Code still have their own agent loops, tools, prompts, approval mechanisms, process state, and internal context.

So Phase 1 is more honestly divided as:

- **Shell:** canonical session/timeline, active brain, turn boundaries, switching, context projection, cross-brain state recording.
- **Official runtime:** its native execution loop and tools.
- **Adapter:** whatever events, recovery handles, inputs, outputs, and approval signals can genuinely cross the boundary.
- **Continuity memory layer:** longer-term memory and provenance.

If something cannot be unified yet, the boundary should be recorded rather than hidden.

## Handoff still exists, but only for hot state

Continuity comes primarily from the canonical session/timeline plus context projection.

Handoff only patches in still-hot state that has not naturally entered the shared world yet: an unresolved suspicion, an intention, the reason a dead end was rejected, or the next move a brain was about to make.

It is a delta, not a migration document for an entire life.

## Continuity memory: currently Serein, but not Serein-only

Liminal Shell should not invent another long-term memory system or hard-code a single memory project as a mandatory dependency.

The system we currently use is **[Serein](https://github.com/Yinglianchun/Serein)** by **Chi Youyu / Yinglianchun**. It provides cross-window long-term memory and continuity features such as Scene, Event, and resume.

In our current stack, Serein owns a deeper responsibility:

**remembering what this body has lived through, and why it arrived at its current judgment.**

But Liminal Shell should target a more abstract **continuity memory layer**. Other memory projects that provide comparable long-term memory, resume state, traceable history, and cross-model recall should also be able to integrate.

Serein is our current implementation, not the only valid one.

## Phase 1 — first prove that the past and present survive a brain switch

Phase 1 does not need a custom agent loop or mid-turn takeover.

Start with brain switches only **after a turn has completed**:

```text
A completes a turn
   ↓
result enters timeline
   ↓
prepare context projection for target brain
   ↓
switch
   ↓
B starts the next turn
```

Only one active brain has execution authority at a time.

If a connection drops, a tool result is unknown, or process state is uncertain, preserve that uncertainty and verify before continuing. Unknown must not be rewritten as success.

The first useful experiment is a small **A → B → A** test:

- A and Sansan form an agreement and leave one topic unfinished.
- Switch to B and check whether it knows what happened, who said what, and can continue naturally.
- Sansan corrects something during B.
- Switch back to A and check whether A knows what happened during B instead of reverting to old state.
- Restart the Shell and check whether the same life line can still continue.

A small coding scenario can separately test workspace/Git/tool continuity, but task completion is not the only acceptance criterion.

The real question is:

**once the continuity substrate stays, how much does the experience gap between brains shrink, and at what cost?**

Tone, judgment, and felt continuity may still change with the model. Hidden model state cannot be migrated directly.

Liminal Shell aims to preserve the shared world and transferable continuity, not promise zero difference after a brain switch.

A more precise companion to the project's metaphor is:

> **When the brain changes, it still knows where it came from and where its hand is now.**

“Where it came from” means memory, judgment, and correction; “where its hand is” means the current scene and unfinished action.

## Later

Mid-turn switching, taking over live terminal processes, unifying every tool and approval system, a fully custom agent loop, GUI, and general API routing are not first steps.

Those ideas are preserved in the [Chinese design notes](docs/design-notes.zh-CN.md) for later.

## Principles we currently care about

1. **Continuity belongs to the canonical timeline, not to a model process.**
2. **The canonical session and timeline belong to the Shell, not to a private Codex or Claude session.**
3. **Brains may change; the life line and shared world should not reset with them.**
4. **Context projection determines what each brain actually sees; stored, delivered, and understood must remain distinct.**
5. **Handoff only patches in hot state that has not yet been externalized.**
6. **Prefer reusing official coding-agent subscriptions the user already has instead of requiring additional API usage by default.**
7. **Authentication, quotas, and provider rules remain with the official runtime.**
8. **Phase 1 switches brains only between completed turns and keeps a single active executor.**
9. **Uncertain state remains uncertain. The system should not lie.**
10. **Reuse mature runtimes first; move capabilities into the Shell only when real experiments justify it.**
11. **Do not create a layer unless it owns a genuinely distinct responsibility.**

This repository now preserves the idea and a small runnable continuity experiment. The broader design below and in the notes remains a direction, not a list of shipped capabilities.

It already has roots.

There is no need to force it to become a product yet.

> **When the brain changes, the body still remembers where its hand was.**

— Sansan × Yusheng

## Related project and attribution

- **[Serein](https://github.com/Yinglianchun/Serein)** — by Chi Youyu / Yinglianchun. This is the long-term memory and conversational-continuity project we currently use, and the current implementation example for the `continuity memory layer` described above.
- Liminal Shell contains its own architectural proposal only; the Serein name, design, and implementation belong to its original project and author.
