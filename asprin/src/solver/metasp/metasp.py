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


#
# IMPORTS
#

import clingo
import re
from . import metasp_programs
from . import reify
from ...utils import utils


#
# DEFINES
#

U_METABASE = utils.U_METABASE
U_METAPREF = utils.U_METAPREF
PREFERENCE = utils.PREFERENCE
OPTIMIZE   = utils.OPTIMIZE
VOLATILE      = utils.VOLATILE
HOLDS         = utils.HOLDS
UNSAT_ATOM    = utils.UNSAT
HOLDS_AT_ZERO = utils.HOLDS_AT_ZERO

METAPREF_BASIC = """
{ ##""" + HOLDS + """(X,0..1) } :- X = @get_holds_domain().
##""" + VOLATILE + """(##m(0),##m(1)).
:- ##""" + UNSAT_ATOM + """(##m(0),##m(1)).
#show ##""" + HOLDS + """/2.
#const ##m1=0.
#const ##m2=1.
"""

BINDING_SIMPLE_PYTHON = """
**true(atom(A)) :-     ##""" + HOLDS + """(X,0), **output(##""" + HOLDS + """(X,1),A).                    % from base
**fail(atom(A)) :- not ##""" + HOLDS + """(X,0), **output(##""" + HOLDS + """(X,1),A).                    % from base
**true(atom(A)) :- $$output_term(##""" + HOLDS_AT_ZERO + """(X)), **output(##""" + HOLDS + """(X,0),A),   % from meta_base
                   $$true(atom( B)) : $$output_term(##""" + HOLDS_AT_ZERO + """(X),B), B >= 0;
                   $$fail(atom(-B)) : $$output_term(##""" + HOLDS_AT_ZERO + """(X),B), B <  0.
**fail(atom(A)) :- $$output_term(##""" + HOLDS_AT_ZERO + """(X)), **output(##""" + HOLDS + """(X,0),A),   % from meta_base
                   $$fail(atom( B)),  $$output_term(##""" + HOLDS_AT_ZERO + """(X),B), B >= 0.
**fail(atom(A)) :- $$output_term(##""" + HOLDS_AT_ZERO + """(X)), **output(##""" + HOLDS + """(X,0),A),   % from meta_base
                   $$true(atom(-B)),  $$output_term(##""" + HOLDS_AT_ZERO + """(X),B), B <  0.
**bot :- $$bot.
$$bot :- **bot.
:- not **bot.
$$atom(|B|) :- $$output_term(X,B). % needed when X is a fact
"""

BINDING_SIMPLE_BINARY = """
**true(atom(A)) :-     ##""" + HOLDS + """(X,0), **output(##""" + HOLDS + """(X,1),B), **literal_tuple(B,A).  % from base
**fail(atom(A)) :- not ##""" + HOLDS + """(X,0), **output(##""" + HOLDS + """(X,1),B), **literal_tuple(B,A).  % from base
**true(atom(A)) :- $$true(normal(B)), $$output(##""" + HOLDS + """(X,0),B),                       % from meta_base
                   **output(##""" + HOLDS + """(X,0),C), **literal_tuple(C,A).
**fail(atom(A)) :- $$fail(normal(B)), $$output(##""" + HOLDS + """(X,0),B),                       % from meta_base
                   **output(##""" + HOLDS + """(X,0),C), **literal_tuple(C,A).
**bot :- $$bot.
$$bot :- **bot.
:- not **bot.
"""

BINDING_INC_PYTHON_BASE = """
##fixed(A) :- ##output($$""" + HOLDS + """(X,1),A).
"""

BINDING_INC_BINARY_BASE = """
##fixed(A) :- ##output($$""" + HOLDS + """(X,1),B), ##literal_tuple(B,A).
"""

BINDING_INC_PYTHON = """
##true(m1,m2,atom(A)) :-     $$""" + HOLDS + """(X,m2), ##output($$""" + HOLDS + """(X,1),A).
##fail(m1,m2,atom(A)) :- not $$""" + HOLDS + """(X,m2), ##output($$""" + HOLDS + """(X,1),A).
##true(m1,m2,atom(A)) :-     $$""" + HOLDS + """(X,m1), ##output($$""" + HOLDS + """(X,0),A).
##fail(m1,m2,atom(A)) :- not $$""" + HOLDS + """(X,m1), ##output($$""" + HOLDS + """(X,0),A).
$$""" + UNSAT_ATOM + """($$m(m1),$$m(m2)) :- $$""" + VOLATILE + """($$m(m1),$$m(m2)).
:- not ##bot(m1,m2).
"""

