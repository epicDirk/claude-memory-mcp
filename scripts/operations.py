import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from falkordb import FalkorDB

CONTAINER_NAME = "claude-memory-graph"
BACKUP_DIR = Path("backups")


def run_command(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr.decode()}")
        return False


def check_health() -> bool:
    print("Checking system health...")
    try:
        client = FalkorDB(host="localhost", port=6379, password="claudememory2026")
        # Just select the graph implies connection check
        graph = client.select_graph("claude_memory")
        # Simple query to check responsiveness
        res = graph.query("MATCH (n) RETURN count(n)")
        count = res.result_set[0][0]
        print(f"✅ Connection successful. Node count: {count}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def backup() -> bool:
    print(f"Starting backup for {CONTAINER_NAME}...")

    # 1. Trigger SAVE
    if not run_command(
        ["docker", "exec", CONTAINER_NAME, "redis-cli", "-a", "claudememory2026", "SAVE"]
    ):
        return False

    # 2. Ensure backup dir exists
    BACKUP_DIR.mkdir(exist_ok=True)

    # 3. Copy dump.rdb
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_file = BACKUP_DIR / f"dump_{timestamp}.rdb"

    if run_command(
        ["docker", "cp", f"{CONTAINER_NAME}:/var/lib/falkordb/data/dump.rdb", str(target_file)]
    ):
        print(f"✅ Backup saved to {target_file}")
        return True
    return False


def restore(snapshot_path: str) -> bool:
    print(f"Restoring from {snapshot_path}...")
    path = Path(snapshot_path)
    if not path.exists():
        print(f"❌ Snapshot not found: {path}")
        return False

    # 1. Stop container? No, usually replace file then restart.
    # But if redis is running, replacing dump.rdb might be ignored or overwritten on shutdown.
    # Best practice: Stop, Copy, Start.

    print("Stopping container...")
    if not run_command(["docker", "stop", CONTAINER_NAME]):
        return False

    print("Copying snapshot...")
    # docker cp can copy to stopped container
    if not run_command(
        ["docker", "cp", str(path), f"{CONTAINER_NAME}:/var/lib/falkordb/data/dump.rdb"]
    ):
        print("❌ Failed to copy snapshot.")
        # Try to start anyway?
        run_command(["docker", "start", CONTAINER_NAME])
        return False

    print("Starting container...")
    if not run_command(["docker", "start", CONTAINER_NAME]):
        return False

    print("✅ Restore complete. Waiting for DB to initialize...")
    time.sleep(5)
    return check_health()


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude Memory Operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check database health")
    subparsers.add_parser("backup", help="Create a backup snapshot")

    restore_parser = subparsers.add_parser("restore", help="Restore from snapshot")
    restore_parser.add_argument("snapshot", help="Path to .rdb file")

    args = parser.parse_args()

    success = False
    if args.command == "health":
        success = check_health()
    elif args.command == "backup":
        success = backup()
    elif args.command == "restore":
        success = restore(args.snapshot)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
