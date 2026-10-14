# Liminal Shell

> **When the brain changes, the body still remembers where its hand was.**

[中文版](README.zh-CN.md)

**Status:** this repository currently preserves the design. Implementation has not started, and there is no need to rush it into a product.

---

We did not begin by wanting another multi-model client.

One day, Sansan asked a simpler question:

> If Codex and Claude Code already exist, could we build our own shell and let both of them live inside it?

At first it sounded like a convenient model switcher.

But the interesting part was not convenient model selection.

It was a different question:

**If the brain can change, what must remain so that the working self does not have to be born again every time?**

We had already been asking a version of that question elsewhere.

In conversation, windows change, models change, and processes end. If continuity lives inside one particular instance, every new window becomes another reintroduction.

So we arrived at a principle:

**continuity should not live inside a single instance.**

What remains continuous is a canonical timeline: what already happened, what judgment has just formed, what action is unfinished, and what the next brain should inherit as its own ongoing state.

Then the same answer appeared again in coding.

Sharing a directory is not enough.

Two agents can share files without sharing one thread.

So Liminal Shell is not primarily trying to preserve the model.

It is trying to preserve the **body**:

the workspace,  
the files,  
the terminal,  
the Git state,  
the permission boundary,  
and most importantly, **one canonical thread**.

Codex may leave.

Claude may take over.

Other brains may come later.

But the thread should not disappear with the brain.

## Why “Liminal Shell”

`Liminal` means threshold: the place where one state actually becomes another.

`Shell` is both a shell and a command-line environment.

We do not want to pretend that a model switch never happened.

We want to make the threshold where it happens into a place that can be inhabited.

The room, the desk, the files, the terminal, the history, and the active thread never belonged to one brain in the first place.

## What it may look like

The goal is closer to a model switch inside one thread than to a handoff between two independent agent sessions:

```text
Liminal Thread #42
│
├─ Sansan: inspect this error
├─ [Codex] I'll start with the parser...
├─ [tool] read / edit / test
├─ [Codex] this change is only half done
├─ Sansan: /model claude
├─ system: Codex → Claude
├─ [Claude] continues with the same thread and workspace
└─ ...
```

In other words:

**the thread belongs to Liminal Shell; the model is only the thinking organ selected for the current turn.**

The ideal switch is not leaving one complete world and moving into another.

It is simply:

```text
/model codex
/model claude
/model ...
```

The model changes.

The thread does not.

The workspace does not.

Git does not.

And the human does not need to explain the background again.

## The canonical thread is the core

Liminal Shell should own one canonical thread containing all explicitly shareable context:

- user messages
- agent-visible conversation history
- current task
- tool calls and results
- workspace / repository state
- Git diff
- test output
- confirmed decisions
- unresolved questions
- Serein resume
- durable working agreements

The shell can then project that same thread into the context format each brain understands:

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

This does not mean forcing a private Codex session object into Claude.

Different models may still have different system prompts, tool definitions, tokenizers, agent loops, and hidden internal state.

“Same thread” therefore does not require identical neural state.

It requires **thread ownership to live in the shell rather than inside a model runtime**.

## Handoff still exists, but it no longer carries all continuity

We revised the role of handoff.

The earlier design treated every model switch like a full shift-change document.

A better model is:

**canonical thread provides continuity by default; handoff only patches in hot state that has not yet been externalized.**

For example:

> I have started to suspect that the bug is not in the parser but in cache invalidation, but I have not verified it yet.

That thought may not exist in code, Git, or a formal conclusion yet.

If it is worth preserving, it needs to be externalized before the switch.

So handoff becomes a small delta containing things like:

- an unresolved direction
- an intention that has not yet become an action
- the reason a dead end was rejected
- the next step the current brain was about to take
- a recently formed suspicion not yet represented elsewhere

Anything recoverable from the canonical thread, workspace, Git, or tool results should not be redundantly summarized.

Conceptually:

```text
one canonical thread
        │
        ├─ shared: history / workspace / git / tools / Serein
        │
        └─ handoff: only still-private hot state
        │
        ▼
switch model
        │
        ▼
next brain continues the same thread
```

## Continuity memory: currently Serein, but not Serein-only

Liminal Shell should not invent another long-term memory system, and it should not hard-code one specific memory project as a mandatory dependency.

The system we currently use is **[Serein](https://github.com/Yinglianchun/Serein)** by **Chi Youyu / Yinglianchun**. It provides cross-window long-term memory and continuity features such as Scene, Event, and resume.

In our current stack, Serein owns a deeper responsibility:

**remembering what this body has lived through, and why it arrived at its current judgment.**

But Liminal Shell should target a more abstract **continuity memory layer**.

Any other memory project that can provide comparable capabilities—long-term memory, breakpoint/resume state, traceable history, and cross-window or cross-model recall—could theoretically be integrated instead. Serein is our current implementation, not the only valid one.

The intended split is roughly:

- `AGENTS.md` — durable working agreements and long-lived self-state
- continuity memory layer (currently Serein) — long-term history, current breakpoint, recent state, unfinished thought, and traceable formation/evidence
- Liminal Shell — canonical thread, cwd, files, Git, terminal, permissions, process/session state
- handoff — only hot state not yet represented in the canonical thread
- Codex / Claude / other agents — the brain doing the thinking and execution right now

Each layer should remember only what it genuinely owns.

> Serein appears throughout this document because it is the continuity-memory project we actually use today, not because Liminal Shell must depend on Serein.

## Phase 1 — borrow existing brains

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

The point of this phase is not to build a new coding agent from scratch.

It is to let different brains take turns inside the same thread instead of giving every agent runtime its own unrelated life.

## Phase 2 — maybe the shell grows its own nervous system

If this abstraction proves worth growing, Liminal Shell could eventually own its own agent loop:

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

At that point Codex, Claude, or another model would no longer be the whole assistant.

They would be replaceable thinking organs inside the same working body.

But that is later.

This repository exists now simply to keep the idea safe until it is ready to grow.

## Principles we currently care about

1. **Continuity belongs to the canonical timeline, not to a model process.**
2. **The canonical thread belongs to the shell, not to a private Codex or Claude session.**
3. **The model may change; the thread, workspace, and working scene should not reset with it.**
4. **Explicit context is shared by default; handoff only patches in hot state that has not yet been externalized.**
5. **The human should not have to pay the context-reconstruction cost after every switch.**
6. **Durable agreements and current state should stay in different layers.**
7. **Git state must remain inspectable.**
8. **Dangerous, destructive, credential-related, or system-level actions remain permission-gated.**
9. **Reuse mature agents before deciding what is worth rebuilding.**
10. **Do not create an architectural layer unless it owns a genuinely distinct responsibility.**

## Not yet

For now, this is not trying to become:

- another multi-model chat client
- a replacement for Codex CLI
- a replacement for Claude Code
- a duplicate long-term memory system
- another personality-state database
- a universal model abstraction for its own sake
- a fully custom agent loop before there is evidence it is needed

For now, this repository does one thing:

**it keeps the idea.**

It already has roots.

There is no need to force it to become a product yet.

When implementation eventually begins, the first thing worth protecting will still be the sentence under the title:

> **When the brain changes, the body still remembers where its hand was.**

— Sansan × Yusheng

## Related project and attribution

- **[Serein](https://github.com/Yinglianchun/Serein)** — by Chi Youyu / Yinglianchun. This is the long-term memory and conversational-continuity project we currently use, and the current implementation example for the `continuity memory layer` described above.
- Liminal Shell contains its own architectural proposal only; the Serein name, design, and implementation belong to its original project and author.
