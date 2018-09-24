# asprin
> A general framework for qualitative and quantitative optimization in answer set programming.

## Description
`asprin` is a general framework for optimization in ASP that allows:
* computing optimal stable models of logic programs with preferences, and
* defining new preference types in a very easy way.
Some preference types (`subset`, `pareto`...) are already defined in `asprin`'s library,
but many more can be defined simply writing a logic program.

For a formal description of `asprin`, please read our [paper](http://www.cs.uni-potsdam.de/wv/pdfformat/brderosc15a.pdf) ([bibtex](http://www.cs.uni-potsdam.de/wv/bibtex/brderosc15a.bib)).

Starting with version 3, `asprin` is documented in the [Potassco guide](https://github.com/potassco/guide/releases/).
Older versions are documented in the [Potassco guide on Sourceforge](https://sourceforge.net/projects/potassco/files/guide/).


## Usage
```bash
$ asprin [number_of_models] [options] [files]
```
By default, `asprin` loads its library `asprin_lib.lp`. This may be disabled with option `--no-asprin-lib`.

Option `--help` prints help.

Options `--approximation=weak` and `--approximation=heuristic` activate solving modes different than the basic ones, 
and are often faster than it.

Option `--meta=query` can be used to compute optimal models that contain the atom `query`. 

Options `--meta=simple` or `--meta=combine` should be used to compute many optimal models using
non stratified preference programs (in `asprin`'s library this can only happen with CP nets, see below).

Option `--on-opt-heur` can be used to enumerate diverse (or similar) optimal stable models. 
For example, try with `--on-opt-heur=+,p,1,false --on-opt-heur=-,p,1,true`.

Option `--improve-limit` can be used to enumerate close to optimal stable models.
For example, try with `--improve-limit 2,1000`.

## Building

The easiest way to obtain `asprin` is using Anaconda. 
<!--- TO BE CHANGED -->
Packages will be soon available in the Potassco channel.
Now they are available in the channel `javier-romero`. 
First install either Anaconda or Miniconda and then run: 
`conda install -c potassco -c javier-romero asprin`
<!---               -->

`asprin` can also be installed with [pip](https://pip.pypa.io) via
```pip install asprin```. 
For a local installation, add option ```--user```.
In this case, setting environment variable `PYTHONUSERBASE` to `dir` before running `pip`, 
`asprin` will be installed in `dir/bin/asprin`.

If that does not work, 
you can always download the sources from 
<!--- TO BE CHANGED -->
[here](https://github.com/potassco/asprin/releases/download/v3.0.3/asprin-3.0.3.tar.gz) in some directory `dir`,
<!---               -->
and run `asprin` with `python dir/asprin/asprin/asprin.py`.

System tests may be run with ```asprin --test``` and ```asprin --test --all```.

<!--- For older releases, please click [here](https://pypi.org/project/asprin/#history). -->

`asprin` has been tested with `Python 2.7.13` and `3.5.3`, using `clingo 5.3.0`.

```asprin``` uses the `ply` library, version `3.11`,
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

`asprin` preference library implements the preference type `cp`,
that stands for *CP nets*.

CP nets where introduced in the following paper:
*  Craig Boutilier, Ronen I. Brafman, Carmel Domshlak, Holger H. Hoos, David Poole:
CP-nets: A Tool for Representing and Reasoning with Conditional Ceteris Paribus Preference Statements. 
J. Artif. Intell. Res. 21: 135-191 (2004)

Propositional preference elements of type `cp` have one of the following forms:
1. `a >> not a || { l1; ...; ln }`, or
2. `not a >> a || { l1, ..., ln }`

where `a` is an atom and `l1`, ..., `ln` are literals.

The semantics is defined using the notion of flips.
Let `X` and `Y` be two interpretations of a logic program.
There is an improving flip from `X` to `Y` if 
`Y` is the union of `X` and `{a}` and there is some rule of the form (1) such that `X` and `Y` satisfy all `li`'s, or
`Y` is `X` minus `{a}` and there is some rule of the form (2) such that `X` and `Y` satisfy all `li`'s.
Then `W` is better than `Z` if there is a sequence of improving flips from `W` to `Z`.
A CP net is consistent if there is no interpretation `X` such that `X` is better than `X`.


We provide various encoding and solving techniques for CP nets, 
that can be applied depending on the structure of the CP net.
For tree-like CP nets, see example [cp_tree.lp](https://github.com/potassco/asprin/blob/master/asprin/examples/cp_tree.lp).
For acyclic CP nets, see example [cp_acyclic.lp](https://github.com/potassco/asprin/blob/master/asprin/examples/cp_acyclic.lp).
For general CP nets, see example [cp_general.lp](https://github.com/potassco/asprin/blob/master/asprin/examples/cp_general.lp).

`asprin` implementation of CP nets is correct only for consistent CP nets.
Note that tree-like and acyclic CP nets are always consistent, but this does not hold in general.


## Contributors

* Javier Romero
