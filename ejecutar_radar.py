"""Bounded execution/verification loop. No trading or credentials in output."""
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def command(*args, check=True, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=check, **kwargs)


def persist():
    command("git", "config", "user.name", "github-actions[bot]")
    command("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    command("git", "add", "docs/")
    if os.getenv("GITHUB_REPOSITORY_PRIVATE", "").lower() == "true" and (ROOT / "history").is_dir():
        command("git", "add", "history/")
    changed = command("git", "diff", "--cached", "--quiet", check=False).returncode
    if changed:
        command("git", "commit", "-m", "Actualizar auditoría Radar Fintual")
        command("git", "pull", "--rebase")
        command("git", "push")


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
