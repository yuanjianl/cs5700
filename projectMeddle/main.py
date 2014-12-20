import os
import sys

dir = sys.argv[1]

appList = ["google", "facebook", "apple", "icloud", "zhihu", "amazon", "yahoo", "skype", "apple-finance", "gmail", "youtube", "zaker"]

print dir
#for root, dirs, files in os.walk(dir):
#    if not dirs:
#	command = './count_sites.sh ' + dir
#	os.system( command )
#    for d in dirs:
#        # command = './all.sh ' + os.path.join(root, d)
#        command = './count_sites.sh ' + os.path.join(root, d)
#	# command = './count_sited.sh ' + dir
#        # print command
#        os.system(command)
#    break

for root, dirs, files in os.walk(dir):
    for f in files:
        if f.endswith('clr'):
            command = './grepForStuff.sh ' + os.path.join(root, f)
            os.system(command)
