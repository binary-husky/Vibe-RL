---
name: monitor-with-tmux
description: Monitor training progress by reading tmux content at exponential backoff intervals (30s, 1min, 2min, 4min, 8min...), analyze logs when anomalies occur, and provide fix suggestions
license: Complete terms in LICENSE.txt
---

# Monitor with Tmux

Monitor in tmux, detect anomalies, analyze errors, provide fix suggestions.

## Step Zero

Create a sleep script for tmux monitoring:

1. create `./tmp/wait_tmux.py`

```python
import argparse
import subprocess
import time

SHELLS = {"bash", "zsh", "sh", "fish", "csh", "tcsh", "ksh", "dash", "ash"}

def smart_sleep(session: str, seconds: float, check_every: float = 2.0) -> bool:
    """
    替代 time.sleep()，但在命令结束时提前返回。

    Returns:
        True  - 正常超时（命令还在跑）
        False - 提前返回（命令结束了或session没了）
    """
    end_time = time.time() + seconds
    while time.time() < end_time:
        try:
            r = subprocess.run(
                ["tmux", "list-panes", "-F", "#{pane_current_command}", "-t", session],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode != 0:
                return False  # session没了
            cmds = [l.strip().lower() for l in r.stdout.splitlines() if l.strip()]
            if not any(c not in SHELLS for c in cmds):
                return False  # 命令结束了，回到shell
        except Exception:
            return False

        time.sleep(min(check_every, end_time - time.time()))

    return True


def main():
    parser = argparse.ArgumentParser(description="Wait for a tmux session with smart early-exit.")
    parser.add_argument("session", help="tmux session name")
    parser.add_argument("seconds", type=float, help="total seconds to wait")
    args = parser.parse_args()

    timed_out = smart_sleep(args.session, args.seconds, 2)
    raise SystemExit(0 if timed_out else 1)


if __name__ == "__main__":
    main()
```

## Begin Monitor

当你需要监控一个tmux窗口时，运行：

```bash
python ./tmp/tmux_wait.py my_session_name 30
```

意思是：
1. 监控名字为 my_session_name 的tmux session
2. 等待30秒

- 退出码 0：正常超时（命令仍在运行）
- 退出码 1：命令提前结束或 session 消失

## Working with ssh

when working with ssh, always use a local tmux window to set up ssh connection

## When you want to delay a while before reading tmux window again

必须要具备出错即时返回功能，即不能使用 `sleep xxx`，而是使用 `python ./tmux_wait.py my_session_name xxx`

DO NOT USE: `sleep 60 && tmux capture-pane -t my_session_name -p | tail -80`

YOU SHOULD USE: `python ./tmux_wait.py my_session_name 30 && tmux capture-pane -t my_session_name -p | tail -80`

- 60 seconds is too long
- always use `python ./tmux_wait.py` to wait




## Example:


### without ssh example

0 example available


### with ssh example

1 example available

```agent

--- example user instruction begin ---
login
ssh root@localhost -p 8824
goto
/mnt/data_cpfs/qingxu.fu/agentjet/good-luck-agentjet
run with venv and monitor
source .venv/bin/activate && python -m ajet.launcher --conf tests/bench/benchmark_math/benchmark_math.yaml --autokill
--- example user instruction end ---

--- example agent reaction begin ---
The user wants me to monitor a tmux session while running a training job. Let me break down what they're asking:
1. SSH into a remote machine (root@localhost -p 8824)
2. Go to a specific directory
3. Activate a virtual environment and run a Python command
4. Monitor the tmux session

# Wrote ./tmp/tmux_wait.py
....

# Create tmux session for training
$ tmux new-session -d -s agentjet -c "/mnt/data_cpfs/qingxu.fu/agentjet/good-luck-agentjet"
...

# Send SSH command to tmux session
$ tmux send-keys -t agentjet "ssh root@localhost -p 8824" Enter
...

# Wait and check SSH connection
$ python3 /tmp/tmux_wait.py agentjet 10 && tmux capture-pane -t agentjet -p | tail -20
SSH connected successfully. Now I need to navigate to the directory and run the training command. Let me send the commands to the tmux session.
...

# Navigate to working directory
$ tmux send-keys -t agentjet "cd /mnt/data_cpfs/qingxu.fu/agentjet/good-luck-agentjet" Enter
...

# Start training with venv and launcher
$ tmux send-keys -t agentjet "source .venv/bin/activate && python -m ajet.launcher --conf tests/bench/benchmark_math/benchmark_math.yaml --autokill" Enter
...

# Capture initial training output
$ tmux capture-pane -t agentjet -p | tail -40
...

# Wait 30s and check training progress
$ python3 /tmp/tmux_wait.py agentjet 30 && tmux capture-pane -t agentjet -p | tail -50
...
Training is running. The command is executing properly. Let me continue monitoring at 1 minute intervals.

# Wait 1min and check training progress
$ python3 /tmp/tmux_wait.py agentjet 60 && tmux capture-pane -t agentjet -p | tail -50
...

# Wait 2min and check training progress
$ python3 /tmp/tmux_wait.py agentjet 120 && tmux capture-pane -t agentjet -p | tail -60
...
Training is progressing well. Checkpoints loaded, vLLM server started, swanlab is tracking the run. No errors so far, just warnings. Let me continue monitoring.

# Wait 4min and check training progress
$ python3 /tmp/tmux_wait.py agentjet 240 && tmux capture-pane -t agentjet -p | tail -60
...

... many other rounds ...

--- example agent reaction end ---

```