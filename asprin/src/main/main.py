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

#
# IMPORTS
#

from __future__ import print_function
import re
import argparse
import sys
import clingo
import os
from ..spec_parser    import    spec_parser
from ..program_parser import program_parser
from ..solver         import         solver
from ..utils          import        printer
from ..utils          import          utils
from .                import    clingo_help
import errno
import signal

#
# DEFINES
#

UNKNOWN        = "UNKNOWN"
ERROR          = "*** ERROR: (asprin): {}"
ERROR_INFO     = "*** Info : (asprin): Try '--help' for usage information"
ERROR_OPEN     = "<cmd>: error: file could not be opened:\n  {}\n"
ERROR_FATAL    = "Fatal error, this should not happen.\n"
ERROR_PARSING  = "parsing failed"
DEBUG          = "--debug"
TEST           = "--test"
ALL_CONFIGS    = ["tweety", "trendy", "frumpy", "crafty", "jumpy", "handy"]
HELP_PROJECT   = """R|: Enable projective solution enumeration,
  projecting on the formulas of the specification"""
HELP_HEURISTIC = """R|: Apply domain heuristics with value <v> and modifier <m>
  on formulas of the preference specification"""
HELP_DELETE_BETTER = """R|: After computing an optimal model,
  add a program to delete models better than that one"""
HELP_TOTAL_ORDER = """R|: Do not add programs for optimal models after the \
first one
  Use only if the preference specification represents a total order"""
HELP_GROUND_ONCE = """R|: Ground preference program only once \
(for improving a model)"""
HELP_CLINGO_HELP = ": Print {1=basic|2=more|3=full} clingo help and exit"
HELP_RELEASE_LAST = """R|: Improving a model, release the preference program \
for the last model 
  as soon as possible"""
HELP_NO_OPT_IMPROVING = """R|: Improving a model, do not use optimal models"""
HELP_VOLATILE_IMPROVING = """R|: Use volatile preference programs \
for improving a model"""
HELP_VOLATILE_OPTIMAL = """R|: Use volatile preference programs \
for optimal models"""
HELP_TRANS_EXT = """R|: Configure handling of extended rules \
for non base programs
  (<m> should be as in clingo --trans-ext option)"""
HELP_PREFERENCE_UNSAT = """R|: Use """ + utils.UNSATP + """ programs \
for optimal models"""
HELP_CONST_NONBASE = """R|: Replace term occurrences of <id> in non-base
  programs with <t>"""
HELP_IMPROVE_LIMIT = """R|: Improving a model, stop search after x conflicts,
  where x is <m> times the conflicts for the first model of the current iteration;
  add ',all' to consider the conflicts for all the models of the current iteration,
  add ',<min>' to search always for at least <min> conflicts, 
  and add ',reprint' to reprint at the end the optimal models"""
HELP_CONFIGS = """R|: Run clingo configurations c1, ..., cn iteratively 
  (use 'all' for running all configurations)"""

#
# VERSION
#

HERE = os.path.abspath(os.path.dirname(__file__))
META_FILE = os.path.join(HERE,"..","..","__init__.py")
with open(META_FILE,'r') as f:
    meta = f.read()
    meta_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", meta, re.M)
    if meta_match:
        VERSION = meta_match.group(1)
    else:
        raise RuntimeError("Unable to find __version__ string")


#
# MyArgumentParser
#

class MyArgumentParser(argparse.ArgumentParser):

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        file.write("asprin version {}\n".format(VERSION))
        argparse.ArgumentParser.print_help(self, file)

    def error(self, message):
        raise argparse.ArgumentError(None,"In context <asprin>: " + message)

