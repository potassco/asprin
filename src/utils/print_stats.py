from __future__ import print_function
from src.utils import clingo_stats

class PrintStats:

    def print(self,control,models,more_models,opt_models,stats=False):
        print("")
        print("Models       : {}{}".format(models,"+" if more_models else ""))
        print("  Optimum    : {}".format("yes" if opt_models>0 else "no"))
        if opt_models > 1:
            print("  Optimal    : {}".format(opt_models))
        print(clingo_stats.Stats().summary(control,False))
        if stats:
            print(clingo_stats.Stats().statistics(control))

