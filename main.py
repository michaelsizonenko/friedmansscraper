import csv
import subprocess
import sys
import traceback
import json
import base64

ALL_FOUND_TWITTERS = "all found twitters"

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            if ALL_FOUND_TWITTERS not in header:
                header.append(ALL_FOUND_TWITTERS)
            result_index = header.index(ALL_FOUND_TWITTERS)
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
