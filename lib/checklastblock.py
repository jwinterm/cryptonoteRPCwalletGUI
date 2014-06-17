import requests
import json
import time
import datetime

serverURL = 'http://localhost:18081/json_rpc'

headers = {'content-type': 'application/json'}

payload = json.dumps({
    "jsonrpc": "2.0",
    "id": "test",
    "method": "getlastblockheader"
})


def checklastblock(jobqueue, resultsqueue):
    """Try and get last block info and return formatted text"""
    kivysignal = True
    while kivysignal:
        time.sleep(1)
        daemonrunning, kivysignal = jobqueue.get()
        if daemonrunning:
            try:
                resp = requests.get(serverURL, headers=headers, data=payload)
                output = json.loads(resp.text)
                # print(output)
                reward = output[u'result'][u'block_header'][u'reward']
                linuxblocktime = output[u'result'][u'block_header'][u'timestamp']
                linuxtimenow = time.time()
                timesince = linuxtimenow - linuxblocktime
                localtime = datetime.datetime.fromtimestamp(int(linuxblocktime
                    )).strftime('%Y-%m-%d %H:%M:%S')

                blocktext = "Last block height: [color=00ffff]{0}[/color]".format(
                    output[u'result'][u'block_header'][u'height'])
                rewardtext = "Last block reward: [color=00ffff]{0:2.2f}[/color] XMR".format(float(reward)/1e12)
                timetext = "Last block time: [color=00ffff]{0}[/color]".format(localtime)
                timesincetext = "Time since last block: [color=00ffff]{0:4.2f} s[/color]".format(timesince)
                difftext = "Difficulty: [color=00ffff]{0}[/color]".format(
                    output[u'result'][u'block_header'][u'difficulty'])
                orphantext = "Orphan status: [color=00ffff]{0}[/color]".format(
                    output[u'result'][u'block_header'][u'orphan_status'])

            except:
                blocktext = "Last block height: Not connected to daemon..."
                rewardtext = "Last block reward: Not connected to daemon..."
                timetext = "Last block time: Not connected to daemon..."
                timesincetext = "Time since last block: Not connected to daemon..."
                difftext = "Difficulty: Not connected to daemon..."
                orphantext = "Orphan status: connected to daemon..."

            daemoninfo_labeltext = "[b]Last block info:[/b]\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(
                blocktext, rewardtext, timetext, timesincetext, difftext, orphantext)
            resultsqueue.put(daemoninfo_labeltext)
