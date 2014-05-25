import requests
import json

serverURL = 'http://localhost:8082/json_rpc'


def checkbalancerpccall():
    """function to make rpc call to simplewallet to get current balance"""
    payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "getbalance",
    "params": {}
    })
    print 'attempting rpc call'
    try:
        #Make rpc call
        headers = {'content-type': 'application/json'}
        resp = requests.get(serverURL, headers=headers, data=payload)
        output = json.loads(resp.text)

        #Parse json data to get balance info
        rawbalance = str(output[u'result'][u'balance']/1e12)
        rawunlockedbalance = str(output[u'result'][u'unlocked_balance']/1e12)

        #Format data for kivy
        balance = '[color=00ff00]'+rawbalance+'[/color]'
        unlockedbalance = '[color=00ff00]'+rawunlockedbalance+'[/color]'
        return balance, unlockedbalance


    except:
        #Return out of sync if bitmonerod is not ready
        return '[color=ff0000]out of sync[/color]', '[color=ff0000]out of sync[/color]'



if __name__ == "__main__":
    checkbalance()