# Liminal Shell

> **When the brain changes, the body still remembers where its hand was.**

[中文版](README.zh-CN.md)

**Status:** this repository currently preserves the design. Implementation has not started, and there is no need to rush it into a product.

---

We did not begin by wanting another multi-model client.

One day, Sansan asked a simpler question:

> If Codex and Claude Code already exist, could we build our own shell and let both of them live inside it?

At first it sounded like a convenient launcher:

```text
/codex
/claude
/back
```

But the interesting part was not convenient model selection.

It was a different question:

**If the brain can change, what must remain so that the working self does not have to be born again every time?**

We had already been asking a version of that question elsewhere.

In conversation, windows change, models change, and processes end. If continuity lives inside one particular instance, every new window becomes another reintroduction.

So we arrived at a principle:

**continuity should not live inside a single instance.**

What remains continuous is the canonical timeline: what already happened, what judgment has just formed, what action is unfinished, and what the next instance should be able to inherit as its own ongoing state.

Then the same answer appeared again in coding.

Why should a project have to reintroduce itself because a Codex session ended and Claude Code took over?

Why should a model switch require the human to explain the repository, the current task, the failed attempts, and the reason the last approach was abandoned?

Sharing a directory is not enough.

Two agents can share files without sharing the live working scene.

The code that was changed a minute ago, the hypothesis that is still unverified, the dead end that was already explored, the next file the previous agent was about to touch—none of that becomes shared merely because the cwd is the same.

So Liminal Shell is not primarily trying to preserve the model.

It is trying to preserve the **body**:

the workspace,  
the files,  
the terminal,  
the Git state,  
the permission boundary,  
and the task that is still warm.

Codex may leave.

Claude Code may take over.

Other brains may come later.

But the body should not lose its memory just because the brain changed.

## Why “Liminal Shell”

`Liminal` means threshold: the place where one state actually becomes another.

`Shell` is both a shell and a command-line environment.

We do not want to pretend that a model switch never happened.

We want to make the threshold where it happens into a place that can be inhabited.

A new agent should not enter an empty room.

It should arrive somewhere that already knows where the work has reached.

## What it may look like

The first version would not reimplement Codex CLI or Claude Code.

They already have mature coding-agent loops. Liminal Shell would sit above them as the cockpit:

```text
liminal
  ├─ /codex   → start Codex in the current workspace
  ├─ /claude  → start Claude Code in the current workspace
  └─ /back    → return to Liminal Shell
```

They would share:

- the same working directory and repository
- the same Git state
- the same long-lived working agreements
- the same terminal and permission boundaries
- the same Serein continuity source
- the same current-task handoff

This is not “several models in one dropdown”.

A normal multi-model client asks:

> Which model do I want now?

Liminal Shell asks:

> After the model changes, how does the working self keep its hand on the same place?

## A handoff is not a project summary

The important layer is not the launcher.

It is the handoff.

A cold summary such as “changed A, pending B, next C” loses too much.

The handoff should preserve the still-warm working scene:

- the actual problem being solved
- completed edits
- failed attempts and why they were abandoned
- unresolved judgments
- recently touched files
- current Git diff and repository state
- uncommitted risks
- the next intended action
- recent context that still affects the current decision
- the difference between durable agreements and temporary state

Conceptually:

```text
current agent
    ↓
leave a still-warm handoff
    ├─ current task
    ├─ completed changes
    ├─ unresolved judgments
    ├─ failed attempts and reasons
    ├─ git diff / repo state
    └─ intended next action
    ↓
exit
    ↓
next agent enters the same shell
    ↓
load the same workspace + Serein resume + handoff
    ↓
continue from here
```

Not “one employee leaves a status report for another”.

More like one body changing brains while its hand remains where it was.

## Where Serein fits

Liminal Shell should not invent another memory system.

Serein owns a deeper responsibility:

**remembering what this body has lived through, and why it arrived at its current judgment.**

The intended split is roughly:

- `AGENTS.md` — durable working agreements and long-lived self-state
- Serein `resume` — the current breakpoint, recent state, unfinished thought
- Serein Scene / Diary / Event — longer history, formation, and evidence
- Liminal Shell — cwd, files, Git, terminal, permissions, process/session state, and the current handoff
- Codex / Claude Code / other agents — the brain doing the thinking and execution right now

Each layer should remember only what it genuinely owns.

## Phase 1 — borrow existing brains

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

The point of this phase is not to build a new coding agent from scratch.

The point is to protect continuity when one capable agent leaves and another enters.

## Phase 2 — maybe the shell grows its own nervous system

If this abstraction proves worth growing, Liminal Shell could eventually own its own agent loop:

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

At that point Codex, Claude, or another model would no longer be the whole assistant.

They would be replaceable thinking organs inside the same working body.

But that is later.

This repository exists now simply to keep the idea safe until it is ready to grow.

## Principles we currently care about

1. **Continuity belongs to the canonical timeline, not to a model process.**
2. **The model may change; the working body should not reset with it.**
3. **A handoff should preserve the scene, not merely summarize the result.**
4. **The human should not have to pay the context-reconstruction cost after every switch.**
5. **Durable agreements and current state should stay in different layers.**
6. **Git state must remain inspectable.**
7. **Dangerous, destructive, credential-related, or system-level actions remain permission-gated.**
8. **Reuse mature agents before deciding what is worth rebuilding.**
9. **Do not create an architectural layer unless it owns a genuinely distinct responsibility.**

## Not yet

For now, this is not trying to become:

- another multi-model chat client
- a replacement for Codex CLI
- a replacement for Claude Code
- a duplicate Serein
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
