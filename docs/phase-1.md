# Phase 1 minimal vertical slice

Requires Python 3.11+ and the official Codex CLI on PATH. No Python packages,
API keys, credential copying, UI, or server are needed.

```sh
codex login
python liminal.py new
# Copy the printed Liminal UUID, then use it in every command:
python liminal.py send <session-uuid> "Remember that our marker is blue."
python liminal.py show <session-uuid>
# Exit the terminal / restart the program, then continue the same UUID:
python liminal.py send <session-uuid> "What marker did we agree on?"
```

PowerShell can capture the ID with `$session = python liminal.py new`.
`show` prints the canonical events as UTF-8 JSON lines. On Windows, if the
terminal uses a legacy encoding, set `$env:PYTHONIOENCODING = 'utf-8'`.

The default database is `~/.liminal-shell/timeline.sqlite3`. To keep everything
in a chosen directory, put `--db ./timeline.sqlite3` **before** each command.
The same database path and Liminal UUID restore the same session. Back up the
database while no sends are running. Timestamps are UTC; `seq` is the canonical
ordering within a session, independent of clock changes.

## Implemented boundary

- Shell-generated session UUID, append-only SQLite events, user text, visible
  assistant messages, runtime/thread provenance, UTC timestamps and turn boundaries.
- User message and turn start commit before execution. Assistant replies and
  completion commit atomically. SQL triggers reject updates and deletes.
- Atomic turn reservation prevents concurrent sends to the same session.
- Both login preflight and generation run in a fresh empty temporary cwd, outside
  the caller repository. The directory is removed afterward. Caller workspace
  files, project instructions and project config are not the runtime working root.
  This is context isolation, not an additional filesystem security sandbox.
- Official `codex exec --json --ephemeral --sandbox read-only`, using the existing
  official ChatGPT login. Shell never opens credential files or accepts an API key.
  API-key environment variables are removed from the child environment, the official
  OpenAI provider and ChatGPT login are selected explicitly, and login status is checked.
- Each invocation is a fresh native runtime. Full verbatim user/assistant history
  is projected from the Shell database on every turn, with sequence and speaker labels.
  Native thread IDs are provenance only; they do not define or restore Liminal identity.
  This deliberately avoids native-session binding/delta synchronization in this slice.
- User Codex config is ignored for execution to avoid enabling configured integrations.
  The runtime selects its default model. No model or subscription-usage promises are made.

## Deliberate limits

This is a text continuity experiment, not the full Phase 1 design. Claude, brain
switching, handoff, memory, frontend, plugin runtime, native-thread resume,
workspace/process ownership, tool/approval unification, compaction and a context
delivery ledger are still design work. No A → B → A result is claimed.

Codex retains its own agent loop, tools and permissions. The sandbox is read-only;
this CLI does not implement a coding workspace executor. Output is buffered until
the child exits. Only completed visible messages from a confirmed successful turn
are normalized; streaming text and tool events are not a canonical tool audit.
The stored projection range means context was prepared, not that it was understood.
Full-history projection is intentionally small-session only; context overflow is
an error, never silent truncation.

Missing CLI, neutral-directory creation failure, and failed/unavailable official
login checks produce `turn.preflight_failed`: generation was never invoked. The
user message remains in the append-only audit, but is excluded from later context
projection. Fix the preflight issue, then explicitly send the message again using
the same UUID; restart does not block that new send. There is no automatic retry.

Once generation is invoked, errors are conservatively uncertain, including
subprocess transport errors: the buffered runner cannot prove whether execution
already began. A nonzero exec exit alone does not prove a preflight failure.

If a turn crashes, is interrupted, exits unsuccessfully, or yields an unrecognized
protocol, its outcome remains unresolved (`turn.started` or `turn.uncertain`).
Further sends to that session are blocked, including after restart. Inspect `show`
and the official runtime before any manual recovery. This version has no automatic
retry or recovery command: do not delete events or assume execution did not happen.
Failed/incomplete runtime output is not presented as a completed assistant reply.

## Validation

```sh
python -m unittest -v
```

Tests use an isolated local database and simulated runtime responses. They cover
restart persistence, CLI processes, event order, session isolation, append-only
guards, competing sends, authentication/protocol errors, and an actual subprocess
crash after a durable turn start. They also verify neutral cwd/cleanup, preflight
retry after restart, failed-message exclusion and conservative transport handling.
They do not consume subscription quota. GitHub Actions runs the suite on Windows
and Linux with Python 3.11 and 3.14; CI never authenticates or calls Codex.

For a local real-runtime check after checking out the PR branch:

```powershell
$env:PYTHONIOENCODING = "utf-8"
$session = python liminal.py --db ./smoke.sqlite3 new
python liminal.py --db ./smoke.sqlite3 send $session "Remember cobalt-731. Reply only ACK. Do not use tools."
# Save the UUID; close the terminal, open another, and restore it:
$session = "<saved-liminal-uuid>"
python liminal.py --db ./smoke.sqlite3 send $session "What token did I ask you to remember? Do not use tools."
python liminal.py --db ./smoke.sqlite3 show $session
```

Use the same absolute database path (or return to the same directory) in both
terminals. Expect `cobalt-731` in the second reply.

Run the two `send` commands in separate processes
and inspect `show`: expect one Liminal UUID, two different native thread IDs,
ordered replies, and two `turn.completed` events. This tests supplied-context
continuation, not migration of hidden runtime state.

### Recorded real smoke result

The user completed the real two-turn Codex smoke test successfully on Windows
with Python 3.14.5 and codex-cli 0.155.1, using the existing official ChatGPT login.
The supplied timeline records 2026-10-21 07:17:29–07:18:23 UTC.

- Liminal session: `818d003c-4a0f-4a54-a054-37395a13a6ab`.
- First native thread: `01a15d52-87cd-7c60-bfb6-136214126f63`; visible reply: `ACK`.
- After closing and reopening PowerShell, second native thread:
  `01a15d53-2d3f-7c11-8870-c1c5d92302ef`; visible reply: `cobalt-731`.
- The same Liminal session retained events 1–9 in order, including both user
  messages, both visible replies, provenance, timestamps and two `turn.completed` events.

This verifies **Shell-supplied context continuity** across process restart with
separate native runtimes. It does not verify A → B → A brain switching, hidden
runtime state migration, or native-session handoff. Earlier agent-host attempts
were blocked by filesystem sandbox initialization; the successful user-run local
smoke test supplies the real-generation evidence.

Integration reference: [official Codex non-interactive mode documentation](https://developers.openai.com/codex/noninteractive).
The installed CLI inspected during implementation was `codex-cli 0.155.1`.
