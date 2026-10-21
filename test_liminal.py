import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from uuid import uuid4
import unittest
from unittest.mock import patch

from liminal import Store, codex, PreflightFailure


def reply(events):
    return dict(thread_id='runtime-handle', replies=['你好'], usage={'input_tokens': 1})


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path('.test-' + uuid4().hex)
        self.directory.mkdir()
        self.path = self.directory.resolve() / 'timeline.sqlite3'
        self.store = Store(self.path)
        self.session = self.store.new()

    def tearDown(self):
        self.store.close()
        for file in self.directory.iterdir():
            file.unlink()
        self.directory.rmdir()

    def test_restart_order_and_projection(self):
        self.store.send(self.session, '记住蓝色', reply)
        original = self.store.events(self.session)
        self.store.close()
        self.store = Store(self.path)

        def continued(events):
            self.assertEqual([e['text'] for e in events if 'text' in e],
                             ['记住蓝色', '你好', '继续'])
            return reply(events)

        self.store.send(self.session, '继续', continued)
        events = self.store.events(self.session)
        self.assertEqual(events[:len(original)], original)
        self.assertEqual([e['seq'] for e in events], list(range(1, 10)))
        self.assertEqual([e['kind'] for e in events], ['session.created'] +
                         ['user.message', 'turn.started', 'assistant.message', 'turn.completed'] * 2)
        self.assertTrue(all(e['timestamp'].endswith('+00:00') for e in events))
        self.assertEqual(events[3]['runtime_thread_id'], 'runtime-handle')
        self.assertNotEqual(self.session, events[3]['runtime_thread_id'])

    def test_append_only_and_session_isolation(self):
        other = self.store.new()
        self.store.send(self.session, 'one', reply)
        self.assertEqual(len(self.store.events(other)), 1)
        for sql in ('UPDATE events SET kind="changed"', 'DELETE FROM events'):
            with self.assertRaises(sqlite3.IntegrityError), self.store.db:
                self.store.db.execute(sql)

    def test_unknown_empty_and_concurrent_send(self):
        for session, text in [('00000000-0000-0000-0000-000000000000', 'x'),
                              (self.session, '  ')]:
            with self.assertRaises(ValueError):
                self.store.send(session, text, reply)

        def competing(events):
            other = Store(self.path)
            try:
                with self.assertRaisesRegex(ValueError, 'Unresolved'):
                    other.send(self.session, 'competing', reply)
            finally:
                other.close()
            return reply(events)

        self.store.send(self.session, 'first', competing)

    def test_failure_and_process_crash_block_retries(self):
        def failed(events):
            raise RuntimeError('transport lost')

        with self.assertRaises(RuntimeError):
            self.store.send(self.session, 'first', failed)
        self.assertEqual(self.store.events(self.session)[-1]['kind'], 'turn.uncertain')
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            self.store.send(self.session, 'retry', reply)
        session = self.store.new()
        code = ('import os; from liminal import Store; '
                f's=Store({str(self.path)!r}); '
                f's.send({session!r}, "crash", lambda events: os._exit(7))')
        result = subprocess.run([sys.executable, '-c', code])
        self.assertEqual(result.returncode, 7)
        self.assertEqual(self.store.events(session)[-1]['kind'], 'turn.started')
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            self.store.send(session, 'retry', reply)

    def test_preflight_failure_survives_restart_and_allows_new_send(self):
        def unavailable(events):
            raise PreflightFailure('not logged in')

        with self.assertRaises(PreflightFailure):
            self.store.send(self.session, 'not delivered', unavailable)
        original = self.store.events(self.session)
        self.assertEqual(original[-1]['kind'], 'turn.preflight_failed')
        self.store.close()
        self.store = Store(self.path)
        self.store.send(self.session, 'try now', reply)
        self.assertEqual(self.store.events(self.session)[:len(original)], original)
        self.assertEqual(self.store.events(self.session)[-1]['kind'], 'turn.completed')

    def test_cli_new_and_show_across_processes(self):
        command = [sys.executable, 'liminal.py', '--db', str(self.path)]
        created = subprocess.check_output(command + ['new'], text=True).strip()
        shown = subprocess.check_output(command + ['show', created], text=True)
        self.assertEqual(json.loads(shown)['session'], created)


