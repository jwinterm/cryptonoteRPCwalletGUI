import subprocess
from sys import platform
import os

def bitmonerodloader():
    """Start bitmonerod and/or simplewallet and collect wallet name and address"""
    print "Start daemon button pressed..."
    #Start bitmonerod daemon if not running
    if platform == 'win32':
        daemonproc = subprocess.Popen("start bitmonerod.exe --rpc-bind-port 18081 --log-level 0",
                                      shell=True)
    elif platform == 'linux' or platform == 'linux2' or platform == 'linux32':
        # print "linux!"
        daemonproc = subprocess.Popen('xterm -bg black -e "./bitmonerod --rpc-bind-port 18081 --log-level 0"',
                                      shell=True)

