import os
import subprocess

def bitmonerodloader():
    """Start bitmonerod and/or simplewallet and collect wallet name and address"""
    #Start bitmonerod daemon if not running
    if os.name == 'nt':
        daemonproc = subprocess.Popen("start bitmonerod --rpc-bind-port 18081",
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
    elif os.name == 'posix':
        daemonproc = subprocess.Popen(['./bitmonerod --rpc-bind-port 18081'],
                                      creationflags=subprocess.CREATE_NEW_CONSOLE,
                                      shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
