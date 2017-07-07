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
        errors, error = False, False
        for i in sorted(os.listdir(dir)):
            abs_i = os.path.join(dir,i)
            if os.path.isdir(abs_i):
                error = self.run(os.path.join(dir,i))
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
                error = result.compare(test)
            if error:
                errors = True
        try:
            os.remove(TMP_FILE)
        except OSError:
            pass
        return errors

if __name__ == "__main__":
    if len(sys.argv) > 1:
        errors = Tester().run(sys.argv[1])
    else:
        errors = Tester().run(PATH)
    if errors:
        print("ERROR: There were errors in the tests")
    else:
        print("OK: All tests were correct")
