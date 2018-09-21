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
import sys
import subprocess
from . import utils

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
    ["--approximation=heuristic"],
    ["--approximation=heuristic --const-nb heuristic_aso=2"],
    ["--approximation=heuristic --const-nb heuristic_aso=2 --const-nb use_get_sequence=2 "],
    ["""--approximation=heuristic --const-nb heuristic_poset=2 --const-nb heuristic_aso=3 \
     --const-nb heuristic_pareto=2 --const-nb heuristic_and=2"""],
    ["--approximation=weak"],
    ["--approximation=weak --const-nb approx_aso=2"],
    ["--approximation=weak --const-nb approx_aso=2 --const-nb use_get_sequence=2 "],
    ["""--approximation=weak --const-nb approx_poset=2 --const-nb approx_aso=3 \
     --const-nb approx_pareto=2 --const-nb approx_and=2"""],
    ["--improve-limit=0,5"],
    ["--improve-limit=1,all,100"],
    ["--on-opt-heur=+,p,-1,sign --on-opt-heur=-,p,1,sign"],
    ["--on-opt-heur=+,s,1,true --on-opt-heur=-,s,1,false"],
    ["--meta=simple"],
    ["--meta=simple,bin"],
    ["--meta=combine"],
    ["--meta=combine,bin"],
]

EXCLUDE = {}

EXCLUDE["--on-opt-heur=+,p,-1,sign --on-opt-heur=-,p,1,sign"] = [
    os.path.join(PATH, "program_parser/basic/test001.lp"), # uses --approximation=heuristic
    os.path.join(PATH, "program_parser/basic/test002.lp"), # uses --approximation=heuristic
]

EXCLUDE["--meta=simple"] = [
    os.path.join(PATH, "asprin_lib/test022.lp"), # too hard
    os.path.join(PATH, "asprin_lib/test023.lp"), # too hard
    os.path.join(PATH, "asprin_lib/test024.lp"), # too hard
    os.path.join(PATH, "asprin_lib/test025.lp"), # too hard
    os.path.join(PATH, "solver/solver/test008.lp"), # too hard
    os.path.join(PATH, "solver/solver/test009.lp"), # too hard
    os.path.join(PATH, "program_parser/visitor/test002.lp"), # no error with --meta
]
EXCLUDE[ "--meta=simple,bin"] = EXCLUDE["--meta=simple"]
EXCLUDE[    "--meta=combine"] = EXCLUDE["--meta=simple"]
EXCLUDE["--meta=combine,bin"] = EXCLUDE["--meta=simple"]

EXCLUDE["--preference-unsat $asprin/mine/asprin_lib_unsat.lp"] = [
    os.path.join(PATH, "solver/solver/test002.lp"),           # adds new preference programs
    os.path.join(PATH, "program_parser/visitor/test002.lp"),  # adds new preference programs
    os.path.join(PATH, "spec_parser/spec_lexer/test005.lp"),  # adds new preference programs
    os.path.join(PATH, "spec_parser/spec_parser/test026.lp"), # adds new preference programs
]

add_option = False
# to add one option to all OPTIONS, uncomment the next line and set option below
#add_option = True
option = "--preference-unsat $asprin/mine/asprin_lib_unsat.lp"
#
option_exclude = EXCLUDE[option]
if add_option:
    for i in OPTIONS:
        if i == option:
            continue
        if i[0] in EXCLUDE:
            EXCLUDE[i[0] + " " + option] = option_exclude + EXCLUDE[i[0]]
        else:
            EXCLUDE[i[0] + " " + option] = option_exclude
        i[0] += " " + option

# uncomment to only test --preference-unsat
#OPTIONS = [["--preference-unsat $asprin/mine/asprin_lib_unsat.lp"]]

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

    def exclude(self, options, _file):
        try:
            if _file in EXCLUDE[" ".join(options)]:
                return True
        except:
            pass
        return False

    def run(self, dir, options):
        errors, error = False, False
        for i in sorted(os.listdir(dir)):
            abs_i = os.path.join(dir,i)
            if self.exclude(options, abs_i):
                continue
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
                    output = tmp.read()
                    if isinstance(output, bytes):
                        output = output.decode()
                    result = utils.Result(output)
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
    global_errors = []
    for opt in options:
        print("Options = {}".format(opt))
        errors = Tester().run(path, opt)
        if errors:
            print("ERROR: There were errors in the tests")
            global_errors.append(str(opt))
        else:
            print("OK: All tests were successful")
    if len(options) <= 1:
        return
    if global_errors:
        e = " ".join(global_errors)
        print("\nSUMMARY: There were errors with options: {}".format(e))
    else:
        print("\nSUMMARY: There were no errors.")

if __name__ == "__main__":
    main()

