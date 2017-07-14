# asprin
> A general framework for qualitative and quantitative optimization in answer set programming.

## Usage
```bash
$ asprin [number_of_models] [options] [files]
```
By default, asprin loads its library `asprin_lib.lp`. This may be disabled with option `--no-asprin-lib`.

Option `--help` prints help.

## Building
`asprin` requires Python (version 2.7 is tested), and 
the [python module of clingo](https://github.com/potassco/clingo) (version 5.2.0 is tested),
whose directory should appear in the [environment variable](https://en.wikipedia.org/wiki/Environment_variable)
`PYTHONPATH`.

`asprin` can be installed with [pip](https://pip.pypa.io) via
```pip install asprin```. 
For a local installation, add option ```--user```.

For older releases, please click [here](https://pypi.org/project/asprin/#history).

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
Calls        : 10
Time         : 0.054s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.052s

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
  Calls        : 2
  Time         : 0.109s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
  CPU Time     : 0.104s
```

## Contributors

* Javier Romero
