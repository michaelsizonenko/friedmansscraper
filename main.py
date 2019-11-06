import csv
import subprocess
import sys
import traceback
import json
import base64
import os

ALL_FOUND_TWITTERS = "all found twitters"
MATCH_TWITTER = "match twitter "
ONE_W = "1 WORD MATCH"
ALL_W = "ALL NAME WORDS MATCH"

CONFIG_FILE = "config.json"
CONFIG_PARAMS = {
    "depth",
    "name_index",
    "input_file",
    "output_file",
    "start_from",
    "continue_processing",
    "process_until"
}

if __name__ == "__main__":
    try:
        assert os.path.exists(CONFIG_FILE), "This is weird! Config file does not exists"
        with open(CONFIG_FILE) as config_file:
            config = json.load(config_file)
        assert set([x.encode('utf-8') for x in config.keys()]).issubset(
            CONFIG_PARAMS), "This is weird! Config file contains unexpected params"
        assert set([x.encode('utf-8') for x in config.keys()]).issuperset(
            CONFIG_PARAMS), "This is weird! Config file contains not enough params"
        assert os.path.exists(config["input_file"]), "This is weird! The input file does not exists"
        filename = config["input_file"]
        result_filename = config["output_file"]
        start_from = config["start_from"]
        process_until = config["process_until"]
        continue_processing = config["continue_processing"]
        if len(sys.argv) > 2:
            start_from = int(sys.argv[2])
        print("start from {}".format(start_from))
        if len(sys.argv) > 3:
            process_until = int(sys.argv[3])
        print("end with {}".format(process_until))
        assert start_from < process_until, "Are you serious ?"
        if len(sys.argv) > 4:
            print(sys.argv[4])
            continue_processing = bool(sys.argv[4])
            print(continue_processing)
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
                    header.append(MATCH_TWITTER + str(i + 1))
                    header.append(ONE_W)
                    header.append(ALL_W)
            if not (os.path.isfile(result_filename) and continue_processing):
                with open(result_filename, 'w') as result_file:
                    result_file.write(",".join(header) + "\n")
            counter = 0
            for row in reader:
                counter += 1
                print(counter, start_from)
                print(row)
                if start_from > counter:
                    continue
                if counter > process_until:
                    continue
                cmd = [
                    'scrapy', 'crawl', 'twitter',
                    '-a', 'index={}'.format(index),
                    '-a', 'data="' + base64.b64encode(json.dumps(row)) + '"',
                    '-a', 'depth=' + str(config["depth"]),
                    '-a', 'name_index=' + str(config["name_index"]),
                    '-a', 'result_filename=' + result_filename
                ]
                print(" ".join(cmd))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                p.wait()
                print(p.returncode)
    except Exception, e:
        traceback.print_exc()
    finally:
        pass
