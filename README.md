# Liminal Shell

> A persistent local shell for switching coding agents without switching worlds.

[中文版](README.zh-CN.md)

**Status:** idea parked for later. This repository currently stores the architecture concept only; implementation has not started.

## What it is

Liminal Shell is a local terminal host that keeps the **workspace, session state, tools, permissions, and continuity** stable while allowing the underlying coding agent to change.

The first version would not reimplement a coding-agent loop. Instead, it would use existing agents such as **OpenAI Codex CLI** and **Claude Code** as interchangeable engines behind one local shell.

```text
liminal
  ├─ /codex   → start Codex in the current workspace
  ├─ /claude  → start Claude Code in the current workspace
  └─ /back    → return to the shell
```

The agents would share:

- the same working directory and repository
- the same Git state
- the same long-lived project agreements
- the same Serein continuity source
- the same handoff state for the current task

The goal is not merely "multiple CLIs in one launcher". The goal is **switching the active agent without resetting the working world around it**.

## Why a shell layer

Launching two agent CLIs in the same directory already gives them shared files, but it does not give them shared live context.

A useful switch therefore needs an explicit handoff:

```text
current agent
    ↓
capture current task
capture completed changes
capture unresolved reasoning
capture relevant git diff / repo state
capture recent handoff context
    ↓
stop current agent
    ↓
start next agent
    ↓
load the same Serein resume + handoff
    ↓
continue the same task
```

This is the central idea: **change the brain, not the body**.

## Responsibility boundaries

The intended separation is:

- `AGENTS.md` — stable long-term working agreements / durable self-state
- Serein `resume` — current conversational breakpoint, recent state, unfinished thoughts
- Serein Scene / Diary / Event — history and evidence
- Liminal Shell — cwd, files, Git, terminal, permissions, process/session state
- coding agent / model backend — interchangeable execution engine

The shell should not invent another redundant personality/state layer when an existing system already owns that responsibility.

## Phase 1 — use existing coding agents as engines

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

This phase deliberately reuses mature agent loops instead of rebuilding file editing, shell execution, repository inspection, tool orchestration, and coding workflows from scratch.

## Phase 2 — optional native agent host

If the abstraction proves useful, Liminal Shell could later own its own agent loop:

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

At that point Codex, Claude, or another model would become execution backends rather than the whole assistant environment.

## Design principles

1. **Continuity belongs to the canonical timeline, not to a model process.**
2. **Models and agents may change; the workspace and canonical state should not.**
3. **A model switch should carry a handoff instead of making the user rebuild context.**
4. **Stable agreements and current state are different things and should stay in different layers.**
5. **Dangerous, destructive, credential-related, or system-level actions should remain permission-gated.**
6. **Git state should remain inspectable; changes should not disappear behind the shell.**
7. **Reuse mature coding-agent infrastructure before attempting to replace it.**
8. **Avoid extra architecture layers unless they own a genuinely distinct responsibility.**

## Non-goals for now

This repository is not currently trying to:

- replace Codex CLI or Claude Code
- implement a new coding-agent loop
- define a new personality system
- duplicate Serein memory
- provide a universal model API abstraction immediately

For now, it is simply a place to preserve the idea until the surrounding continuity and handoff infrastructure is ready enough to justify implementation.
