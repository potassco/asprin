#!/usr/bin/python
from __future__ import print_function
import os
import utils
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
STR_TMP = "_tester.tmp"
TMP_FILE = os.path.join(PATH, STR_TMP)
CALL = "cd {}; {} > {} 2> {}"

class Tester:
    
    def run(self, dir):
        for i in sorted(os.listdir(dir)):
            abs_i = os.path.join(dir,i)
            if os.path.isdir(abs_i):
                self.run(os.path.join(dir,i))
            elif str(abs_i)[-3:] == ".lp":
                with open(abs_i, 'r') as f:
                    test = utils.Test(f.read())
                print("Testing {}...".format(abs_i))
                call = CALL.format(dir, test.command, TMP_FILE, TMP_FILE)
                os.system(call)
                with open(TMP_FILE, 'r') as tmp:
                    result = utils.Result(tmp.read())
                result.compare(test)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        Tester().run(sys.argv[1])
    else:
        Tester().run(PATH)

