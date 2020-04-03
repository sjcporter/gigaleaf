from typing import List, Optional, Dict
import subprocess


def call_subprocess(cmd_tokens: List[str], cwd: str, check: bool = True,
                    shell: bool = False, env: Optional[Dict[str, str]] = None) -> str:
    """Execute a subprocess call and properly benchmark and log

    Args:
        cmd_tokens: List of command tokens, e.g., ['ls', '-la']
        cwd: Current working directory
        check: Raise exception if command fails
        shell: Run as shell command (not recommended)
        env: environment variables to pass to the subprocess

    Returns:
        Decoded stdout of called process after completing

    Raises:
        subprocess.CalledProcessError
    """
    try:
        r = subprocess.run(cmd_tokens, cwd=cwd, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                           check=check, shell=shell, env=env)
    except subprocess.CalledProcessError as err:
        raise IOError(f"An error occurred in a subprocess call:\ncmd: {' '.join(cmd_tokens)}\ncode: {err.returncode}\n"
                      f"output: {err.stdout} \nerror: {err.stderr}")

    return (r.stdout or b"").decode()


