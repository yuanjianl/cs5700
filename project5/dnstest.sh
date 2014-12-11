#!/bin/bash
for (( i=1; i<=50; i++ ))
do
	echo "Welcome $i times"

	resp="$(dig @cs5700cdnproject.ccs.neu.edu -p 49384 -n cs5700cdn.example.com)"
	echo "${resp}"

	destdir=dns.txt
	echo "$resp" >> "$destdir"

	ip="$(grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' dns.txt | head -1)"
	echo "**********************${ip}*****************************"
	wget http://$ip:49384/wiki/Special:Random
done

