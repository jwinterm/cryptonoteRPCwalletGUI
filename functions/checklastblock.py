import requests
import json
import time

serverURL = 'http://localhost:8081/json_rpc'

headers = {'content-type': 'application/json'}

payload = json.dumps({
    "jsonrpc": "2.0",
    "id": "test",
    "method": "getlastblockheader"
})


def checklastblockrpccall():
    synced = False
    while synced == False:
        resp = requests.get(serverURL, headers=headers, data=payload)
        output = json.loads(resp.text)
        try:
            output[u'result'][u'status'] == 'OK'
            synced = True
        except:
            time.sleep(2)
            print "Waiting for bitmonerod client to sync with network..."

        try:
            if output[u'error'][u'message'] == 'Core is busy':
                time.sleep(3)
        except:
            print '2nd'


    print "Client is synced with the network."
    print output
    time.sleep(4)

    return output

if __name__ == "__main__":
    checklastblockrpccall()