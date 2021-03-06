####README for [ProjectMeddle](http://david.choffnes.com/classes/cs4700fa14/projectMeddle.php)####

Part 1:
How I did the analysis:
  To identify the sites that have been visited by my phone, I first filtered the traffic by only parsing the DNS traffic, then wrote the result into a file. After that, I developed an appList that contains my frequently used apps. At last I used a 'grep' command to count the keywords of each app in the previous generated filtered file.

  There are some potential drawbacks of this method:
	1. Some apps may use multiple host for its contents. For example, zhihu.com uses pic.zhimg.com for images. It is hard to calculate these traffic for that specific app name.
	2. It is possible that different apps accessing the same domain. For example, a lot of games may contact icloud.com for their data.

Question 1:

First, I used a script to gather the information of dns request.

======================================
	#!/bin/bash
	directoryname="$1"
	
	rm -r $1/output
	
	mkdir $1/output
	
	for file in $directoryname/*.clr;
	do
	        echo $file >> $1/output/dnsCount.txt
	        tcpdump -vv -tnr $file | grep 'q: A?' | while read LINE; do echo "$LINE" | grep -P -o '(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])\.' | sort | uniq; echo "$LINE" | grep -P -o 'A \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq; done >> $1/output/dnsCount.txt
	done;
======================================
After I have gathered all dns request, I used this python script to count the sites of my frequently used apps.

======================================
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
=======================================
Here is a list of my frequently used apps, and the many of sites they have visited:

google 5455
facebook 3845
apple 12359
icloud 1068
zhihu 1145
amazon 892
yahoo 2685
skype 4328
apple-finance(stock) 169
gmail 942
youtube 2
zaker 759
instagram 0
expedia 0
boa 2
chase 2
bestbuy 7
linkedin 703
baidu 31
qq 291
wechat 45
whatsapp 0
douban 1229
wikipedia 0

Question 2:
There is some apps frequently sending out location information, for example the zillow app. I do remember that I have granted the permission of accessing gps for zillow, but I don't think I have been using it a lot during these days. It is possible that zillow is "stealing" the gps location.

Question 3:
The most surprising part is that most traffic are fairly small. I thought that to minimum the effect of overhead ( headers, three-way-handshake ), the traffic should be as big as possible. It seems that most apps are using parrellel request to decrease the response delay.

Part 2:
First I modified the grepForStuff.sh script with my creditial information such as username, devide name, IMEI number, phone number, email address, frequently used passwords and so on. 

Then I wrote a python script to iterate all the generated tcpdump files to grep the needed information. 

=============================================
	for root, dirs, files in os.walk(dir):
	    for f in files:
	        if f.endswith('clr'):
	            command = './grepForStuff.sh ' + os.path.join(root, f)
	            os.system(command)
=============================================
Then I found it took a long time to analyze even a very small trace file, so I used the screen command to leave the process running while I am logging off, and dump the outputs to result.txt.
============================================
	screen -s meddle
	python main.py ./ > result.txt
============================================
Finally, after a couple of hours, I obtained the result and search for any leaked information.

I found one PII leak of a game called ShapeJam. The app would send out Username, Device Name and Device vendor_uuid to its own server( I am not ure about this actually, I used whois command but only find it is under Joyent, Inc. I would assume that the app is running in this infrastructure )

Here is the detail of the leak ( I have already posted it to piazza though ):
Flow: 
02:22:38.202154 IP ip-10-11-1-6.ec2.internal.61541 > 165.225.130.241.http: Flags [P.],
seq 1:467, ack 1, win 4106, options [nop,nop,TS val 512383276 ecr 1093876549], length
466
E...#8@.?...
........e.P....^0.....
.......
..Y,A3;EPOST /api/5967/store/ HTTP/1.1
Host: toledo-errors.jit.su
Expect:
Accept: application/json
Content-Type: application/json
Accept-Language: en;q=1, zh-Hans;q=0.9
Accept-Encoding: gzip, deflate
Content-Length: 922
Connection: keep-alive
X-Sentry-Auth: Sentry sentry_version=4, sentry_client=shapejam/1332, sentry_key=b9ca99
9f27af47ad9bb191c2d1d62ea1, sentry_secret=9e52b687fb8d48abbdcf9b13694aefed
User-Agent: ShapeJam/1332 (iPhone; iOS 8.1; Scale/2.00)

02:22:38.202161 IP ip-10-11-1-6.ec2.internal.61541 > 165.225.130.241.http: Flags [P.],
seq 467:1389, ack 1, win 4106, options [nop,nop,TS val 512383276 ecr 1093876549], len
gth 922
E...u.@.?...
........e.P...p^0.....
.......
..Y,A3;E{"event_id":"08e36c4c7afe41f78774e47a954c2dfc","timestamp":"2014-11-19T02:22:3
6","level":"error","message":"Error: Invalid products: (\n premium\n)","platform":"
javascript","sha1":"8d929d11321c4140fc1d446fc7c02b85b8ddd1c6","exception":{"type":"Err
or","value":"Invalid products: (\n premium\n)","stacktrace":{"frames":[{"function":
"","filename":"upgrade.js","abs_path":"upgrade.js","lineno":"111"},{"function":"","fil
ename":"q.js","abs_path":"q.js","lineno":"547"},{"function":"when","filename":"q.js","
abs_path":"q.js","lineno":"842"},{"function":"","filename":"utils.js","abs_path":"util
s.js","lineno":"1008"},{"function":"","filename":"utils.js","abs_path":"utils.js","lin
eno":"975"}]}},"user":{"username":"(xxxxxx)"},"tags":{"app_version":"1.33","build_numb
er":"1332","vendor_uuid":"xxxxxxx","platform":"ios","syst
em_version":"iOS 8.1","device_name":"xxxxxx","device_model":"iPhone"}}
02:22:38.204291 IP 165.225.130.241.http > ip-10-11-1-6.ec2.internal.61541: Flags [.],
ack 467, win 32772, options [nop,nop,TS val 1093876601 ecr 512383276], length 0
 
 
tcpdump -Ar /opt/meddle/decrypt-data/pcap-decrypted/mi.z/2014-Nov-19/tcpdump-mi.z-Nov-19-2014-02-19-1416363581-172.31.45.70-10.11.1.6-107.107.63.178.pcap.enc.clr | grep "<username>"

For this PII leak, I guess ShapeJam would gather this information for
user statastics analysis. 