BINDING_INC_BINARY = """
##true(m1,m2,atom(A)) :-     $$""" + HOLDS + """(X,m2), ##output($$""" + HOLDS + """(X,1),B), ##literal_tuple(B,A).
##fail(m1,m2,atom(A)) :- not $$""" + HOLDS + """(X,m2), ##output($$""" + HOLDS + """(X,1),B), ##literal_tuple(B,A).
##true(m1,m2,atom(A)) :-     $$""" + HOLDS + """(X,m1), ##output($$""" + HOLDS + """(X,0),B), ##literal_tuple(B,A).
##fail(m1,m2,atom(A)) :- not $$""" + HOLDS + """(X,m1), ##output($$""" + HOLDS + """(X,0),B), ##literal_tuple(B,A).
$$""" + UNSAT_ATOM + """($$m(m1),$$m(m2)) :- $$""" + VOLATILE + """($$m(m1),$$m(m2)).
:- not ##bot(m1,m2).
"""

BINDING_INC_VOLATILE = """
##true(m1,m2,atom(A)) :- ##supp(A), not ##fact(A), not ##fixed(A), not $$""" + VOLATILE + """($$m(m1),$$m(m2)).
##fail(m1,m2,atom(A)) :- ##supp(A), not ##fact(A), not ##fixed(A), not $$""" + VOLATILE + """($$m(m1),$$m(m2)).
"""

# get_holds_domain() should not be defined here
ASPRIN_LIBRARY_PY = """
#script(python)

import math

def exp2(x):
    return int(math.pow(2,x.number))

def get(atuple, index):
    try:
        return atuple.arguments[index.number]
    except:
        return atuple

def get_mode():
    return 'normal'

sequences = {}
def get_sequence(name, elem):
    string = str(name)
    if string in sequences:
        sequences[string] += 1
    else:
        sequences[string]  = 1
    return sequences[string]

def length(atuple):
    try:
        return len(atuple.arguments)
    except:
        return 1 

def log2up(x):
    return int(math.ceil(math.log(x.number,2)))

#end.
"""

HOLDS_DOMAIN_PY = """
import clingo
holds_domain = {}
def get_holds_domain():
    return holds_domain
"""

class Observer:

    def __init__(
        self,
        control,
        register_observer = False,
        replace = False,
        bool_add_statement = False,
        bool_add_base = False,
        bool_add_specification = False,
        bool_add_constants_nb = False
    ):
        # flags
        self.bool_add_statement     = bool_add_statement
        self.bool_add_base          = bool_add_base
        self.bool_add_specification = bool_add_specification
        self.bool_add_constants_nb  = bool_add_constants_nb
        if register_observer:
            control.register_observer(self, replace)
        # observations
        self.rules         = []
        self.weight_rules  = []
        self.output_atoms  = []
        self.output_terms  = []
        self.statements    = []
        self.base          = None         # (program, old consts, new consts)
        self.specification = None         # (program, old consts, new consts)
        self.constants_nb  = ("", [], []) # (program,         [],         [])

    #
    # control object observer
    #

    def rule(self, choice, head, body):
        self.rules.append((choice, head, body))

    def weight_rule(self, choice, head, lower_bound, body):
        self.weight_rules.append((choice, head, lower_bound, body))

    def output_atom(self, symbol, atom):
        self.output_atoms.append((symbol, atom))

    def output_term(self, symbol, condition):
        self.output_terms.append((symbol, condition))

    #
    # program parser observer
    #

    def add_statement(self, statement):
        if self.bool_add_statement:
            self.statements.append(statement)

    def add_base(self, program, old, new):
        if self.bool_add_base:
            self.base = (program, old, new)

    def add_specification(self, program, old, new):
        if self.bool_add_specification:
            self.specification = (program, old, new)

    def add_constants_nb(self, program, old, new):
        if self.bool_add_constants_nb:
            self.constants_nb = (program, old, new)


