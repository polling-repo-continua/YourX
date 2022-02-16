
BLUE='\033[94m'
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CLEAR='\x1b[0m'

import sys, optparse
from os_urlpattern.formatter import pformat
from os_urlpattern.pattern_maker import PatternMaker
from os_urlpattern.pattern_matcher import PatternMatcher
import concurrent.futures
import re

print(BLUE + "YourX[1.0] by ARPSyndicate" + CLEAR)
print(YELLOW + "url clusterer" + CLEAR)

if len(sys.argv)<2:
	print(RED + "[!] ./YourX --help" + CLEAR)
	sys.exit()

else:
    parser = optparse.OptionParser()
    parser.add_option('-l', '--list', action="store", dest="list", help="list of url to cluster")
    parser.add_option('-o', '--output', action="store", dest="output", help="output file")
    parser.add_option('-t', '--threads', action="store", dest="threads", help="maximum threads [default=20]", default=20)
	
inputs,args  = parser.parse_args()
if not inputs.list:
	parser.error(RED + "[!] input not given" + CLEAR)

ilist = str(inputs.list)
output = str(inputs.output)
threads = int(inputs.threads)

pattern_maker = PatternMaker()
pattern_matcher = PatternMatcher()
with open(ilist) as f:
	urls=f.read().splitlines()
urls = [item.strip("&/") for item in urls]

iunm = []

def genp(url):
    global iunm
    try:
        pattern_maker.load(url)
    except:
        iunm.append(url)

with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
	try:
		executor.map(genp, urls)
	except(KeyboardInterrupt, SystemExit):
		print(RED + "[!] interrupted" + CLEAR)
		executor.shutdown(wait=False)
		sys.exit()



enumex = []
for url_meta, clustered in pattern_maker.make():
    for pattern in pformat('pattern', url_meta, clustered):
        enumex.append(pattern)
for i in range(0,len(enumex)):
    pattern_matcher.load(enumex[i], meta=i)


mdata = {}

def match_all(url):
    global mdata, iunm
    try:
        matched_results = pattern_matcher.match(url)
        sorted(matched_results, reverse=True)[0]
        patterns = [(n.meta) for n in matched_results][0]
        try:
            mdata[patterns].append(url)
        except:
            mdata[patterns] = [url]
    except:
        iunm.append(url)

with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
	try:
		executor.map(match_all, urls)
	except(KeyboardInterrupt, SystemExit):
		print(RED + "[!] interrupted" + CLEAR)
		executor.shutdown(wait=False)
		sys.exit()

iunm = list(set(iunm))
iunm.sort()
for url in iunm:
    urls.remove(url)

result = []


for kdi in mdata.keys():
    for data in mdata[kdi]:
        print(("{2} [{0}] {3} {1}".format(enumex[kdi], data, BLUE, CLEAR)))
        result.append("[{0}] {1}".format(enumex[kdi], data))

eunm = []
inumex = []
for i in range(0,len(enumex)):
    if i not in mdata.keys():
        inumex.append(enumex[i])

def match_rem(d):
    global eunm, inumex, result
    for i in inumex:
        z = re.search(i,d)
        if z:
            print(("{2} [{0}] {3} {1}".format(i, d, BLUE, CLEAR)))
            eunm.append(d)
            result.append("[{0}] {1}".format(i,d))
            break
with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
	try:
		executor.map(match_rem, iunm)
	except(KeyboardInterrupt, SystemExit):
		print(RED + "[!] interrupted" + CLEAR)
		executor.shutdown(wait=False)
		sys.exit()

eunm = list(set(eunm))
for e in eunm:
    iunm.remove(e)

for data in iunm:
    print(("{1} [UNCLUSTERED] {2} {0}".format(data, BLUE, CLEAR)))
    result.append("[UNCLUSTERED] {0}".format(data))


if inputs.output:
	result.sort()
	with open(output, 'w') as f:
		f.writelines("%s\n" % line for line in result)
print(YELLOW + "done"+ CLEAR)