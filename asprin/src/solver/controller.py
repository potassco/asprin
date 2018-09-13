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

from ..utils import utils
from .metasp import metasp

class GeneralController:

    def __init__(self, solver):
        self.improve_limit = True if solver.options.improve_limit is not None \
            else False
        self.solver         = solver

    def start(self):
        solver, options = self.solver, self.solver.options
        if options.trans_ext is not None:
            solver.control.configuration.asp.trans_ext = options.trans_ext
        # store nholds and set holds domain
        if solver.options.max_models != 1:
            solver.store_nholds = True
        if solver.store_nholds:
            solver.set_holds_domain = True
        if solver.set_holds_domain:
            solver.do_set_holds_domain()
        #
        solver.add_encodings()
        solver.ground_preference_base()
        if options.cmd_heuristic is not None:
            solver.ground_cmd_heuristic()
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"
        if options.preference_unsat and options.max_models != 1:
            solver.get_preference_parts_opt = solver.get_preference_parts_unsatp
            solver.ground_unsatp_base()
        # check syntax
        if options.check:
            solver.check_errors()
        # non optimal
        if solver.no_optimize():
            # modifying options
            solver.options.non_optimal = True
        if solver.options.non_optimal:
            solver.str_found      = utils.STR_MODEL_FOUND
            solver.str_found_star = utils.STR_MODEL_FOUND_STAR
            solver.add_unsat_to_preference_program()


    def sat(self):
        self.solver.models     += 1
        self.solver.last_unsat  = False
        self.solver.last_model  = self.solver.step
        self.solver.check_last_model()
        if self.solver.options.quiet == 0:
            self.solver.print_answer()
        else:
            self.solver.print_str_answer()

    def unsat(self):
        if self.solver.last_unsat:
            self.solver.more_models = False
            if self.solver.models == 0:
                self.solver.print_unsat()
            elif self.improve_limit:
                self.solver.enumerate_unknown()
            self.solver.end()
        if self.solver.options.quiet == 1:
            self.solver.print_shown()
        self.solver.last_unsat = True
        self.solver.opt_models  += 1
        self.solver.print_optimum_string()
        if self.solver.opt_models == self.solver.options.max_models:
            self.solver.end()
        if self.solver.options.steps == self.solver.step:
            self.solver.print_steps_message()
            self.solver.end() # to exit asap in this case

    def unknown(self):
        if self.solver.last_unsat:
            raise utils.FatalException
        self.solver.print_limit_string()
        self.solver.last_unsat = True # act as if unsat
        if self.solver.options.steps == self.solver.step:
            self.solver.print_steps_message()
            self.solver.end() # to exit asap in this case

    def end_loop(self):
        self.solver.step = self.solver.step + 1
        if self.solver.options.steps == (self.solver.step - 1):
            self.solver.print_steps_message()
            self.solver.end()
        if self.solver.options.clean_up:
            self.solver.clean_up()


class GeneralControllerHandleOptimal:

    def __init__(self, solver):
        self.solver = solver
        self.start_step = True
        self.first  = True
        self.delete_worse  = True
        self.delete_better = self.solver.options.delete_better
        self.total_order   = self.solver.options.total_order
        self.no_opt_improving, self.volatile = False, False
        if solver.options.no_opt_improving:
            if solver.options.max_models != 1:
                self.no_opt_improving = True
            self.volatile = True
        if solver.options.volatile_optimal:
            self.volatile = True

    def start(self):
        if self.delete_better:
            self.solver.ground_holds_delete_better()

    def sat(self):
        if self.no_opt_improving and self.start_step:
            self.solver.relax_optimal_models()
        self.start_step = False

    def __preprocess(self):
        if self.total_order and not self.first:
            self.delete_worse  = False
            self.delete_better = False
        self.first = False

    def unsat(self):
        self.start_step = True
        self.__preprocess()
        self.solver.handle_optimal_model(self.solver.last_model,
                                         False,
                                         self.delete_worse,
                                         self.delete_better,
                                         self.volatile)

    def unknown(self):
        self.start_step = True
        self.__preprocess()
        self.solver.handle_optimal_model(self.solver.last_model,
                                         True,
                                         self.delete_worse,
                                         False,
                                         True)