class SmartFormatter(argparse.RawDescriptionHelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.RawDescriptionHelpFormatter._split_lines(self, text, width)


#
# class AsprinArgumentParser
#
class AsprinArgumentParser:


    clingo_help = """
Clingo Options:
  --<option>[=<value>]\t: Set clingo <option> [to <value>]

    """


    usage = "asprin [number] [options] [files]"


    epilog = """
Default command-line:
asprin --models 1

asprin is part of Potassco: https://potassco.org/labs
Get help/report bugs via : https://potassco.org/support
    """


    version_string = "asprin " + VERSION + """
Copyright (C) Javier Romero
License: The MIT License <https://opensource.org/licenses/MIT>"""


    def __init__(self):
        self.underscores  = 0
        self.__first_file = None
        self.__file_warnings = []

    def __update_underscores(self,new):
        i = 0
        while len(new)>i and new[i]=="_": i+=1
        if i>self.underscores: self.underscores = i

    def __add_file(self,files,file):
        abs_file = os.path.abspath(file) if file != "-" else "-"
        if abs_file in [i[1] for i in files]:
            self.__file_warnings.append(file)
        else:
            files.append((file,abs_file))
        if not self.__first_file:
            self.__first_file = file

    def __do_constants(self, alist):
        try:
            constants = dict()
            for i in alist:
                old, sep, new = i.partition("=")
                self.__update_underscores(new)
                if new is "":
                    raise Exception(
                        "no definition for constant {}".format(old)
                    )
                if old in constants:
                    raise Exception("constant {} defined twice".format(old))
                else:
                    constants[old] = new
            return constants
        except Exception as e:
            self.__cmd_parser.error(str(e))

    def __do_improve_limit(self, string):
        if string is None:
            return None
        try:
            out = [0,False,0,False]
            match = re.match(r'(\d+)(,all)?(,\d+)?(,reprint)?$',string)
            if not match:
                raise Exception("incorrect value for option --improve-limit")
            out[0] = int(match.group(1))
            if match.group(2) is not None:
                out[1] = True
            if match.group(3) is not None:
                out[2] = int(match.group(3)[1:])
            if match.group(4) is not None:
                out[3] = True
            return out
        except Exception as e:
            self.__cmd_parser.error(str(e))

    def run(self, args):

        # command parser
        _epilog = self.clingo_help + "\nusage: " + self.usage + self.epilog
        cmd_parser = MyArgumentParser(usage=self.usage, epilog=_epilog,
            formatter_class=SmartFormatter, #argparse.RawDescriptionHelpFormatter,
            add_help=False, prog="asprin")
        self.__cmd_parser = cmd_parser

        # Basic Options
        basic = cmd_parser.add_argument_group('Basic Options')
        basic.add_argument('--help', '-h', action='help',
                           help=': Print help and exit')
        basic.add_argument('--clingo-help',
                           help=HELP_CLINGO_HELP,
                           type=int, dest='clingo_help', metavar='<m>', 
                           default=0, choices=[0,1,2,3])
        basic.add_argument('--version', '-v', dest='version',
                           action='store_true',
                           help=': Print version information and exit')
        basic.add_argument('--print-programs', dest='print-programs',
                           help=': Print translated programs and exit',
                           action='store_true')
        basic.add_argument('--no-check', dest='check', 
                           help=": Skip syntax checks",
                           action='store_false')
        #basic.add_argument('-', dest='read_stdin', action='store_true',
        #                   help=argparse.SUPPRESS)
        basic.add_argument(TEST, dest='test', action='store_true',
                           help=': Run system tests')
        basic.add_argument('--stats', dest='stats', action='store_true',
                           help=': Print statistics')
        basic.add_argument('--quiet', '-q', dest='quiet', choices=[0,1,2],
                           metavar='<q>', type=int, default=0, 
                           help=': print {0=all|1=optimal|2=no} models')
        #basic.add_argument('--no-info', dest='no_info', action='store_true',
        #                   help=': Do not print basic information')
        basic.add_argument('--no-asprin-lib', dest='asprin-lib',
                           help=': Do not include asprin_lib.lp',
                           action='store_false')
        basic.add_argument('-c', '--const', dest='constants', 
                           action="append", help=argparse.SUPPRESS, default=[])
        basic.add_argument('--const-nb', dest='constants_nb', 
                           action="append", 
                           metavar="<id>=<t>",
                           help=HELP_CONST_NONBASE,
                           default=[])
        basic.add_argument(DEBUG, dest='debug', action='store_true',
                           help=argparse.SUPPRESS)
        basic.add_argument('--to-clingo', dest='to_clingo', 
                           action="append", help=argparse.SUPPRESS, default=[])

        # Solving Options
        solving = cmd_parser.add_argument_group('Solving Options')
        solving.add_argument('--models', '-n',
                             help=": Compute at most <n> models (0 for all)",
                             type=int, dest='max_models', metavar='<n>',
                             default=1)
        solving.add_argument('--non-optimal', dest='non_optimal', 
                             help=": Compute also non optimal models", 
                             action='store_true')
        solving.add_argument('--project', dest='project', help=HELP_PROJECT,
                             action='store_true')
        solving.add_argument('--solving-mode', dest='solving_mode', 
                             metavar="<arg>",
                             help=""": Run {normal|approx|heuristic} \
                                       solving mode""",
                             #help=argparse.SUPPRESS,
                             default="normal", 
                             choices=["normal", "heuristic", "approx"])
        solving.add_argument('--dom-heur', dest='cmd_heuristic',
                              nargs=2, metavar=('<v>','<m>'),
                              help=HELP_HEURISTIC)
        solving.add_argument('--configs', dest='configs',
                              metavar='<ci>', action='append',
                              help=HELP_CONFIGS)

        # Additional Solving Options
        solving = cmd_parser.add_argument_group('Additional Solving Options')
        solving.add_argument('--steps', '-s', 
                             help=": Execute at most <s> steps", type=int,
                             dest='steps', metavar='<s>', default=0)
        basic.add_argument('--clean-up', dest='clean_up', action='store_true',
                           help=argparse.SUPPRESS)
        solving.add_argument('--delete-better', dest='delete_better', 
                             help=HELP_DELETE_BETTER,
                             action='store_true')
        solving.add_argument('--total-order', dest='total_order', 
                             help=HELP_TOTAL_ORDER,
                             action='store_true')
        solving.add_argument('--ground-once', dest='ground_once', 
                             help=HELP_GROUND_ONCE,
                             action='store_true')
        solving.add_argument('--release-last', dest='release_last', 
                             help=HELP_RELEASE_LAST,
                             action='store_true')
        solving.add_argument('--no-opt-improving', dest='no_opt_improving', 
                             help=HELP_NO_OPT_IMPROVING,
                             action='store_true')
        solving.add_argument('--volatile-improving', dest='volatile_improving', 
                             help=HELP_VOLATILE_IMPROVING,
                             action='store_true')
        solving.add_argument('--volatile-optimal', dest='volatile_optimal', 
                             help=HELP_VOLATILE_OPTIMAL,
                             action='store_true')
        solving.add_argument('--pref-trans-ext', dest='trans_ext',
                             help=HELP_TRANS_EXT, metavar="<m>", default=None)
        solving.add_argument('--preference-unsat', dest='preference_unsat',
                             help=argparse.SUPPRESS,
                             #help=HELP_PREFERENCE_UNSAT,
                             action='store_true')
        solving.add_argument('--improve-limit',
                             metavar='<m>', dest='improve_limit',
                             help=HELP_IMPROVE_LIMIT)

        options, unknown = cmd_parser.parse_known_args(args=args)
        options = vars(options)

        # print version
        if options['version']:
            print(self.version_string)
            sys.exit(0)

        # separate files, number of models and clingo options
        options['files'], clingo_options = [], []
        for i in unknown:
            if i=="-":                                   
                self.__add_file(options['files'],i)
            elif (re.match(r'^([0-9]|[1-9][0-9]+)$',i)): 
                options['max_models'] = int(i)
            elif (re.match(r'^-',i)):                    
                clingo_options.append(i)
            else:                                        
                self.__add_file(options['files'],i)

        # when no files, add stdin
        # build prologue
        if options['files'] == []:
            self.__first_file = "stdin"
            options['files'].append(("-","-"))
        if len(options['files'])>1: 
            self.__first_file += " ..."
        prologue = "asprin version " + VERSION + "\nReading from " 
        prologue += self.__first_file

        # handle constants
        options['constants']    = self.__do_constants(options['constants'])
        options['constants_nb'] = self.__do_constants(options['constants_nb'])

        # handle improve_limit
        options['improve_limit'] = self.__do_improve_limit(
            options['improve_limit']
        )

        # handle configs all
        if options['configs'] and 'all' in options['configs']:
            options['configs'] = ALL_CONFIGS

        # statistics
        # if options['stats']:
        clingo_options.append('--stats')

        # return
        return options, clingo_options, self.underscores, prologue, \
               self.__file_warnings



#
# class Asprin
#
class Asprin:

    def __init__(self):
        self.control = None
        self.solver = None
        self.options = None

    def __update_constants(self,options,constants):
        for i in constants:
            if i[0] not in options['constants']:
                options['constants'][i[0]] = i[1]

    def __get_control(self,clingo_options):
        try:
            return clingo.Control(clingo_options)
        except Exception as e:
            raise argparse.ArgumentError(None,e.message)

    def run_wild(self, args):

        # arguments parsing 
        aap = AsprinArgumentParser()
        self.options, clingo_options, u, prologue, warnings = aap.run(args)

        # clingo help
        if self.options["clingo_help"] > 0:
            if self.options["clingo_help"] == 1:
                out = clingo_help.HELP_1
            if self.options["clingo_help"] == 2:
                out = clingo_help.HELP_2
            if self.options["clingo_help"] == 3:
                out = clingo_help.HELP_3
            printer.Printer().do_print(out)
            sys.exit(0)

        # create Control object
        self.control = self.__get_control(clingo_options)

        # print prologue and warnings
        print(prologue)
        for i in warnings:
            printer.Printer().warning_included_file(i)

        # load --to-clingo files
        for i in self.options["to_clingo"]:
            self.control.load(i)

        # specification parsing
        sp = spec_parser.Parser(u)
        programs, utils.underscores, base_constants, self.options['show'] = \
                                                 sp.parse_files(self.options)
        self.__update_constants(self.options, base_constants)

        # preference programs parsing
        program_parser.Parser(self.control, programs, self.options).parse() 

        # solving
        self.solver = solver.Solver(self.control)
        self.solver.set_options(self.options)
        self.solver.run()

    def signal_handler(self, signum, frame):
        if self.solver is not None:
            self.solver.end()
        elif self.control is not None:
            printer.Printer().print_stats(self.control, 0, True, 0, False,
                                          self.options['stats'])
        sys.exit(1)

    def run(self, args):
        # signals
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT,  self.signal_handler)
        # try to run wild
        try:
            self.run_wild(args)
        # catch exceptions
        except argparse.ArgumentError as e:
            print(ERROR.format(str(e)),file=sys.stderr)
            print(ERROR_INFO,file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            if (e.errno == errno.ENOENT):
                print(ERROR_OPEN.format(e.filename),file=sys.stderr)
                print(ERROR.format(ERROR_PARSING),file=sys.stderr)
            else: 
                print(ERROR.format(str(e)),file=sys.stderr)
            print(UNKNOWN,file=sys.stdout)
            sys.exit(65)
        except utils.SilentException as e:
            pass
        except utils.FatalException as e:
            print(ERROR.format(ERROR_FATAL),file=sys.stderr)
            print(UNKNOWN,file=sys.stdout)
            sys.exit(65)
        except Exception as e:
            print(ERROR.format(str(e)),file=sys.stderr)
            print(UNKNOWN,file=sys.stdout)
            sys.exit(65)


def main(args):
    if TEST in args:
        args.remove(TEST)
        from ..tests import tester
        tester.main(args)
    elif DEBUG in args:
        Asprin().run_wild(args)
    else:
        Asprin().run(args)


