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
crash after a durable turn start. They do not consume subscription quota.

For a real-runtime check, run the two `send` commands above in separate processes
and inspect `show`: expect one Liminal UUID, two different native thread IDs,
ordered replies, and two `turn.completed` events. This tests supplied-context
continuation, not migration of hidden runtime state.

During implementation, local tests passed; a live run confirmed official ChatGPT
login but could not initialize Codex inside the host's filesystem sandbox
(`state_5.sqlite` read-only / access denied), including after a permission grant.
Real generation and the two-turn live check therefore remain **unverified** here.

Integration reference: [official Codex non-interactive mode documentation](https://developers.openai.com/codex/noninteractive).
The installed CLI inspected during implementation was `codex-cli 0.155.1`.
