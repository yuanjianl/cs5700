md5sum 2MB.log
md5sum 2MB.log.1

cmp 2MB.log 2MB.log.1

od -x 2MB.log > 2MB.log.hex
od -x 2MB.log.1 > 2MB.log.1.hex
