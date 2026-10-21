"""Minimal Shell-owned continuity substrate. Python 3.11+, no dependencies."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from uuid import UUID, uuid4


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=5)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                session TEXT NOT NULL, seq INTEGER NOT NULL,
                timestamp TEXT NOT NULL, kind TEXT NOT NULL,
                payload TEXT NOT NULL, PRIMARY KEY(session, seq));
            CREATE TRIGGER IF NOT EXISTS no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT, 'append-only timeline'); END;
            CREATE TRIGGER IF NOT EXISTS no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT, 'append-only timeline'); END;
        """)

    def close(self):
        self.db.close()

    def events(self, session):
        if str(UUID(session)) != session:
            raise ValueError('Use the full Liminal session UUID')
        return [dict(session=session, seq=r[0], timestamp=r[1], kind=r[2],
                     **json.loads(r[3])) for r in self.db.execute(
                         'SELECT seq,timestamp,kind,payload FROM events WHERE session=? ORDER BY seq',
                         (session,))]

    def append(self, session, kind, **payload):
        self.db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)', (
            session, self.db.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events WHERE session=?',
                                     (session,)).fetchone()[0],
            datetime.now(timezone.utc).isoformat(), kind,
            json.dumps(payload, ensure_ascii=False)))

    def new(self):
        session = str(uuid4())
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            self.append(session, 'session.created', runtime='codex')
        return session

    def send(self, session, text, runtime):
        if not text.strip():
            raise ValueError('Message must not be empty')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            history = self.events(session)
            if not history:
                raise ValueError('Unknown Liminal session')
            if history[-1]['kind'] not in ('session.created', 'turn.completed'):
                raise ValueError('Unresolved turn: inspect show; no automatic retry is safe')
            turn = str(uuid4())
            self.append(session, 'user.message', turn=turn, speaker='user', text=text)
            self.append(session, 'turn.started', turn=turn, runtime='codex',
                        projection='full-verbatim-messages', through_seq=history[-1]['seq'] + 1)
        # Committed before invoking the runtime. A crash leaves a blocking unresolved turn.
        try:
            result = runtime(self.events(session))
            with self.db:
                self.db.execute('BEGIN IMMEDIATE')
                for reply in result['replies']:
                    self.append(session, 'assistant.message', turn=turn, speaker='assistant',
                                runtime='codex', runtime_thread_id=result['thread_id'], text=reply)
                self.append(session, 'turn.completed', turn=turn, runtime='codex',
                            runtime_thread_id=result['thread_id'], usage=result.get('usage'))
            return '\n\n'.join(result['replies'])
        except (Exception, KeyboardInterrupt):
            with self.db:
                self.append(session, 'turn.uncertain', turn=turn, runtime='codex',
                            reason='Runtime or persistence did not confirm a complete turn')
            raise


def codex(events):
    executable = shutil.which('codex')
    if not executable:
        raise RuntimeError('Install the official Codex CLI and run codex login first')
    env = dict(os.environ)
    for key in ('OPENAI_API_KEY', 'CODEX_API_KEY'):
        env.pop(key, None)
    base = [executable, '-c', 'forced_login_method="chatgpt"',
            '-c', 'model_provider="openai"']
    status = subprocess.run(base + ['login', 'status'], capture_output=True,
                            text=True, encoding='utf-8', env=env)
    if status.returncode or 'chatgpt' not in (status.stdout + status.stderr).lower():
        raise RuntimeError('Official Codex ChatGPT login required; run codex login')
    messages = [{k: e[k] for k in ('seq', 'speaker', 'text')} for e in events
                if e['kind'] in ('user.message', 'assistant.message')]
    prompt = ('Continue this Liminal session. The following JSON is the canonical conversation, '
              'in order; respond to its last user message. Preserve speaker attribution.\n'
              + json.dumps(messages, ensure_ascii=False))
    process = subprocess.run(base + ['exec', '--ignore-user-config', '--json', '--ephemeral', '--skip-git-repo-check',
                                    '--sandbox', 'read-only', '-'], input=prompt,
                             capture_output=True, text=True, encoding='utf-8', env=env)
    if process.returncode:
        raise RuntimeError(f'Codex exited {process.returncode}; outcome uncertain')
    rows = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    threads = [r['thread_id'] for r in rows if r.get('type') == 'thread.started']
    completed = [r for r in rows if r.get('type') == 'turn.completed']
    replies = [r['item']['text'] for r in rows if r.get('type') == 'item.completed'
               and r.get('item', {}).get('type') == 'agent_message']
    if len(threads) != 1 or len(completed) != 1 or not replies or any(
            r.get('type') in ('error', 'turn.failed') for r in rows):
        raise RuntimeError('Codex did not confirm a complete visible reply')
    return dict(thread_id=threads[0], replies=replies, usage=completed[0].get('usage'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default=str(Path.home() / '.liminal-shell' / 'timeline.sqlite3'))
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('new')
    for name in ('show', 'send'):
        sub = commands.add_parser(name)
        sub.add_argument('session')
        if name == 'send':
            sub.add_argument('message')
    args = parser.parse_args()
    store = Store(args.db)
    try:
        if args.command == 'new':
            print(store.new())
        elif args.command == 'show':
            events = store.events(args.session)
            if not events:
                raise ValueError('Unknown Liminal session')
            for event in events:
                print(json.dumps(event, ensure_ascii=False))
        else:
            print(store.send(args.session, args.message, codex))
    except (ValueError, RuntimeError, OSError, sqlite3.Error) as error:
        parser.exit(1, f'{error}\n')
    finally:
        store.close()


if __name__ == '__main__':
    main()
