
import sys
import os
import re
import logging
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

    def run(self,files):
        # specification parsing
        self.spec_parser = spec_parser.Parser()
        program          = self.spec_parser.parse_files(files)
        underscores      = self.spec_parser.get_underscores()
        #print program
        #print "###############################"
        # preference programs parsing
        self.pp_parser = pp_parser.Parser(underscores)
        control        = self.pp_parser.parse(program)
        #_solver = solver.Solver(control)
        #solver.main(control)
        _solver = solver.Solver(control)
        _solver.run()

if __name__ == "__main__":
    asprin = Asprin()
    asprin.run(sys.argv[1:])


