import os
import time
import subprocess

import checklastblock

def simplewalletloader(walletname, walletpw, queue):
    """Function to create and/or open wallet in simplewallet rpc mode"""

    #Generate wallet if file doesn't exist in local directory
    if not os.path.isfile('./'+walletname):
        print "Generating wallet file " + walletname
        if os.name == 'nt':
            walletgen = subprocess.Popen(
                "simplewallet --generate-new-wallet " + walletname + " --password " + walletpw,
                shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elif os.name == 'posix':
            walletgen = subprocess.Popen(
                "./simplewallet --generate-new-wallet " + walletname + " --password " + walletpw,
                shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_CONSOLE)

        time.sleep(7)
        walletgen.terminate()

    #Launch simplewallet in rpc mode
    print "***Opening ___" + walletname + "___ wallet file rpc interface***"
    if os.name == 'nt':
        walletproc = subprocess.Popen("start simplewallet --wallet {0} --password {1} --rpc-bind-port 8082".format(walletname, walletpw),
            shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    elif os.name == 'posix':
        walletproc = subprocess.Popen(["./simplewallet --wallet {0} --password {1} --rpc-bind-port 8082".format(
            walletname, walletpw)], creationflags=subprocess.CREATE_NEW_CONSOLE)

    #Read address file to get address
    with open(walletname + ".address.txt", "r") as addressfile:
        rawaddress = addressfile.read().replace('\n', '')

    #Format data for display in kivy
    walletname = walletname + ' wallet file has been opened'
    address = '[color=00ffff][ref=addressselection]' + rawaddress + '[/ref][/color]'

    queue.put((walletname, address, rawaddress))