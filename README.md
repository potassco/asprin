# asprin
> A general framework for qualitative and quantitative optimization in answer set programming.

## Description
`asprin` is a general framework for optimization in ASP that allows:
* computing optimal stable models of logic programs with preferences, and
* defining new preference types in a very easy way.
Some preference types (`subset`, `pareto`...) are already defined in `asprin`'s library,
but many more can be defined simply writing a logic program.

For a formal description of `asprin`, please read our [paper](http://www.cs.uni-potsdam.de/wv/pdfformat/brderosc15a.pdf) ([bibtex](http://www.cs.uni-potsdam.de/wv/bibtex/brderosc15a.bib)).

Starting with version 3, asprin is documented in the [Potassco guide](https://github.com/potassco/guide/releases/).
Older versions are documented in the [Potassco guide on Sourceforge](https://sourceforge.net/projects/potassco/files/guide/).


## Usage
```bash
$ asprin [number_of_models] [options] [files]
```
By default, asprin loads its library `asprin_lib.lp`. This may be disabled with option `--no-asprin-lib`.

Option `--help` prints help.

## Building
`asprin` requires Python (version 2.7 is tested), and 
the python module of [clingo](https://github.com/potassco/clingo) (version 5.2.2 is tested),
whose directory should be in the environment variable `PYTHONPATH`:

* On Windows, 
you can download the corresponding [clingo release](https://github.com/potassco/clingo/releases/download/v5.2.2/clingo-5.2.2-win64.zip), 
uncompress it in some directory `dir`,
and set `PYTHONPATH` to `dir\clingo-5.2.2-win64\python-api` (with `set PYTHONPATH=dir\clingo-5.2.2-win64\python-api`).

* On Mac, 
you can download the corresponding [clingo release](https://github.com/potassco/clingo/releases/download/v5.2.2/clingo-5.2.2-macos-10.9.tar.gz), 
uncompress it in some directory `dir`,
and set `PYTHONPATH` to `dir\clingo-5.2.2-macos-10.9\python-api` (with `export PYTHONPATH=dir\clingo-5.2.2-macos-10.9\python-api`).

* On Unix, you can download the [source code](https://github.com/potassco/clingo/archive/v5.2.2.tar.gz), 
build it following the instructions in `INSTALL.md`, and set `PYTHONPATH` accordingly.

`asprin` can be installed with [pip](https://pip.pypa.io) via
```pip install asprin```. 

For a local installation, add option ```--user```.
In this case, setting environment variable `PYTHONUSERBASE` to `dir` before running `pip`, 
`asprin` will be installed in `dir/bin/asprin`.

If that does not work, 
you can always download the sources from [here](https://github.com/potassco/asprin/releases/download/v3.0.3/asprin-3.0.3.tar.gz) in some directory `dir`,
and run `asprin` with `python dir/asprin/asprin/asprin.py`.

System tests may be run with ```asprin --test``` and ```asprin --test --all```.

For older releases, please click [here](https://pypi.org/project/asprin/#history).

```asprin``` uses the ply library, version 3.11,
which is bundled in [asprin/src/spec_parser/ply](https://github.com/potassco/asprin/tree/master/asprin/src/spec_parser/ply),
and was retrieved from http://www.dabeaz.com/ply/.

## Examples
```
$ cat examples/example1.lp
dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,subset) { 
  a(X)
}.
#optimize(p).


$ asprin examples/example1.lp 0
asprin version 3.0.0
Reading from examples/example1.lp
Solving...
Answer: 1
a(3)
OPTIMUM FOUND
Answer: 2
a(2)
OPTIMUM FOUND
Answer: 3
a(1)
OPTIMUM FOUND

Models       : 3
  Optimum    : yes
  Optimal    : 3

$ cat examples/example2.lp
%
% base program
%

dom(1..3).
1 { a(X) : dom(X) } 2.
1 { b(X) : dom(X) } 2.
#show a/1.
#show b/1.

%
% basic preference statements
%

#preference(p(1),subset){
  a(X)
}.

#preference(p(2),less(weight)){
  X :: b(X)
}.

#preference(p(3),aso){
  a(X) >> not a(X) || b(X)
}.

#preference(p(4),poset){
  a(X);
  b(X);
  a(X) >> b(X)
}.

%
% composite preference statements
%

#preference(q,pareto){
  **p(X)
}.

#preference(r,neg){
  **q
}.

%
% optimize statement
%

#optimize(r).

$ asprin examples/example2.lp 
asprin version 3.0.0
Reading from examples/example2.lp
Solving...
Answer: 1
a(3) b(1)
OPTIMUM FOUND

Models       : 1+
  Optimum    : yes
```

## CP nets

asprin preference library implements the preference type cp,
that stands for CP nets.

CP nets where introduced in the following paper:
*  Craig Boutilier, Ronen I. Brafman, Carmel Domshlak, Holger H. Hoos, David Poole:
CP-nets: A Tool for Representing and Reasoning with Conditional Ceteris Paribus Preference Statements. 
J. Artif. Intell. Res. 21: 135-191 (2004)

Propositional preference elements of cp have one of the following forms:
  a >> not a || { l1; ...; ln }
or
  not a >> a || { l1, ..., ln }
where a is an atom and l1, ..., ln are literals.

The semantics is defined using the notion of flips.
Let X and Y be two interpretations of a logic program.
There is an improving flip from X to Y if 
X and Y only differ in the interpretation of some atom a, 
and there is some preference element of the previous form 
such that both X and Y satisfy all li's, 
and either the left part is a >> not a and a belongs to Y, 
or it is not a >> a and a does not belong to a.

Then W is better than Z if there is a sequence of improving flips from W to Z.

A CP net is consistent if there is not interpretation X such that X is better than X.


We provide various encoding and solving techniques for cp nets, 
that can be applied depending on the structure of the cp net.
For tree-like cp nets, see file cp_tree.lp, and use options ...
For acyclic cp nets, see file cp_acyclic.lp, and use options ...
For general cp nets, see file cp_general.lp, and use options ...

asprin implementation of cp nets is correct only for consistent cp nets.
Tree-like and acyclic cp nets are always consistent, but this does not hold in general.



## Contributors

* Javier Romero
