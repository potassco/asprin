#!/usr/bin/python
from __future__ import print_function
import os
import utils
import sys
import subprocess

PATH = os.path.dirname(os.path.realpath(__file__))
STR_TMP = "tester.tmp"
TMP_FILE = os.path.join(PATH, STR_TMP)

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

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
                with open(TMP_FILE, 'w') as tmp:
                    with cd(dir):
                        subprocess.call(test.command, stdout=tmp,
                                        stderr=subprocess.STDOUT, shell=True)
                with open(TMP_FILE, 'r') as tmp:
                    result = utils.Result(tmp.read())
                result.compare(test)
        try:
            os.remove(TMP_FILE)
        except OSError:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        Tester().run(sys.argv[1])
    else:
        Tester().run(PATH)