class EnumerationController:

    def __init__(self, solver):
        self.solver = solver
        # show_underscores is set by program_parser.py
        if not solver.options.project and not solver.options.show_underscores:
            solver.same_shown_function = solver.same_shown

    def unsat(self):
        if not self.solver.options.project:
            self.solver.enumerate()
            if self.solver.opt_models == self.solver.options.max_models:
                self.solver.end()


#
# Method Controllers
#

class MethodController:

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        pass

    def start_loop(self):
        pass

    def solve(self):
        pass

    def unsat(self):
        pass


class GroundManyMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        self.volatile = False
        self.ground_holds = 0
        if (self.solver.options.max_models != 1 or
            self.solver.options.release_last or 
            self.solver.options.volatile_improving):
            self.volatile = True 

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.ground_holds(self.solver.last_model)
            self.ground_holds = self.solver.last_model
            self.solver.ground_preference_program(self.volatile)

    def solve(self):
        self.solver.solve(
            assumptions=self.solver.assumptions,
            on_model=self.solver.on_model
        )

    def unsat(self):
        self.solver.relax_previous_models()
        if self.ground_holds != self.solver.last_model:
            self.solver.ground_holds(self.solver.last_model)


class GroundOnceMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        solver.store_nholds = True

    def start(self):
        self.solver.ground_open_preference_program()
        self.solver.turn_off_preference_program()

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.turn_on_preference_program()

    def solve(self):
        self.solver.solve(
            assumptions=self.solver.assumptions,
            on_model=self.solver.on_model
        )

    def unsat(self):
        self.solver.ground_holds(self.solver.last_model)
        self.solver.turn_off_preference_program()


class ApproxMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        self.solver.store_nholds = True

    def start(self):
        self.solver.solve_approx()
        # finishes asprin


class HeurMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)

    def start(self):
        self.solver.ground_heuristic()

    def solve(self):
        if self.solver.last_unsat:
            self.solver.solve_heuristic()
        else:
            self.solver.solve_unsat()

    def unsat(self):
        self.solver.ground_holds(self.solver.last_model)


class MetaMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        self.solver = solver
        self.solver.set_holds_domain = True # TODO: CHECK IF/WHEN NEEDED
        #self.meta = metasp.MetaspA(solver)
        self.meta = metasp.MetaspB(solver)

    def start(self):
        # get meta program
        meta_program = self.meta.get_meta_program()
        # add and ground
        ctl = self.solver.control
        ctl.add(utils.METAPROGRAM, [], meta_program)
        self.solver.ground([(utils.METAPROGRAM, [])])
        # solve
        count = 0
        ctl.configuration.solve.models = "0"
        with ctl.solve(yield_=True) as handle:
            for m in handle:
                print(m.symbols(shown=True))
                count += 1
            print(handle.get())
        print(count)
        # finishes asprin
        self.solver.end()

    def get_specification(self):
        control = self.solver.control
        underscores = self.solver.underscores
        signatures = [(underscores +   "preference", 2),
                      (underscores + "##preference", 5),
                      (underscores +    "_optimize", 1)]
        spec = ""
        for name, arity in signatures:
            spec += " ".join([
                str(atom.symbol)+"." for atom in control.symbolic_atoms.by_signature(name, arity)
            ]) + "\n"
        return spec

    def get_meta_pref(self):
        # same
        from .meta import meta
        observer = self.solver.observer
        ubase, upref = "____", "_____"

        # Add constants non base

        # start
        import clingo
        ctl = clingo.Control(["--output-debug=text"])
        ctl = clingo.Control(["0"])
        # preference program
        def to_str(s):
            if str(s.type) == "Definition":
                return "#const {}={}.".format(s.name, s.value)
            return str(s)
        program = "\n".join([to_str(s) for s in observer.statements])
        # preference specification
        specification = self.get_specification()
        # constants
        constants = " ".join(["#const {}={}.".format(x,y) for x, y in self.solver.options.constants_nb.items()])
        # domain independent
        choices = """
{ _holds(X,1) } :- X = @get_holds_domain().
{ _holds(X,0) } :- X = @get_holds_domain().
#show _holds/2.
_volatile(_m(0),_m(1)).
:- _unsat(_m(0),_m(1)).
"""
        choices += constants
        # add preference programs
        ctl.add("base", [], program)
        # add specification
        ctl.add("specification", [], specification)
        # add choices
        ctl.add("choices", [], choices)
        parts  = [("specification", [])]
        parts.append((utils.PREFP, [0,1]))
        parts.append((utils.PBASE, []))
        parts.append(("choices", []))
        observer = utils.Observer(ctl, True)
        #observer = utils.Observer(ctl, False)
        ctl.ground(parts, self.solver)
        return meta.Meta().reify(observer, upref)

    def get_meta_pref2(self):
        # same
        from .meta import meta
        observer = self.solver.observer
        ubase, upref = "____", "_____"

        # PROBLEM WITH CONSTANTS

        # start
        import clingo
        ctl = clingo.Control(["--output-debug=text"])
        ctl = clingo.Control(["0"])
        # preference program
        def to_str(s):
            if str(s.type) == "Definition":
                return "#const {}={}.".format(s.name, s.value)
            return str(s)
        program = "\n".join([to_str(s) for s in observer.statements])
        # preference specification
        specification = self.get_specification()
        # domain independent
        choices = """
{ _holds(X,1) } :- X = @get_holds_domain().
{ _holds(X,0) } :- X = @get_holds_domain().
#show _holds/2.
_volatile(_m(0),_m(1)).
:- _unsat(_m(0),_m(1)).
"""
        # constants
        constants = " ".join(["#const {}={}.".format(x,y) for x, y in self.solver.options.constants_nb.items()])
        choices += constants
        functions = """
#script(python)

import math

#
# USED BY ASPRIN LIBRARY
#

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

        holds_domain = " ".join(["_holds_domain({}).".format(x) for x in self.solver.holds_domain])
        choices = choices.replace("X = @get_holds_domain()", "_holds_domain(X)")
        choices += "\n" + holds_domain + "\n"
        all = functions + "\n" + program + "\n" + specification + "\n" + choices
        all = all.replace("\n#program", "\n%#program")
        all += "\n#const _m1=0.\n#const _m2=1."

        ### DONE: ADD SOLVER FUNCTIONS CALLED BY THE LIBRARY

        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile() as file_in:
            file_in.write(all.encode())
            file_in.flush()
            with tempfile.TemporaryFile() as file_out:
                command = ["clingo", "--output=reify", file_in.name]
                subprocess.call(command, stdout=file_out)
                file_out.seek(0)
                out = file_out.read()
                if isinstance(out, bytes):
                    out = out.decode()
                out = "\n" + out
                import re
                out = re.sub(r'\n(\w+)', r'\n' + upref + r'\1', out)
                from .meta import meta_programs
                out += meta_programs.metaD_program.replace("##", upref)
        return out

    def get_meta_bind1(self):
        return """
###true(atom(A)) :-     _holds(X,0), ###output(_holds(X,1),A). % from base
###fail(atom(A)) :- not _holds(X,0), ###output(_holds(X,1),A). % from base
###true(atom(A)) :- ##true(atom(B)), ##output_term(_holds_at_zero(X),B), ###output(_holds(X,0),A). % from meta-base
###fail(atom(A)) :- ##fail(atom(B)), ##output_term(_holds_at_zero(X),B), ###output(_holds(X,0),A). % from meta-base
        """

    def get_meta_bind2(self):
        return """
