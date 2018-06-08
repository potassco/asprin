# MIT License
# 
# Copyright (c) 2017 Javier Romero
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -*- coding: utf-8 -*-

#!/usr/bin/python
from __future__ import print_function
import os
import utils
import sys
import subprocess

PATH = os.path.dirname(os.path.realpath(__file__))
DIR = "--test-dir="
ALL = "--all"
OPTIONS = [
    [""],
    ["--delete-better"],
    ["--ground-once"],
    ["--release-last"],
    ["--no-opt-improving"],
    ["--volatile-improving"],
    ["--volatile-optimal"],
    #["--preference-unsat $asprin/mine/asprin_lib_unsat.lp"],
    #["--approximation=heuristic"],
    #["--approximation=heuristic --const-nb heuristic_aso=2"],
    #["--approximation=heuristic --const-nb heuristic_aso=2 --const-nb use_get_sequence=2 "],
    #["""--approximation=heuristic --const-nb heuristic_poset=2 --const-nb heuristic_aso=3 \
    # --const-nb heuristic_pareto=2 --const-nb heuristic_and=2"""],
    ["--approximation=weak"],
    ["--approximation=weak --const-nb approx_aso=2"],
    ["--approximation=weak --const-nb approx_aso=2 --const-nb use_get_sequence=2 "],
    ["""--approximation=weak --const-nb approx_poset=2 --const-nb approx_aso=3 \
     --const-nb approx_pareto=2 --const-nb approx_and=2"""],
    ["--improve-limit=0,10"],
    ["--improve-limit=1,all,10,reprint"],
]

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
    
    def run(self, dir, options):
        errors, error = False, False
        for i in sorted(os.listdir(dir)):
            abs_i = os.path.join(dir,i)
            if os.path.isdir(abs_i):
                error = self.run(os.path.join(dir, i), options)
            elif str(abs_i)[-3:] == ".lp":
                with open(abs_i, 'r') as f:
                    test = utils.Test(f.read(), options)
                print("Testing {}...".format(abs_i))
                import tempfile
                tmp = tempfile.TemporaryFile()
                with cd(dir):
                    subprocess.call(test.command, stdout=tmp,
                                    stderr=subprocess.STDOUT, shell=True)
                    tmp.seek(0)
                    result = utils.Result(tmp.read())
                error = result.compare(test)
            if error:
                errors = True
        return errors

def main(args):
    path = PATH
    for i in args:
        if i.startswith(DIR):
            path = i[len(DIR):]
            args.remove(i)
            break
    if ALL in args:
        options = OPTIONS
    else:
        options = [args]
    for opt in options:
        print("Options = {}".format(opt))
        errors = Tester().run(path, opt)
        if errors:
            print("ERROR: There were errors in the tests")
        else:
            print("OK: All tests were successful")

if __name__ == "__main__":
    main()