# abstract class
class AbstractMetasp:

    def __init__(self, solver):
        # uses solver.control, solver.observer and solver.underscores
        self.solver = solver
        self.binding_simple = None   # to be defined by subclasses
        self.binding_inc_base = None # to be defined by subclasses
        self.binding_inc = None      # to be defined by subclasses

    # private
    # to be defined by subclasses (used by get_incremental_program())
    def get_meta_pref_facts(self, prefix):
        return None

    # private
    # to be defined by subclasses (used by get_meta_program())
    def get_meta_base_facts(self, prefix):
        return None

    # public
    # uses get_meta_base_facts(), get_meta_pref_facts and binding0
    def get_meta_program(self):
        # base
        prefix = self.solver.underscores + "_"*U_METABASE
        meta_base  = self.get_meta_base_facts(prefix)
        meta_base += metasp_programs.metaD_program.replace("##", prefix)
        # pref
        prefix = self.solver.underscores + "_"*U_METAPREF
        meta_pref = self.get_meta_pref_facts(prefix)
        meta_pref += metasp_programs.metaD_program.replace("##", prefix)
        # binding
        meta_bind = self.get_meta_bind(self.binding_simple)
        # return
        return meta_base + meta_pref + meta_bind

    # public
    # uses get_meta_pref_facts, binding_inc and binding_inc_base
    def get_incremental_program(self):
        u = self.solver.underscores
        prefix = u + "_"*U_METAPREF
        # base
        base = self.get_meta_pref_facts(prefix)
        base += metasp_programs.metaD_program_inc_base.replace("##", prefix)
        base += self.binding_inc_base.replace("$$", u).replace("##", prefix)
        # parameters
        parameters = metasp_programs.metaD_program_parameters
        # incremental
        inc = metasp_programs.metaD_program_inc.replace("##", prefix)
        binding = self.binding_inc + BINDING_INC_VOLATILE
        inc += binding.replace("$$", u).replace("##", prefix)
        # return
        return base, parameters, inc

    #
    # get_pref() (used by MetaspPython and MetaspBinary)
    #

    def statement_to_str(self, statement):
        if str(statement.type) == "Definition": # to avoid printing [default]
            return "#const {}={}.".format(statement.name, statement.value)
        elif str(statement.type) == "Program":
            return "" # IMPORTANT: program statements are skipped
        return str(statement)

    def get_specification(self):
        underscores = self.solver.underscores
        signatures = [(underscores + PREFERENCE, 2),
                      (underscores + PREFERENCE, 5),
                      (underscores +   OPTIMIZE, 1)]
        symbolic_atoms = self.solver.control.symbolic_atoms
        spec = ""
        for name, arity in signatures:
            spec += " ".join([
                str(atom.symbol) + "."
                for atom in symbolic_atoms.by_signature(name, arity)
            ]) + "\n"
        return spec

    # WARNING:
    # This is incorrect in general, since it may change the
    # content of some strings.
    # This is needed so that @functions of 0 parameters are printed
    # correctly. This should be fixed in clingo.
    def fix_functions(self, program):
        pattern = r'(@_*[a-z][\'A-Za-z0-9_]*)([^\(\'A-Za-z0-9_])'
        return re.sub(pattern, r'\1()\2', program)

    def get_pref(self):
        # basic program
        basic = METAPREF_BASIC.replace("##", self.solver.underscores)
        # preference specification
        specification = self.get_specification()
        # preference program
        preference_program = "\n".join([
            self.statement_to_str(s) for s in self.solver.observer.statements
        ])
        # See WARNING above
        preference_program = self.fix_functions(preference_program)
        # constants
        constants = self.solver.observer.constants_nb[0]
        # return
        return basic + specification + preference_program + constants

    #
    # get_meta_bind() (used by get_meta_program())
    #

    def get_meta_bind(self, binding):
        out = binding.replace("##", self.solver.underscores)
        prefix_base = self.solver.underscores + "_"*U_METABASE
        prefix_pref = self.solver.underscores + "_"*U_METAPREF
        return out.replace("$$", prefix_base).replace("**", prefix_pref)


# Uses the observer in Python
class MetaspPython(AbstractMetasp):

    def __init__(self, solver):
        AbstractMetasp.__init__(self, solver)
        self.binding_simple = BINDING_SIMPLE_PYTHON
        self.binding_inc_base = BINDING_INC_PYTHON_BASE
        self.binding_inc = BINDING_INC_PYTHON

    def get_meta_base_facts(self, prefix):
        return reify.reify_from_observer(self.solver.observer, prefix)

    def get_meta_pref_facts(self, prefix):
        ctl = clingo.Control([])
        observer = Observer(ctl, register_observer=True, replace=True)
        ctl.add("base", [], self.get_pref())
        ctl.ground([("base",[])], self.solver)
        return reify.reify_from_observer(observer, prefix)


# Uses clingo binary
class MetaspBinary(AbstractMetasp):

    def __init__(self, solver):
        AbstractMetasp.__init__(self, solver)
        self.binding_simple = BINDING_SIMPLE_BINARY
        self.binding_inc_base = BINDING_INC_BINARY_BASE
        self.binding_inc = BINDING_INC_BINARY

    # WARNING:
    # The next function relies on the form of the specification programs,
    # assumes rules for preference/2, preference/5, optimize/1
    # start at the beginning of a line and finish at the end.
    # Depends on spec_parser/ast.py.
    def get_meta_base_facts(self, prefix):
        observer = self.solver.observer
        # get base
        program  = observer.base[0] + "\n"
        # get specification without preference/2, /5 and optimize/1
        pattern = r'^(\_*)(' + PREFERENCE + r'|' + OPTIMIZE + r')'
        program += re.sub(
            pattern, r'%\1\2', observer.specification[0], flags=re.M
        ) + "\n"
        # add constants
        for idx, old in enumerate(observer.base[1]): # for every old constant
            program += "#const {}={}.".format(old, observer.base[2][idx]) + "\n"
        # add show
        program += "#show " + self.solver.underscores + "holds/2.\n"
        # get meta using clingo binary
        return reify.reify_from_string(program, prefix)

    def get_meta_pref_facts(self, prefix):
        holds_domain = ",\n".join([
            '  clingo.parse_term("""{}""")'.format(x) 
            for x in self.solver.holds_domain
        ])
        get_holds_domain = HOLDS_DOMAIN_PY.format("[\n" + holds_domain + "\n]")
        library = ASPRIN_LIBRARY_PY.replace(
            "#end.", get_holds_domain + "\n#end."
        )
        prefix = self.solver.underscores + "_"*U_METAPREF
        return reify.reify_from_string(self.get_pref() + library, prefix)

