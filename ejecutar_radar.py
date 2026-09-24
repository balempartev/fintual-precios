"""Bounded execution/verification loop. No trading or credentials in output."""
import os
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def command(*args, check=True, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=check, **kwargs)


def reconcile(path, remote, produced):
    """Preserve append-only ledgers and newer diagnoses after another job pushes."""
    if path.endswith('.jsonl'):
        prior = remote.decode().splitlines()
        additions = [line for line in produced.decode().splitlines() if line not in prior]
        return ('\n'.join(prior + additions) + '\n').encode()
    if path == 'docs/recovery_state.json':
        try:
            old, new = json.loads(remote), json.loads(produced)
            if old.get('date') != new.get('date'):
                return produced if new.get('date', '') > old.get('date', '') else remote
            new['attempts'] = max(old.get('attempts', 0), new.get('attempts', 0))
            new['last_attempt'] = max(old.get('last_attempt') or '', new.get('last_attempt') or '') or None
            for flag in ('recovery_notified', 'failure_signaled'):
                new[flag] = bool(old.get(flag) or new.get(flag))
            new['incident_number'] = new.get('incident_number') or old.get('incident_number')
            return (json.dumps(new, indent=2) + '\n').encode()
        except (ValueError, TypeError):
            return produced
    try:
        old, new = json.loads(remote), json.loads(produced)
        timestamp = ('checked_at_utc' if path == 'docs/vigilancia.json' else
                     'updated_at_utc' if path == 'docs/sectores.json' else 'generated_at_utc')
        if old.get(timestamp, '') > new.get(timestamp, ''):
            return remote
    except (ValueError, TypeError, AttributeError):
        pass
    if path == 'docs/lectura_rapida.md':
        return remote if remote.splitlines()[:1] > produced.splitlines()[:1] else produced
    return produced


def persist():
    command("git", "config", "user.name", "github-actions[bot]")
    command("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    command("git", "add", "docs/")
    if os.getenv("GITHUB_REPOSITORY_PRIVATE", "").lower() == "true" and (ROOT / "history").is_dir():
        command("git", "add", "history/")
    paths = command('git', 'diff', '--cached', '--name-only', '-z', capture_output=True).stdout.decode().strip('\0').split('\0')
    if not paths or paths == ['']:
        return
    # Runner checkout is disposable. Save only files changed by this job, fetch
    # the newest tree and reapply them. A concurrent watchdog/capture may have
    # updated the same ledger while this capture spent 90 seconds scanning.
    produced = {name: (ROOT / name).read_bytes() for name in paths}
    for attempt in range(4):
        command('git', 'fetch', 'origin', 'main')
        command('git', 'reset', '--hard', 'origin/main')
        for name, content in produced.items():
            target = ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(reconcile(name, target.read_bytes() if target.exists() else b'', content))
        command('git', 'add', '--', *paths)
        if command('git', 'diff', '--cached', '--quiet', check=False).returncode == 0:
            return
        command('git', 'commit', '-m', 'Actualizar auditoría Radar Fintual')
        if command('git', 'push', check=False).returncode == 0:
            return
        print(f'Concurrent push; retry {attempt + 1}/4', flush=True)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError('Could not publish operational ledger after four retries')


def main():
    cycles = 3 if os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch" and os.getenv("VALIDATION_CYCLES") == "3" else 1
    origin = time.monotonic()
    failed = False
    for cycle in range(1, cycles + 1):
        # Start-to-start target includes scan and persistence duration.
        time.sleep(max(0, origin + (cycle - 1) * 300 - time.monotonic()))
        print(f"Validation cycle {cycle}/{cycles}", flush=True)
        env = {**os.environ, "RADAR_CYCLE": str(cycle)}
        try:
            result = command(sys.executable, "actualizar_precios.py", check=False, env=env, timeout=240)
            failed |= result.returncode != 0
        except subprocess.TimeoutExpired:
            print("Collector timeout after 240 seconds; no successful update claimed", flush=True)
            failed = True
        # Persist diagnostics even when the collector exits with no quotes.
        persist()
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
