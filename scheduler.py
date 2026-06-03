#!/usr/bin/env python3
"""
笔记整理定时调度器
常驻后台运行，每天凌晨 1 点自动执行 organize.py

用法:
  python scheduler.py          # 前台运行（可看到日志）
  nohup python scheduler.py &  # 后台运行
"""

import subprocess
import sys
import time
import os
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).parent
LOG_FILE = VAULT_ROOT / "90-System" / "organize.log"
LOCK_FILE = VAULT_ROOT / "90-System" / "organize.lock"
SCHEDULE_HOUR = 1  # 凌晨 1 点执行
TASK_TIMEOUT_SECONDS = 60 * 60


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def acquire_lock():
    if LOCK_FILE.exists():
        age = time.time() - LOCK_FILE.stat().st_mtime
        if age < TASK_TIMEOUT_SECONDS:
            log("定时整理任务跳过：已有整理任务在运行")
            return False
        log("发现过期锁文件，自动清理")
        LOCK_FILE.unlink(missing_ok=True)

    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        log("定时整理任务跳过：锁文件已被其他进程创建")
        return False

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(str(datetime.now()))
    return True


def run_organize():
    if not acquire_lock():
        return

    log("定时整理任务开始")
    try:
        result = subprocess.run(
            [sys.executable, str(VAULT_ROOT / "organize.py"), "--auto"],
            capture_output=True,
            text=True,
            cwd=str(VAULT_ROOT),
            timeout=TASK_TIMEOUT_SECONDS,
        )
        log(result.stdout.strip())
        if result.stderr:
            log(f"STDERR: {result.stderr.strip()}")
        log(f"定时整理任务结束 (exit={result.returncode})")
    except subprocess.TimeoutExpired:
        log(f"定时整理任务超时，已终止 (timeout={TASK_TIMEOUT_SECONDS}s)")
    except Exception as e:
        log(f"执行出错: {e}")
    finally:
        LOCK_FILE.unlink(missing_ok=True)


def main():
    log(f"调度器启动，每天 {SCHEDULE_HOUR}:00 执行整理")
    last_run_date = None

    while True:
        now = datetime.now()
        today = now.date()

        if now.hour == SCHEDULE_HOUR and last_run_date != today:
            run_organize()
            last_run_date = today

        time.sleep(30)  # 每 30 秒检查一次


if __name__ == "__main__":
    main()
