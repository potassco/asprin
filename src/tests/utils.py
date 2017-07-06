from __future__ import print_function
import os
import re

PYTHON = "python"
ASPRIN = PYTHON + " " + str(os.path.join(os.path.dirname(os.path.realpath(
                            __file__)),"..","..","asprin")) + " --no-info"

class Test:

    def __init__(self, string):
        self.command = None
        self.satisfiable = False
        self.unsatisfiable = False
        self.error = False
        self.answers = None
        self.parse(string)

    def parse(self, string):
        line, last = 1, ""
        self.answers = [] 
        for i in string.splitlines():
            if line == 1:
                self.command = i[1:]
                self.command = self.command.replace('asprin',ASPRIN)
            elif line == 2:
                match = re.match(r'%( )*SATISFIABLE', i)
                self.satisfiable = True if match else False
                match = re.match(r'%( )*UNSATISFIABLE', i)
                self.unsatisfiable = True if match else False
                match = re.match(r'%( )*ERROR', i)
                self.error = True if match else False
            else:
                match = re.match(r'%( )*OPTIMUM FOUND', i)
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
        out = "\ncommand = \"{}\"\n".format(self.command)
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
        Test.__init__(self, string)

    def parse(self, string):
        line, last = 1, ""
        self.answers = []
        for i in string.splitlines():
            match = re.match(r'.*ERROR.*', i)
            if match:
                self.error = True
            match = re.match(r'.*UNSATISFIABLE.*', i)
            if match:
                self.unsatisfiable = True
            match = re.match(r'.*OPTIMUM FOUND.*', i)
            if match:
                self.satisfiable = True
                answer = last.split(' ')
                answer.sort()
                answer = " ".join(answer)
                self.answers.append(answer)
            line, last = line+1, i
        self.answers.sort()
        count = 0
        if self.satisfiable: count += 1
        if self.unsatisfiable: count += 1
        if self.error: count += 1
        if count != 1:
            print("***********************************************************")
            print("PARSING ERROR in class Result (count={})".format(count))
            print(string)
            print("***********************************************************")

    def __print_error(self, test, message):
        print("*************************************************************")
        print("ERROR: " + message)
        print(test)
        print(self)
        print("#############################################################")

    def compare(self, test):
        if self.satisfiable != test.satisfiable:
            self.__print_error(test, "result is satisfiable")
        elif self.unsatisfiable != test.unsatisfiable:
            self.__print_error(test, "result is unsatisfiable")
        elif self.error != test.error:
            self.__print_error(test, "result gives an error")
        elif "\n".join(self.answers) != "\n".join(test.answers):
            self.__print_error(test, "different answers")



#
# not used any more
#

def get_path(file):
    return os.path.dirname(file)

# returns $directory{file}/name
def add_dir(file, name):
    return str(os.path.join(os.path.dirname(file), name))

# returns the absolute paths of all ".lp" files 
# in $directory{file}/dir_name
def get_files(file, dir_name):
    path = os.path.join(os.path.dirname(file), dir_name)
    dir = [os.path.join(path, f) for f in os.listdir(path)]
    out = [str(f) for f in dir if str(f)[-3:]==".lp"]
    out.sort()
    return out



