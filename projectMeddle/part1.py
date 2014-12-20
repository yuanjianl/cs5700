import os
import sys

import subprocess

dir = sys.argv[1]

appList = ["google", "facebook", "apple", "icloud", "zhihu", "amazon", "yahoo", "skype", "apple-finance", "gmail", "youtube", "zaker", "instagram", "expedia", "boa", "chase", "bestbuy", "linkedin", "baidu", "qq", "wechat", "whatsapp", "douban", "wikipedia"]

result = {}

for app in appList:
    count = 0
    for root, dirs, files in os.walk(dir):
        for d in dirs:
            if d.find( "output" ) != -1:
                continue

            command = "grep -c " + app + " " + os.path.join(root, d) + '/output/dnsCount.txt'

            outputs = os.popen( command ).read()
            count += int(outputs[: -1])

    
    print app + " " + str( count )

