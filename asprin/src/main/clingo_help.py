HELP_1="""\
clingo version 5.3.0
usage: clingo [number] [options] [files]

Clasp.Config Options:

  --configuration=<arg>   : Set default configuration [auto]
      <arg>: {auto|frumpy|jumpy|tweety|handy|crafty|trendy|many|<file>}
        auto  : Select configuration based on problem type
        frumpy: Use conservative defaults
        jumpy : Use aggressive defaults
        tweety: Use defaults geared towards asp problems
        handy : Use defaults geared towards large problems
        crafty: Use defaults geared towards crafted problems
        trendy: Use defaults geared towards industrial problems
        many  : Use default portfolio to configure solver(s)
        <file>: Use configuration file to configure solver(s)
  --tester=<options>      : Pass (quoted) string of <options> to tester
  --stats[=<n>[,<t>]],-s  : Enable {1=basic|2=full} statistics (<t> for tester)
  --[no-]parse-ext        : Enable extensions in non-aspif input
  --[no-]parse-maxsat     : Treat dimacs input as MaxSAT problem

Clasp.Solving Options:

  --parallel-mode,-t <arg>: Run parallel search with given number of threads
      <arg>: <n {1..64}>[,<mode {compete|split}>]
        <n>   : Number of threads to use in search
        <mode>: Run competition or splitting based search [compete]

  --enum-mode,-e <arg>    : Configure enumeration algorithm [auto]
      <arg>: {bt|record|brave|cautious|auto}
        bt      : Backtrack decision literals from solutions
        record  : Add nogoods for computed solutions
        domRec  : Add nogoods over true domain atoms
        brave   : Compute brave consequences (union of models)
        cautious: Compute cautious consequences (intersection of models)
        auto    : Use bt for enumeration and record for optimization
  --project[=<arg>|no]    : Enable projective solution enumeration
      <arg>: {show|project|auto}[,<bt {0..3}>] (Implicit: auto,3)
        Project to atoms in show or project directives, or
        select depending on the existence of a project directive
      <bt> : Additional options for enumeration algorithm 'bt'
        Use activity heuristic (1) when selecting backtracking literal
        and/or progress saving (2) when retracting solution literals
  --models,-n <n>         : Compute at most <n> models (0 for all)

  --opt-mode=<arg>        : Configure optimization algorithm
      <arg>: <mode {opt|enum|optN|ignore}>[,<bound>...]
        opt   : Find optimal model
        enum  : Find models with costs <= <bound>
        optN  : Find optimum, then enumerate optimal models
        ignore: Ignore optimize statements
      <bound> : Set initial bound for objective function(s)

Gringo Options:

  --text                  : Print plain text format
  --const,-c <id>=<term>  : Replace term occurrences of <id> with <term>

Basic Options:

  --help[=<n>],-h         : Print {1=basic|2=more|3=full} help and exit
  --version,-v            : Print version information and exit
  --verbose[=<n>],-V      : Set verbosity level to <n>
  --time-limit=<n>        : Set time limit to <n> seconds (0=no limit)
  --quiet[=<levels>],-q   : Configure printing of models, costs, and calls
      <levels>: <mod>[,<cost>][,<call>]
        <mod> : print {0=all|1=last|2=no} models
        <cost>: print {0=all|1=last|2=no} optimize values [<mod>]
        <call>: print {0=all|1=last|2=no} call steps      [2]
  --pre[=<fmt>]           : Print simplified program and exit
      <fmt>: Set output format to {aspif|smodels} (implicit: aspif)
  --mode=<arg>            : Run in {clingo|clasp|gringo} mode

usage: clingo [number] [options] [files]
Default command-line:
clingo --configuration=auto --enum-mode=auto --verbose=1 

Type 'clingo --help=2' for more options and defaults
and  'clingo --help=3' for all options and configurations.

clingo is part of Potassco: https://potassco.org/clingo
Get help/report bugs via : https://potassco.org/support
"""
HELP_2="""\
clingo version 5.3.0
usage: clingo [number] [options] [files]

Clasp.Config Options:

  --configuration=<arg>   : Set default configuration [auto]
      <arg>: {auto|frumpy|jumpy|tweety|handy|crafty|trendy|many|<file>}
        auto  : Select configuration based on problem type
        frumpy: Use conservative defaults
        jumpy : Use aggressive defaults
        tweety: Use defaults geared towards asp problems
        handy : Use defaults geared towards large problems
        crafty: Use defaults geared towards crafted problems
        trendy: Use defaults geared towards industrial problems
        many  : Use default portfolio to configure solver(s)
        <file>: Use configuration file to configure solver(s)
  --tester=<options>      : Pass (quoted) string of <options> to tester
  --stats[=<n>[,<t>]],-s  : Enable {1=basic|2=full} statistics (<t> for tester)
  --[no-]parse-ext        : Enable extensions in non-aspif input
  --[no-]parse-maxsat     : Treat dimacs input as MaxSAT problem

Clasp.Context Options:

  --share=<arg>|no        : Configure physical sharing of constraints [auto]
      <arg>: {auto|problem|learnt|all}
  --sat-prepro[=<arg>|no] : Run SatELite-like preprocessing (Implicit: 2)
      <arg>: <level>[,<limit>...]
        <level> : Set preprocessing level to <level  {1..3}>
          1: Variable elimination with subsumption (VE)
          2: VE with limited blocked clause elimination (BCE)
          3: Full BCE followed by VE
        <limit> : [<key {iter|occ|time|frozen|clause}>=]<n> (0=no limit)
          iter  : Set iteration limit to <n>           [0]
          occ   : Set variable occurrence limit to <n> [0]
          time  : Set time limit to <n> seconds        [0]
          frozen: Set frozen variables limit to <n>%   [0]
          size  : Set size limit to <n>*1000 clauses   [4000]

Clasp.ASP Options:

  --trans-ext=<mode>|no   : Configure handling of extended rules
      <mode>: {all|choice|card|weight|integ|dynamic}
        all    : Transform all extended rules to basic rules
        choice : Transform choice rules, but keep cardinality and weight rules
        card   : Transform cardinality rules, but keep choice and weight rules
        weight : Transform cardinality and weight rules, but keep choice rules
        scc    : Transform "recursive" cardinality and weight rules
        integ  : Transform cardinality integrity constraints
        dynamic: Transform "simple" extended rules, but keep more complex ones
  --eq=<n>                : Configure equivalence preprocessing
      Run for at most <n> iterations (-1=run to fixpoint)
  --[no-]backprop         : Use backpropagation in ASP-preprocessing
  --supp-models           : Compute supported models
  --no-ufs-check          : Disable unfounded set check
  --no-gamma              : Do not add gamma rules for non-hcf disjunctions

Clasp.Solving Options:

  --solve-limit=<n>[,<m>] : Stop search after <n> conflicts or <m> restarts

  --parallel-mode,-t <arg>: Run parallel search with given number of threads
      <arg>: <n {1..64}>[,<mode {compete|split}>]
        <n>   : Number of threads to use in search
        <mode>: Run competition or splitting based search [compete]

  --global-restarts=<X>   : Configure global restart policy
      <X>: <n>[,<sched>]
        <n> : Maximal number of global restarts (0=disable)
     <sched>: Restart schedule [x,100,1.5] (<type {F|L|x|+}>)

  --distribute=<arg>|no   : Configure nogood distribution [conflict,global,4]
      <arg>: <type>[,<mode>][,<lbd {0..127}>][,<size>]
        <type> : Distribute {all|short|conflict|loop} nogoods
        <mode> : Use {global|local} distribution   [global]
        <lbd>  : Distribute only if LBD  <= <lbd>  [4]
        <size> : Distribute only if size <= <size> [-1]
  --integrate=<arg>       : Configure nogood integration [gp]
      <arg>: <pick>[,<n>][,<topo>]
        <pick>: Add {all|unsat|gp(unsat wrt guiding path)|active} nogoods
        <n>   : Always keep at least last <n> integrated nogoods   [1024]
        <topo>: Accept nogoods from {all|ring|cube|cubex} peers    [all]

  --enum-mode,-e <arg>    : Configure enumeration algorithm [auto]
      <arg>: {bt|record|brave|cautious|auto}
        bt      : Backtrack decision literals from solutions
        record  : Add nogoods for computed solutions
        domRec  : Add nogoods over true domain atoms
        brave   : Compute brave consequences (union of models)
        cautious: Compute cautious consequences (intersection of models)
        auto    : Use bt for enumeration and record for optimization
  --project[=<arg>|no]    : Enable projective solution enumeration
      <arg>: {show|project|auto}[,<bt {0..3}>] (Implicit: auto,3)
        Project to atoms in show or project directives, or
        select depending on the existence of a project directive
      <bt> : Additional options for enumeration algorithm 'bt'
        Use activity heuristic (1) when selecting backtracking literal
        and/or progress saving (2) when retracting solution literals
  --models,-n <n>         : Compute at most <n> models (0 for all)

  --opt-mode=<arg>        : Configure optimization algorithm
      <arg>: <mode {opt|enum|optN|ignore}>[,<bound>...]
        opt   : Find optimal model
        enum  : Find models with costs <= <bound>
        optN  : Find optimum, then enumerate optimal models
        ignore: Ignore optimize statements
      <bound> : Set initial bound for objective function(s)

Clasp.Search Options:

  --opt-strategy=<arg>    : Configure optimization strategy
      <arg>: {bb|usc}[,<tactics>]
        bb : Model-guided optimization with <tactics {lin|hier|inc|dec}> [lin]
          lin : Basic lexicographical descent
          hier: Hierarchical (highest priority criteria first) descent 
          inc : Hierarchical descent with exponentially increasing steps
          dec : Hierarchical descent with exponentially decreasing steps
        usc: Core-guided optimization with <tactics>: <relax>[,<opts>]
          <relax>: Relaxation algorithm {oll|one|k|pmres}                [oll]
            oll    : Use strategy from unclasp
            one    : Add one cardinality constraint per core
            k[,<n>]: Add cardinality constraints of bounded size ([0]=dynamic)
            pmres  : Add clauses of size 3
          <opts> : Tactics <list {disjoint|succinct|stratify}>|<mask {0..7}>
            disjoint: Disjoint-core preprocessing                    (1)
            succinct: No redundant (symmetry) constraints            (2)
            stratify: Stratification heuristic for handling weights  (4)
  --opt-usc-shrink=<arg>  : Enable core-shrinking in core-guided optimization
      <arg>: <algo>[,<limit> (0=no limit)]
        <algo> : Use algorithm {lin|inv|bin|rgs|exp|min}
          lin  : Forward linear search unsat
          inv  : Inverse linear search not unsat
          bin  : Binary search
          rgs  : Repeated geometric sequence until unsat
          exp  : Exponential search until unsat
          min  : Linear search for subset minimal core
        <limit>: Limit solve calls to 2^<n> conflicts [10]
  --opt-heuristic=<list>  : Use opt. in <list {sign|model}> heuristics
  --[no-]restart-on-model : Restart after each model

  --lookahead[=<arg>|no]  : Configure failed-literal detection (fld)
      <arg>: <type>[,<limit>] / Implicit: atom
        <type> : Run fld via {atom|body|hybrid} lookahead
        <limit>: Disable fld after <limit> applications ([0]=no limit)
      --lookahead=atom is default if --no-lookback is used

  --heuristic=<heu>       : Configure decision heuristic
      <heu>: {Berkmin|Vmtf|Vsids|Domain|Unit|None}[,<n>]
        Berkmin: Use BerkMin-like heuristic (Check last <n> nogoods [0]=all)
        Vmtf   : Use Siege-like heuristic (Move <n> literals to the front [8])
        Vsids  : Use Chaff-like heuristic (Use 1.0/0.<n> as decay factor  [95])
        Domain : Use domain knowledge in Vsids-like heuristic
        Unit   : Use Smodels-like heuristic (Default if --no-lookback)
        None   : Select the first free variable
  --sign-def=<sign>       : Default sign: {asp|pos|neg|rnd}
  --dom-mod=<arg>         : Default modification for domain heuristic
      <arg>: (no|<mod>[,<pick>])
        <mod>  : Modifier {level|pos|true|neg|false|init|factor}
        <pick> : Apply <mod> to (all | <list {scc|hcc|disj|opt|show}>) atoms
  --save-progress[=<n>]   : Use RSat-like progress saving on backjumps > <n>
  --seed=<n>              : Set random number generator's seed to <n>
  --partial-check[=<arg>] : Configure partial stability tests
      <arg>: <p>[,<h>] / Implicit: 50
        <p>: Partial check skip percentage
        <h>: Init/update value for high bound ([0]=umax)
  --rand-freq=<p>|no      : Make random decisions with probability <p>
  --rand-prob=<n>[,<m>]   : Do <n> random searches with [<m>=100] conflicts

Clasp.Lookback Options:

  --no-lookback           : Disable all lookback strategies

  --forget-on-step=<opts> : Configure forgetting on (incremental) step
      <opts>: <list {varScores|signs|lemmaScores|lemmas}>|<mask {0..15}>

  --strengthen=<X>|no     : Use MiniSAT-like conflict nogood strengthening
      <X>: <mode>[,<type>][,<bump {yes|no}>]
        <mode>: Use {local|recursive} self-subsumption check
        <type>: Follow {all|short|binary} antecedents [all]
        <bump>: Bump activities of antecedents        [yes]
  --otfs[={0..2}]         : Enable {1=partial|2=full} on-the-fly subsumption
  --reverse-arcs[={0..3}] : Enable ManySAT-like inverse-arc learning
  --loops=<type>          : Configure learning of loop nogoods
      <type>: {common|distinct|shared|no}
        common  : Create loop nogoods for atoms in an unfounded set
        distinct: Create distinct loop nogood for each atom in an unfounded set
        shared  : Create loop formula for a whole unfounded set
        no      : Do not learn loop formulas

  --restarts,-r <sched>|no: Configure restart policy
      <sched>: <type {D|F|L|x|+}>,<n {1..umax}>[,<args>][,<lim>]
        F,<n>    : Run fixed sequence of <n> conflicts
        L,<n>    : Run Luby et al.'s sequence with unit length <n>
        x,<n>,<f>: Run geometric seq. of <n>*(<f>^i) conflicts  (<f> >= 1.0)
        +,<n>,<m>: Run arithmetic seq. of <n>+(<m>*i) conflicts (<m {0..umax}>)
        ...,<lim>: Repeat seq. every <lim>+j restarts           (<type> != F)
        D,<n>,<f>: Restart based on moving LBD average over last <n> conflicts
                   Mavg(<n>,LBD)*<f> > avg(LBD)
                   use conflict level average if <lim> > 0 and avg(LBD) > <lim>
      no|0       : Disable restarts
  --[no-]local-restarts   : Use Ryvchin et al.'s local restarts
  --counter-restarts=<arg>: Use counter implication restarts
      <arg>: (<rate>[,<bump>] | {0|no})
      <rate>: Interval in number of restarts
      <bump>: Bump factor applied to indegrees
  --block-restarts=<arg>  : Use glucose-style blocking restarts
      <arg>: <n>[,<R {1.0..5.0}>][,<c>]
        <n>: Window size for moving average (0=disable blocking)
        <R>: Block restart if assignment > average * <R>  [1.4]
        <c>: Disable blocking for the first <c> conflicts [10000]

  --shuffle=<n1>,<n2>|no  : Shuffle problem after <n1>+(<n2>*i) restarts

  --deletion,-d <arg>|no  : Configure deletion algorithm [basic,75,0]
      <arg>: <algo>[,<n {1..100}>][,<sc>]
        <algo>: Use {basic|sort|ipSort|ipHeap} algorithm
        <n>   : Delete at most <n>% of nogoods on reduction    [75]
        <sc>  : Use {activity|lbd|mixed} nogood scores    [activity]
      no      : Disable nogood deletion
  --del-grow=<arg>|no     : Configure size-based deletion policy
      <arg>: <f>[,<g>][,<sched>] (<f> >= 1.0)
        <f>     : Keep at most T = X*(<f>^i) learnt nogoods with X being the
                  initial limit and i the number of times <sched> fired
        <g>     : Stop growth once T > P*<g> (0=no limit)      [3.0]
        <sched> : Set grow schedule (<type {F|L|x|+}>) [grow on restart]
  --del-cfl=<sched>|no    : Configure conflict-based deletion policy
      <sched>:   <type {F|L|x|+}>,<args>... (see restarts)
  --del-init=<arg>        : Configure initial deletion limit
      <arg>: <f>[,<n>,<o>] (<f> > 0)
        <f>    : Set initial limit to P=estimated problem size/<f> [3.0]
        <n>,<o>: Clamp initial limit to the range [<n>,<n>+<o>]
  --del-estimate[=0..3]   : Use estimated problem complexity in limits
  --del-max=<n>,<X>|no    : Keep at most <n> learnt nogoods taking up to <X> MB
  --del-glue=<arg>        : Configure glue clause handling
      <arg>: <n {0..15}>[,<m {0|1}>]
        <n>: Do not delete nogoods with LBD <= <n>
        <m>: Count (0) or ignore (1) glue clauses in size limit [0]
  --del-on-restart=<n>    : Delete <n>% of learnt nogoods on each restart

Gringo Options:

  --text                  : Print plain text format
  --const,-c <id>=<term>  : Replace term occurrences of <id> with <term>
  --output,-o <arg>       : Choose output format:
      intermediate: print intermediate format
      text        : print plain text format
      reify       : print program as reified facts
      smodels     : print smodels format
                    (only supports basic features)
  --output-debug=<arg>    : Print debug information during output:
      none     : no additional info
      text     : print rules as plain text (prefix %)
      translate: print translated rules as plain text (prefix %%)
      all      : combines text and translate
  --warn,-W <warn>        : Enable/disable warnings:
      none:                     disable all warnings
      all:                      enable all warnings
      [no-]atom-undefined:      a :- b.
      [no-]file-included:       #include "a.lp". #include "a.lp".
      [no-]operation-undefined: p(1/0).
      [no-]variable-unbounded:  $x > 10.
      [no-]global-variable:     :- #count { X } = 1, X = 1.
      [no-]other:               clasp related and uncategorized warnings
  --rewrite-minimize      : Rewrite minimize constraints into rules
  --keep-facts            : Do not remove facts from normal rules
  --reify-sccs            : Calculate SCCs for reified output
  --reify-steps           : Add step numbers to reified output

Basic Options:

  --help[=<n>],-h         : Print {1=basic|2=more|3=full} help and exit
  --version,-v            : Print version information and exit
  --verbose[=<n>],-V      : Set verbosity level to <n>
  --time-limit=<n>        : Set time limit to <n> seconds (0=no limit)
  --fast-exit             : Force fast exit (do not call dtors)
  --print-portfolio       : Print default portfolio and exit
  --quiet[=<levels>],-q   : Configure printing of models, costs, and calls
      <levels>: <mod>[,<cost>][,<call>]
        <mod> : print {0=all|1=last|2=no} models
        <cost>: print {0=all|1=last|2=no} optimize values [<mod>]
        <call>: print {0=all|1=last|2=no} call steps      [2]
  --pre[=<fmt>]           : Print simplified program and exit
      <fmt>: Set output format to {aspif|smodels} (implicit: aspif)
  --outf=<n>              : Use {0=default|1=competition|2=JSON|3=no} output
  --out-hide-aux          : Hide auxiliary atoms in answers
  --lemma-in=<file>       : Read additional lemmas from <file>
  --lemma-out=<file>      : Log learnt lemmas to <file>
  --mode=<arg>            : Run in {clingo|clasp|gringo} mode

usage: clingo [number] [options] [files]
Default command-line:
clingo --configuration=auto --share=auto --distribute=conflict,global,4 
       --integrate=gp --enum-mode=auto --deletion=basic,75,0 --del-init=3.0 
       --verbose=1 
[asp] --configuration=tweety
[cnf] --configuration=trendy
[opb] --configuration=trendy

Type  'clingo --help=3' for all options and configurations.

clingo is part of Potassco: https://potassco.org/clingo
Get help/report bugs via : https://potassco.org/support
"""
HELP_3="""\
clingo version 5.3.0
usage: clingo [number] [options] [files]

Clasp.Config Options:

  --configuration=<arg>   : Set default configuration [auto]
      <arg>: {auto|frumpy|jumpy|tweety|handy|crafty|trendy|many|<file>}
        auto  : Select configuration based on problem type
        frumpy: Use conservative defaults
        jumpy : Use aggressive defaults
        tweety: Use defaults geared towards asp problems
        handy : Use defaults geared towards large problems
        crafty: Use defaults geared towards crafted problems
        trendy: Use defaults geared towards industrial problems
        many  : Use default portfolio to configure solver(s)
        <file>: Use configuration file to configure solver(s)
  --tester=<options>      : Pass (quoted) string of <options> to tester
  --stats[=<n>[,<t>]],-s  : Enable {1=basic|2=full} statistics (<t> for tester)
  --[no-]parse-ext        : Enable extensions in non-aspif input
  --[no-]parse-maxsat     : Treat dimacs input as MaxSAT problem

Clasp.Context Options:

  --share=<arg>|no        : Configure physical sharing of constraints [auto]
      <arg>: {auto|problem|learnt|all}
  --learn-explicit        : Do not use Short Implication Graph for learning
  --sat-prepro[=<arg>|no] : Run SatELite-like preprocessing (Implicit: 2)
      <arg>: <level>[,<limit>...]
        <level> : Set preprocessing level to <level  {1..3}>
          1: Variable elimination with subsumption (VE)
          2: VE with limited blocked clause elimination (BCE)
          3: Full BCE followed by VE
        <limit> : [<key {iter|occ|time|frozen|clause}>=]<n> (0=no limit)
          iter  : Set iteration limit to <n>           [0]
          occ   : Set variable occurrence limit to <n> [0]
          time  : Set time limit to <n> seconds        [0]
          frozen: Set frozen variables limit to <n>%   [0]
          size  : Set size limit to <n>*1000 clauses   [4000]

Clasp.ASP Options:

  --trans-ext=<mode>|no   : Configure handling of extended rules
      <mode>: {all|choice|card|weight|integ|dynamic}
        all    : Transform all extended rules to basic rules
        choice : Transform choice rules, but keep cardinality and weight rules
        card   : Transform cardinality rules, but keep choice and weight rules
        weight : Transform cardinality and weight rules, but keep choice rules
        scc    : Transform "recursive" cardinality and weight rules
        integ  : Transform cardinality integrity constraints
        dynamic: Transform "simple" extended rules, but keep more complex ones
  --eq=<n>                : Configure equivalence preprocessing
      Run for at most <n> iterations (-1=run to fixpoint)
  --[no-]backprop         : Use backpropagation in ASP-preprocessing
  --supp-models           : Compute supported models
  --no-ufs-check          : Disable unfounded set check
  --no-gamma              : Do not add gamma rules for non-hcf disjunctions
  --eq-dfs                : Enable df-order in eq-preprocessing

Clasp.Solving Options:

  --solve-limit=<n>[,<m>] : Stop search after <n> conflicts or <m> restarts

  --parallel-mode,-t <arg>: Run parallel search with given number of threads
      <arg>: <n {1..64}>[,<mode {compete|split}>]
        <n>   : Number of threads to use in search
        <mode>: Run competition or splitting based search [compete]

  --global-restarts=<X>   : Configure global restart policy
      <X>: <n>[,<sched>]
        <n> : Maximal number of global restarts (0=disable)
     <sched>: Restart schedule [x,100,1.5] (<type {F|L|x|+}>)

  --distribute=<arg>|no   : Configure nogood distribution [conflict,global,4]
      <arg>: <type>[,<mode>][,<lbd {0..127}>][,<size>]
        <type> : Distribute {all|short|conflict|loop} nogoods
        <mode> : Use {global|local} distribution   [global]
        <lbd>  : Distribute only if LBD  <= <lbd>  [4]
        <size> : Distribute only if size <= <size> [-1]
  --integrate=<arg>       : Configure nogood integration [gp]
      <arg>: <pick>[,<n>][,<topo>]
        <pick>: Add {all|unsat|gp(unsat wrt guiding path)|active} nogoods
        <n>   : Always keep at least last <n> integrated nogoods   [1024]
        <topo>: Accept nogoods from {all|ring|cube|cubex} peers    [all]

  --enum-mode,-e <arg>    : Configure enumeration algorithm [auto]
      <arg>: {bt|record|brave|cautious|auto}
        bt      : Backtrack decision literals from solutions
        record  : Add nogoods for computed solutions
        domRec  : Add nogoods over true domain atoms
        brave   : Compute brave consequences (union of models)
        cautious: Compute cautious consequences (intersection of models)
        auto    : Use bt for enumeration and record for optimization
  --project[=<arg>|no]    : Enable projective solution enumeration
      <arg>: {show|project|auto}[,<bt {0..3}>] (Implicit: auto,3)
        Project to atoms in show or project directives, or
        select depending on the existence of a project directive
      <bt> : Additional options for enumeration algorithm 'bt'
        Use activity heuristic (1) when selecting backtracking literal
        and/or progress saving (2) when retracting solution literals
  --models,-n <n>         : Compute at most <n> models (0 for all)

  --opt-mode=<arg>        : Configure optimization algorithm
      <arg>: <mode {opt|enum|optN|ignore}>[,<bound>...]
        opt   : Find optimal model
        enum  : Find models with costs <= <bound>
        optN  : Find optimum, then enumerate optimal models
        ignore: Ignore optimize statements
      <bound> : Set initial bound for objective function(s)

Clasp.Search Options:

  --opt-strategy=<arg>    : Configure optimization strategy
      <arg>: {bb|usc}[,<tactics>]
        bb : Model-guided optimization with <tactics {lin|hier|inc|dec}> [lin]
          lin : Basic lexicographical descent
          hier: Hierarchical (highest priority criteria first) descent 
          inc : Hierarchical descent with exponentially increasing steps
          dec : Hierarchical descent with exponentially decreasing steps
        usc: Core-guided optimization with <tactics>: <relax>[,<opts>]
          <relax>: Relaxation algorithm {oll|one|k|pmres}                [oll]
            oll    : Use strategy from unclasp
            one    : Add one cardinality constraint per core
            k[,<n>]: Add cardinality constraints of bounded size ([0]=dynamic)
            pmres  : Add clauses of size 3
          <opts> : Tactics <list {disjoint|succinct|stratify}>|<mask {0..7}>
            disjoint: Disjoint-core preprocessing                    (1)
            succinct: No redundant (symmetry) constraints            (2)
            stratify: Stratification heuristic for handling weights  (4)
  --opt-usc-shrink=<arg>  : Enable core-shrinking in core-guided optimization
      <arg>: <algo>[,<limit> (0=no limit)]
        <algo> : Use algorithm {lin|inv|bin|rgs|exp|min}
          lin  : Forward linear search unsat
          inv  : Inverse linear search not unsat
          bin  : Binary search
          rgs  : Repeated geometric sequence until unsat
          exp  : Exponential search until unsat
          min  : Linear search for subset minimal core
        <limit>: Limit solve calls to 2^<n> conflicts [10]
  --opt-heuristic=<list>  : Use opt. in <list {sign|model}> heuristics
  --[no-]restart-on-model : Restart after each model

  --lookahead[=<arg>|no]  : Configure failed-literal detection (fld)
      <arg>: <type>[,<limit>] / Implicit: atom
        <type> : Run fld via {atom|body|hybrid} lookahead
        <limit>: Disable fld after <limit> applications ([0]=no limit)
      --lookahead=atom is default if --no-lookback is used

  --heuristic=<heu>       : Configure decision heuristic
      <heu>: {Berkmin|Vmtf|Vsids|Domain|Unit|None}[,<n>]
        Berkmin: Use BerkMin-like heuristic (Check last <n> nogoods [0]=all)
        Vmtf   : Use Siege-like heuristic (Move <n> literals to the front [8])
        Vsids  : Use Chaff-like heuristic (Use 1.0/0.<n> as decay factor  [95])
        Domain : Use domain knowledge in Vsids-like heuristic
        Unit   : Use Smodels-like heuristic (Default if --no-lookback)
        None   : Select the first free variable
  --[no-]init-moms        : Initialize heuristic with MOMS-score
  --score-res=<score>     : Resolution score {auto|min|set|multiset}
  --score-other=<arg>     : Score other learnt nogoods: {auto|no|loop|all}
  --sign-def=<sign>       : Default sign: {asp|pos|neg|rnd}
  --[no-]sign-fix         : Disable sign heuristics and use default signs only
  --[no-]berk-huang       : Enable Huang-scoring in Berkmin
  --[no-]vsids-acids      : Enable acids-scheme in Vsids/Domain
  --vsids-progress=<arg>  : Enable dynamic decaying scheme in Vsids/Domain
      <arg>: <n>[,<i {1..100}>][,<c>]|(0=disable)
        <n> : Set initial decay factor to 1.0/0.<n>
        <i> : Set decay update to <i>/100.0      [1]
        <c> : Decrease decay every <c> conflicts [5000]
  --[no-]nant             : Prefer negative antecedents of P in heuristic
  --dom-mod=<arg>         : Default modification for domain heuristic
      <arg>: (no|<mod>[,<pick>])
        <mod>  : Modifier {level|pos|true|neg|false|init|factor}
        <pick> : Apply <mod> to (all | <list {scc|hcc|disj|opt|show}>) atoms
  --save-progress[=<n>]   : Use RSat-like progress saving on backjumps > <n>
  --init-watches=<arg>    : Watched literal initialization: {rnd|first|least}
  --update-mode=<mode>    : Process messages on {propagate|conflict}
  --acyc-prop[={0..1}]    : Use backward inference in acyc propagation
  --seed=<n>              : Set random number generator's seed to <n>
  --partial-check[=<arg>] : Configure partial stability tests
      <arg>: <p>[,<h>] / Implicit: 50
        <p>: Partial check skip percentage
        <h>: Init/update value for high bound ([0]=umax)
  --sign-def-disj=<sign>  : Default sign for atoms in disjunctions
  --rand-freq=<p>|no      : Make random decisions with probability <p>
  --rand-prob=<n>[,<m>]   : Do <n> random searches with [<m>=100] conflicts

Clasp.Lookback Options:

  --no-lookback           : Disable all lookback strategies

  --forget-on-step=<opts> : Configure forgetting on (incremental) step
      <opts>: <list {varScores|signs|lemmaScores|lemmas}>|<mask {0..15}>

  --strengthen=<X>|no     : Use MiniSAT-like conflict nogood strengthening
      <X>: <mode>[,<type>][,<bump {yes|no}>]
        <mode>: Use {local|recursive} self-subsumption check
        <type>: Follow {all|short|binary} antecedents [all]
        <bump>: Bump activities of antecedents        [yes]
  --otfs[={0..2}]         : Enable {1=partial|2=full} on-the-fly subsumption
  --update-lbd=<arg>|no   : Configure LBD updates during conflict resolution
      <arg>: <mode {less|glucose|pseudo}>[,<n {0..127}>]
        less   : update to X = new LBD   iff X   < previous LBD
        glucose: update to X = new LBD   iff X+1 < previous LBD
        pseudo : update to X = new LBD+1 iff X   < previous LBD
           <n> : Protect updated nogoods on next reduce if X <= <n>
  --update-act            : Enable LBD-based activity bumping
  --reverse-arcs[={0..3}] : Enable ManySAT-like inverse-arc learning
  --contraction=<arg>|no  : Configure handling of long learnt nogoods
      <arg>: <n>[,<rep>]
        <n>  : Contract nogoods if size > <n> (0=disable)
        <rep>: Nogood replacement {no|decisionSeq|allUIP|dynamic} [no]

  --loops=<type>          : Configure learning of loop nogoods
      <type>: {common|distinct|shared|no}
        common  : Create loop nogoods for atoms in an unfounded set
        distinct: Create distinct loop nogood for each atom in an unfounded set
        shared  : Create loop formula for a whole unfounded set
        no      : Do not learn loop formulas

  --restarts,-r <sched>|no: Configure restart policy
      <sched>: <type {D|F|L|x|+}>,<n {1..umax}>[,<args>][,<lim>]
        F,<n>    : Run fixed sequence of <n> conflicts
        L,<n>    : Run Luby et al.'s sequence with unit length <n>
        x,<n>,<f>: Run geometric seq. of <n>*(<f>^i) conflicts  (<f> >= 1.0)
        +,<n>,<m>: Run arithmetic seq. of <n>+(<m>*i) conflicts (<m {0..umax}>)
        ...,<lim>: Repeat seq. every <lim>+j restarts           (<type> != F)
        D,<n>,<f>: Restart based on moving LBD average over last <n> conflicts
                   Mavg(<n>,LBD)*<f> > avg(LBD)
                   use conflict level average if <lim> > 0 and avg(LBD) > <lim>
      no|0       : Disable restarts
  --reset-restarts=<arg>  : Update restart seq. on model {no|repeat|disable}
  --[no-]local-restarts   : Use Ryvchin et al.'s local restarts
  --counter-restarts=<arg>: Use counter implication restarts
      <arg>: (<rate>[,<bump>] | {0|no})
      <rate>: Interval in number of restarts
      <bump>: Bump factor applied to indegrees
  --block-restarts=<arg>  : Use glucose-style blocking restarts
      <arg>: <n>[,<R {1.0..5.0}>][,<c>]
        <n>: Window size for moving average (0=disable blocking)
        <R>: Block restart if assignment > average * <R>  [1.4]
        <c>: Disable blocking for the first <c> conflicts [10000]

  --shuffle=<n1>,<n2>|no  : Shuffle problem after <n1>+(<n2>*i) restarts

  --deletion,-d <arg>|no  : Configure deletion algorithm [basic,75,0]
      <arg>: <algo>[,<n {1..100}>][,<sc>]
        <algo>: Use {basic|sort|ipSort|ipHeap} algorithm
        <n>   : Delete at most <n>% of nogoods on reduction    [75]
        <sc>  : Use {activity|lbd|mixed} nogood scores    [activity]
      no      : Disable nogood deletion
  --del-grow=<arg>|no     : Configure size-based deletion policy
      <arg>: <f>[,<g>][,<sched>] (<f> >= 1.0)
        <f>     : Keep at most T = X*(<f>^i) learnt nogoods with X being the
                  initial limit and i the number of times <sched> fired
        <g>     : Stop growth once T > P*<g> (0=no limit)      [3.0]
        <sched> : Set grow schedule (<type {F|L|x|+}>) [grow on restart]
  --del-cfl=<sched>|no    : Configure conflict-based deletion policy
      <sched>:   <type {F|L|x|+}>,<args>... (see restarts)
  --del-init=<arg>        : Configure initial deletion limit
      <arg>: <f>[,<n>,<o>] (<f> > 0)
        <f>    : Set initial limit to P=estimated problem size/<f> [3.0]
        <n>,<o>: Clamp initial limit to the range [<n>,<n>+<o>]
  --del-estimate[=0..3]   : Use estimated problem complexity in limits
  --del-max=<n>,<X>|no    : Keep at most <n> learnt nogoods taking up to <X> MB
  --del-glue=<arg>        : Configure glue clause handling
      <arg>: <n {0..15}>[,<m {0|1}>]
        <n>: Do not delete nogoods with LBD <= <n>
        <m>: Count (0) or ignore (1) glue clauses in size limit [0]
  --del-on-restart=<n>    : Delete <n>% of learnt nogoods on each restart

Gringo Options:

  --text                  : Print plain text format
  --const,-c <id>=<term>  : Replace term occurrences of <id> with <term>
  --output,-o <arg>       : Choose output format:
      intermediate: print intermediate format
      text        : print plain text format
      reify       : print program as reified facts
      smodels     : print smodels format
                    (only supports basic features)
  --output-debug=<arg>    : Print debug information during output:
      none     : no additional info
      text     : print rules as plain text (prefix %)
      translate: print translated rules as plain text (prefix %%)
      all      : combines text and translate
  --warn,-W <warn>        : Enable/disable warnings:
      none:                     disable all warnings
      all:                      enable all warnings
      [no-]atom-undefined:      a :- b.
      [no-]file-included:       #include "a.lp". #include "a.lp".
      [no-]operation-undefined: p(1/0).
      [no-]variable-unbounded:  $x > 10.
      [no-]global-variable:     :- #count { X } = 1, X = 1.
      [no-]other:               clasp related and uncategorized warnings
  --rewrite-minimize      : Rewrite minimize constraints into rules
  --keep-facts            : Do not remove facts from normal rules
  --reify-sccs            : Calculate SCCs for reified output
  --reify-steps           : Add step numbers to reified output

Basic Options:

  --help[=<n>],-h         : Print {1=basic|2=more|3=full} help and exit
  --version,-v            : Print version information and exit
  --verbose[=<n>],-V      : Set verbosity level to <n>
  --time-limit=<n>        : Set time limit to <n> seconds (0=no limit)
  --fast-exit             : Force fast exit (do not call dtors)
  --print-portfolio       : Print default portfolio and exit
  --quiet[=<levels>],-q   : Configure printing of models, costs, and calls
      <levels>: <mod>[,<cost>][,<call>]
        <mod> : print {0=all|1=last|2=no} models
        <cost>: print {0=all|1=last|2=no} optimize values [<mod>]
        <call>: print {0=all|1=last|2=no} call steps      [2]
  --pre[=<fmt>]           : Print simplified program and exit
      <fmt>: Set output format to {aspif|smodels} (implicit: aspif)
  --outf=<n>              : Use {0=default|1=competition|2=JSON|3=no} output
  --out-atomf=<arg>       : Set atom format string (<Pre>?%0<Post>?)
  --out-ifs=<arg>         : Set internal field separator
  --out-hide-aux          : Hide auxiliary atoms in answers
  --lemma-in=<file>       : Read additional lemmas from <file>
  --lemma-out=<file>      : Log learnt lemmas to <file>
  --lemma-out-lbd=<n>     : Only log lemmas with lbd <= <n>
  --lemma-out-max=<n>     : Stop logging after <n> lemmas
  --lemma-out-dom=<arg>   : Log lemmas over <arg {input|output}> variables
  --lemma-out-txt         : Log lemmas as ground integrity constraints
  --hcc-out=<file>        : Write non-hcf programs to <file>.#scc
  --compute=<lit>         : Force given literal to true
  --mode=<arg>            : Run in {clingo|clasp|gringo} mode

usage: clingo [number] [options] [files]
Default command-line:
clingo --configuration=auto --share=auto --distribute=conflict,global,4 
       --integrate=gp --enum-mode=auto --deletion=basic,75,0 --del-init=3.0 
       --verbose=1 
[asp] --configuration=tweety
[cnf] --configuration=trendy
[opb] --configuration=trendy

Default configurations:
[tweety]:
 --eq=3 --trans-ext=dynamic --heuristic=Vsids,92 --restarts=L,60
 --deletion=basic,50 --del-max=2000000 --del-estimate=1 --del-cfl=+,2000,100,20
 --del-grow=0 --del-glue=2,0 --strengthen=recursive,all --otfs=2 --init-moms
 --score-other=all --update-lbd=less --save-progress=160 --init-watches=least
 --local-restarts --loops=shared
[trendy]:
 --sat-p=2,iter=20,occ=25,time=240 --trans-ext=dynamic --heuristic=Vsids
 --restarts=D,100,0.7 --deletion=basic,50 --del-init=3.0,500,19500
 --del-grow=1.1,20.0,x,100,1.5 --del-cfl=+,10000,2000 --del-glue=2
 --strengthen=recursive --update-lbd=less --otfs=2 --save-p=75
 --counter-restarts=3,1023 --reverse-arcs=2 --contraction=250 --loops=common
[frumpy]:
 --eq=5 --heuristic=Berkmin --restarts=x,100,1.5 --deletion=basic,75
 --del-init=3.0,200,40000 --del-max=400000 --contraction=250 --loops=common
 --save-p=180 --del-grow=1.1 --strengthen=local --sign-def-disj=pos
[crafty]:
 --sat-p=2,iter=10,occ=25,time=240 --trans-ext=dynamic --backprop
 --heuristic=Vsids --save-p=180 --restarts=x,128,1.5 --deletion=basic,75
 --del-init=10.0,1000,9000 --del-grow=1.1,20.0 --del-cfl=+,10000,1000
 --del-glue=2 --otfs=2 --reverse-arcs=1 --counter-restarts=3,9973
 --contraction=250
[jumpy]:
 --sat-p=2,iter=20,occ=25,time=240 --trans-ext=dynamic --heuristic=Vsids
 --restarts=L,100 --deletion=basic,75,mixed --del-init=3.0,1000,20000
 --del-grow=1.1,25,x,100,1.5 --del-cfl=x,10000,1.1 --del-glue=2
 --update-lbd=glucose --strengthen=recursive --otfs=2 --save-p=70
[handy]:
 --sat-p=2,iter=10,occ=25,time=240 --trans-ext=dynamic --backprop
 --heuristic=Vsids --restarts=D,100,0.7 --deletion=sort,50,mixed
 --del-max=200000 --del-init=20.0,1000,14000 --del-cfl=+,4000,600 --del-glue=2
 --update-lbd=less --strengthen=recursive --otfs=2 --save-p=20
 --contraction=600 --loops=distinct --counter-restarts=7,1023 --reverse-arcs=2

clingo is part of Potassco: https://potassco.org/clingo
Get help/report bugs via : https://potassco.org/support
"""
