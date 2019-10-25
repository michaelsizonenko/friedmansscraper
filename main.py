import csv
import subprocess
import sys
import traceback
import json
import base64

ALL_FOUND_TWITTERS = "all found twitters"
MATCH_TWITTER = "match twitter "
ONE_W = "1 WORD MATCH"
ALL_W = "ALL NAME WORDS MATCH"

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            if ALL_FOUND_TWITTERS not in header:
                header.append(ALL_FOUND_TWITTERS)
                for i in xrange(4):
                    header.append(MATCH_TWITTER + str(i+1))
                    header.append(ONE_W)
                    header.append(ALL_W)
            with open("result.csv", 'w') as result_file:
                result_file.write(",".join(header) + "\n")
            for row in reader:
                cmd = ['scrapy', 'crawl', 'twitter', '-a', 'data="'+base64.b64encode(json.dumps(row))+'"']
                print(" ".join(cmd))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                p.wait()
                print(p.returncode)
    except Exception, e:
        traceback.print_exc()
    finally:
        pass
