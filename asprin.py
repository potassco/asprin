#!/usr/bin/python
import sys
import os
import re
#import logging
#logging.basicConfig(level=logging.DEBUG)

from src.spec_parser import spec_parser
from src.pp_parser   import   pp_parser
from src.solver      import      solver

_version = "asprin version 3.0.0"

class Asprin:

    def __init__(self):
        pass

    def on_model(self,model):
        print model

    def run(self,files,options):
        # specification parsing
        self.spec_parser = spec_parser.Parser()
        program          = self.spec_parser.parse_files(files)
        underscores      = self.spec_parser.get_underscores()
        # preference programs parsing
        self.pp_parser   = pp_parser.Parser(underscores)
        control          = self.pp_parser.parse(program)
        # solving
        _solver          = solver.Solver(control)
        _solver.set_options(options)
        _solver.run()

def run():
    print _version
    asprin = Asprin()
    # parse input
    max_models = 1
    files = []
    for i in sys.argv[1:]:
        if (re.match(r'^[0-9]+$',i)):
            max_models = int(i)
        elif i=="--help":
            print "Usage: asprin [number_of_models] [files]"
            return
        else: files.append(i)
    if files == []: print "No files"; return
    MAX_MODELS = "max_models"
    options = dict([(MAX_MODELS,max_models)])
    print "Reading from " + files[0] + " ..."
    asprin.run(files,options)

if __name__ == "__main__":
    run()


# TODO: underscores
# TODO: preference type names underscored

