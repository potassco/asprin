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

from __future__ import print_function
import os
import re
import sys

PYTHON = sys.executable
ASPRIN = PYTHON + " " + str(os.path.join(os.path.dirname(os.path.realpath(
                            __file__)),"..","..","asprin.py")) + " "

class Test:

    def __init__(self, string, options):
        self.command = None
        self.satisfiable = False
        self.unsatisfiable = False
        self.error = False
        self.answers = None
        self.parse(string, options)
        self.string = string

    def parse(self, string, options):
        line, last = 1, ""
        self.answers = [] 
        for i in string.splitlines():
            if line == 1:
                self.command = i[1:]
                self.command = self.command.replace('asprin',
                                                    ASPRIN+' '.join(options),1)
            elif line == 2:
                match = re.match(r'%( )*SATISFIABLE', i)
                self.satisfiable = True if match else False
                match = re.match(r'%( )*UNSATISFIABLE', i)
                self.unsatisfiable = True if match else False
                match = re.match(r'%( )*ERROR', i)
                self.error = True if match else False
            else:
                match = re.match(r'%( )*((OPTIMUM)|(MODEL)) FOUND.*', i)
                if match:
                    answer = last[1:].split(' ')
                    answer.sort()
                    answer = " ".join(answer)
                    self.answers.append(answer)
            line, last = line+1, i
        self.answers.sort()
        if not self.satisfiable and not self.unsatisfiable and not self.error:
            print("PARSING ERROR in class Test")

    def __repr__(self):
        return self.command + "\n" + self.string
        if self.command:
            out = "\ncommand = \"{}\"\n".format(self.command)
        else:
            out = ""
        if self.satisfiable:
            out += "SATISFIABLE\n"
        if self.unsatisfiable:
            out += "UNSATISFIABLE\n"
        if self.error:
            out += "ERROR\n"
        answers = "\n".join(self.answers)
        out += "Answers:\n{}".format(answers)
        return out


class Result(Test):

    def __init__(self, string):
        self.count = 0
        Test.__init__(self, string, [])

    def __repr__(self):
        return self.string

    def parse(self, string, options):
        line, last = 1, ""
        self.answers = []
        for i in string.splitlines():
            match = re.match(r'.*ERROR.*', i)
            if match:
                self.error = True
            match = re.match(r'.*UNSATISFIABLE.*', i)
            if match:
                self.unsatisfiable = True
            match = re.match(r'.*((OPTIMUM)|(MODEL)) FOUND.*', i)
            match_limit = re.match(r'.*MODEL FOUND \(.*', i)
            if match and not match_limit:
                self.satisfiable = True
                answer = last.split(' ')
                answer.sort()
                answer = " ".join(answer)
                self.answers.append(answer)
            line, last = line+1, i
        self.answers.sort()
        if self.satisfiable:   self.count += 1
        if self.unsatisfiable: self.count += 1
        if self.error:         self.count += 1

    def __print_error(self, test, message):
        print("#############################################################")
        print("*************************************************************")
        print("ERROR: " + message)
        print("*************************************************************")
        print("EXPECTED:")
        print("*************************************************************")
        print(test)
        print("*************************************************************")
        print("RESULT:")
        print("*************************************************************")
        print(self)
        print("#############################################################\n")

    def compare(self, test):
        if self.count != 1:
            msg = "ERROR, UNSATISFIABLE or OPTIMUM FOUND messages"
            self.__print_error(test, "parsing error, 0 or many " + msg)
        elif self.satisfiable != test.satisfiable:
            self.__print_error(test, "result is satisfiable")
        elif self.unsatisfiable != test.unsatisfiable:
            self.__print_error(test, "result is unsatisfiable")
        elif self.error != test.error:
            self.__print_error(test, "result gives an error")
        elif "\n".join(self.answers) != "\n".join(test.answers):
            self.__print_error(test, "different answers")
        else:
            return False
        return True

