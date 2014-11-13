#!/bin/sh
#for i in 2MB 10MB; do
for i in 2MB 10MB 50MB; do	
	sudo python rawhttpget.py http://david.choffnes.com/classes/cs4700fa14/$i.log
	wget http://david.choffnes.com/classes/cs4700fa14/$i.log
	file1="$i.log"
	file2="$i.log.1"
	md5sum $file1
	md5sum $file2
	
	if [ "$md5_1" != "$md5_2" ]; then
		cmp $file1 $file2
		
		od -x $file1 > "$file1.hex"
		od -x $file2 > "$file2.hex"
	fi
done