###true(atom(A)) :-     _holds(X,0), ###output(_holds(X,1),B), ###literal_tuple(B,A). % from base
###fail(atom(A)) :- not _holds(X,0), ###output(_holds(X,1),B), ###literal_tuple(B,A). % from base
###true(atom(A)) :- ##true(atom(B)), ##output_term(_holds_at_zero(X),B), 
                    ###output(_holds(X,0),C), ###literal_tuple(C,A). % from meta-base
###fail(atom(A)) :- ##fail(atom(B)), ##output_term(_holds_at_zero(X),B), 
                    ###output(_holds(X,0),C), ###literal_tuple(C,A). % from meta-base
        """

    def xstart(self):
        from .meta import meta
        observer = self.solver.observer
        ubase, upref = "____", "_____"

        option = 1
        option = 2

        # meta_base
        meta_base = meta.Meta().reify(observer, ubase)
        # get everything that will be grounded up to this point

        # meta_pref
        print("START META_PREF")
        if option == 1:
            meta_pref = self.get_meta_pref()
        else:
            meta_pref = self.get_meta_pref2()
        print("DONE META_PREF")

        # meta_bind
        if option == 1:
            meta_bind = self.get_meta_bind1()
        else:
            meta_bind = self.get_meta_bind2()
        meta_bind += """
###bot :-  ##bot.
 ##bot :- ###bot.
