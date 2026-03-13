"""替代 sleep，在超时或命令结束时返回"""

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