class AdapterTests(unittest.TestCase):
    @patch('liminal.shutil.which', return_value='codex')
    @patch('liminal.subprocess.run')
    def test_official_login_stdin_and_events(self, run, which):
        events = [dict(seq=2, kind='user.message', speaker='user', text='hello')]
        rows = [dict(type='thread.started', thread_id='native'),
                dict(type='item.completed', item=dict(type='agent_message', text='hi')),
                dict(type='turn.completed', usage={})]
        run.side_effect = [subprocess.CompletedProcess([], 0, '', 'Logged in using ChatGPT'),
                           subprocess.CompletedProcess([], 0, '\n'.join(map(json.dumps, rows)), '')]
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'unused', 'CODEX_API_KEY': 'unused'}):
            self.assertEqual(codex(events)['replies'], ['hi'])
        args, kwargs = run.call_args
        self.assertNotIn('--ignore-user-config', run.call_args_list[0].args[0])
        self.assertIn('--ignore-user-config', args[0][args[0].index('exec') + 1:])
        self.assertIn('--ephemeral', args[0])
        self.assertEqual(args[0][-1], '-')
        self.assertIn('hello', kwargs['input'])
        self.assertNotIn('CODEX_API_KEY', kwargs['env'])
        self.assertNotIn('OPENAI_API_KEY', kwargs['env'])
        self.assertIn('forced_login_method="chatgpt"', args[0])
        cwd = kwargs['cwd']
        self.assertNotEqual(cwd, Path.cwd())
        self.assertEqual(cwd, run.call_args_list[0].kwargs['cwd'])
        self.assertFalse(cwd.exists())

    @patch('liminal.shutil.which', return_value='codex')
    @patch('liminal.subprocess.run')
    def test_neutral_directory_empty_and_failed_inputs_not_replayed(self, run, which):
        rows = [dict(type='thread.started', thread_id='native'),
                dict(type='item.completed', item=dict(type='agent_message', text='hi')),
                dict(type='turn.completed')]

        def child(command, **kwargs):
            self.assertEqual(list(kwargs['cwd'].iterdir()), [])
            if 'login' in command:
                return subprocess.CompletedProcess([], 0, '', 'Logged in using ChatGPT')
            self.assertNotIn('not delivered', kwargs['input'])
            self.assertIn('new message', kwargs['input'])
            return subprocess.CompletedProcess([], 0, '\n'.join(map(json.dumps, rows)), '')

        run.side_effect = child
        codex([dict(seq=1, kind='user.message', turn='old', speaker='user', text='not delivered'),
               dict(kind='turn.preflight_failed', turn='old'),
               dict(seq=3, kind='user.message', turn='new', speaker='user', text='new message')])

    @patch('liminal.shutil.which', return_value=None)
    def test_missing_executable_is_preflight(self, which):
        with self.assertRaises(PreflightFailure):
            codex([])

    @patch('liminal.shutil.which', return_value='codex')
    @patch('liminal.subprocess.run')
    def test_exec_transport_exception_is_not_preflight(self, run, which):
        run.side_effect = [subprocess.CompletedProcess([], 0, '', 'Logged in using ChatGPT'),
                           OSError('pipe failure after possible launch')]
        with self.assertRaises(OSError):
            codex([])

    @patch('liminal.shutil.which', return_value='codex')
    @patch('liminal.subprocess.run')
    def test_reject_api_auth_and_incomplete_output(self, run, which):
        run.return_value = subprocess.CompletedProcess([], 0, '', 'Logged in using an API key')
        with self.assertRaisesRegex(RuntimeError, 'ChatGPT login'):
            codex([])
        self.assertEqual(run.call_count, 1)
        for output, status in [('', 0), ('not json', 0), ('', 1),
                               ('{"type":"turn.failed"}', 0)]:
            run.side_effect = [subprocess.CompletedProcess([], 0, '', 'Logged in using ChatGPT'),
                               subprocess.CompletedProcess([], status, output, '')]
            with self.assertRaises((RuntimeError, ValueError)):
                codex([])


if __name__ == '__main__':
    unittest.main()