:- not ###bot.
"""
        meta_bind = meta_bind.replace("###", upref)
        meta_bind = meta_bind.replace( "##", ubase)

        #
        # solve
        #
        ctl = self.solver.control
        ctl.add("conp", [], meta_base + meta_pref + meta_bind)
        ctl.ground([("conp", [])])
        count = 0
        ctl.configuration.solve.models = "0"
        with ctl.solve(yield_=True) as handle:
            for m in handle:
                print(m.symbols(shown=True))
                count += 1
            print(handle.get())
        print(count)
        self.solver.end()
        # finishes asprin

class ImproveLimitController(MethodController):

    def __init__(self, solver, controller):
        MethodController.__init__(self, solver)
        self.solver     = solver
        self.controller = controller
        self.option     = self.solver.options.improve_limit
        self.stats      = solver.control.statistics['solving']['solvers']
        self.conf       = solver.control.configuration.solve
        self.search     = 0
        # limits
        self.previous_limit, self.limit = "", 0
        # store nholds
        self.solver.store_nholds = True

    def start(self):
        self.controller.start()
        self.solver.ground_holds_delete_better()

    def start_loop(self):
        # get previous limit, and set limit
        self.previous_limit = self.conf.solve_limit
        if not self.solver.last_unsat:
            self.limit = (1 if self.search==0 else self.search) * self.option[0]
            if self.limit < self.option[2]:
                self.limit = self.option[2]
            self.conf.solve_limit = str(self.limit) + ",umax"
            if self.limit == 0: # if limit is 0, return
                return
        # call controller
        self.controller.start_loop()

    def solve(self):
        # if improving and limit is 0, return unknown
        if not self.solver.last_unsat and self.limit == 0:
            self.solver.solve_unknown()
        else:
            self.controller.solve()
        # reset previous limit
        self.conf.solve_limit = self.previous_limit
        # gather search results
        if self.solver.solving_result == utils.SATISFIABLE:
            if self.solver.last_unsat:
                self.search  = int(self.stats['conflicts'])
            elif self.option[1]:
                self.search += int(self.stats['conflicts'])

    def unsat(self):
        result = self.solver.solving_result
        self.controller.unsat()
        self.solver.handle_unknown_models(result)


#
# class OnOptimal
#

# defines (from utils)
HOLDS      = utils.HOLDS
LAST_HOLDS = utils.LAST_HOLDS
LAST_SHOWN = utils.LAST_SHOWN
POS        = utils.POS
NEG        = utils.NEG
SHOWN_ATOM = utils.SHOWN_ATOM
PREF_ATOM  = utils.PREF_ATOM
ON_OPT_HEUR_PROGRAM = utils.ON_OPT_HEUR_PROGRAM

# heuristic and external rules
HEUR_RULE = """
#heuristic ##""" + HOLDS + """(X,0) : not ##""" + LAST_HOLDS + """(X). [#v,#m]
"""
HEUR_EXTERNAL_HOLDS = """
#external ##""" + LAST_HOLDS + """(X) : X = @get_holds_domain().
"""
HEUR_EXTERNAL_SHOWN = """
#external ##""" + LAST_SHOWN + """(X) : X = @get_shown_domain().
"""

#
# Note: Option --on-opt-heur does not change anything while enumerating
#       optimal models with the same preference atoms (OPTIMUM FOUND *)
#

class OnOptimalController:

    def __init__(self, solver):
        self.solver     = solver
        self.grounded   = False
        self.heuristic  = False
        self.pref       = False
        self.shown      = False
        self.shown_rule = ""
        # for on_opt_heur
        if self.solver.options.on_opt_heur:
            self.heuristic = True
            # activate domain heuristic
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"
            # find PREF_ATOM and SHOWN_ATOM options, and update domain flags
            for sign, atom_type, value, modifier in solver.options.on_opt_heur:
                if atom_type == PREF_ATOM:
                    self.pref = True
                    self.solver.set_holds_domain = True
                elif atom_type == SHOWN_ATOM:
                    self.shown = True
                    self.solver.set_shown_domain = True

    def on(self):
        return self.heuristic

    def create_shown_heuristic_rules(self):
        # gather signatures
        sigs = set()
        for atom in self.solver.shown_domain:
            sigs.add((atom.negative, atom.name, len(atom.arguments)))
        sigs = sorted(list(sigs))
        # for every signature, add heuristics and externals
        for negative, name, arity in sigs:
            atom = ("-" if negative else "") + name
            if arity > 0:
                variables = ",".join(["X" + str(i) for i in range(arity)])
                atom += "(" + variables + ")"
            rule = HEUR_RULE.replace("##" + HOLDS + "(X,0)", atom)
            rule = rule.replace(LAST_HOLDS, LAST_SHOWN)
            rule = rule.replace("(X).", "(" + atom + ").")
            self.shown_rule += rule

    def unsat(self):

        # return if no heuristics
        if not self.heuristic:
            return
        solver = self.solver

        # ground if not grounded
        if not self.grounded:
            self.grounded = True
            # if needed: create shown heuristic rules
            if self.shown == True:
                self.create_shown_heuristic_rules()
            # create heuristic program
            program = ""
            ## iterate over options
            for sign, atom_type, value, modifier in solver.options.on_opt_heur:
                rule = HEUR_RULE
                if atom_type == SHOWN_ATOM:
                    rule = self.shown_rule
                if sign == POS:
                    rule = rule.replace(": not ", ": ")
                rule = rule.replace("#v", value)
                rule = rule.replace("#m", modifier)
                program += rule
            ## add externals
            if self.pref:
                program += HEUR_EXTERNAL_HOLDS
            if self.shown:
                program += HEUR_EXTERNAL_SHOWN
            ## replace ##
            program = program.replace("##", solver.underscores)
            # add and ground it
            solver.add_and_ground(ON_OPT_HEUR_PROGRAM, [], program, [])

        # assign externals
        if self.pref:
            solver.assign_heuristic_externals(
                solver.get_holds_domain(),
                set(solver.get_holds()),
                solver.underscores + LAST_HOLDS
            )
        if self.shown:
            solver.assign_heuristic_externals(
                solver.get_shown_domain(),
                set(solver.get_shown()),
                solver.underscores + LAST_SHOWN
            )
