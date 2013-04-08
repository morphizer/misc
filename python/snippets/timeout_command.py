#!/usr/bin/env python
import sys, signal, subprocess, datetime, os, time

def timeout_command(command, timeout):
    """call shell-command and either return <something> or if the
    command times out return <something else>"""
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return

timeout_command(["sleep","5"], 2)
timeout_command(["sleep","1"], 2)
