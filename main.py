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
        start_from = 0
        end_with = 100000
        continue_parsing = False
        if len(sys.argv) > 2:
            start_from = int(sys.argv[2])
        print("start from {}".format(start_from))
        if len(sys.argv) > 3:
            end_with = int(sys.argv[3])
        print("end with {}".format(end_with))
        assert start_from < end_with, "Are you serious ?"
        if len(sys.argv) > 4:
            print(sys.argv[4])
            continue_parsing = bool(sys.argv[4])
            print(continue_parsing)
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            index = len(header)
            if ALL_FOUND_TWITTERS not in header:
                header.append("")
                header.append("")
                index = len(header)
                header.append(ALL_FOUND_TWITTERS)
                for i in xrange(4):
                    header.append(MATCH_TWITTER + str(i+1))
                    header.append(ONE_W)
                    header.append(ALL_W)
            if not continue_parsing:
                with open("result.csv", 'w') as result_file:
                    result_file.write(",".join(header) + "\n")
            counter = 0
            for row in reader:
                counter += 1
                print(counter)
                print(start_from)
                if start_from > counter:
                    continue
                if counter > end_with:
                    continue
                cmd = ['scrapy', 'crawl', 'twitter', '-a', 'index={}'.format(index), '-a',
                       'data="'+base64.b64encode(json.dumps(row))+'"']
                print(" ".join(cmd))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                p.wait()
                print(p.returncode)
    except Exception, e:
        traceback.print_exc()
    finally:
        pass
