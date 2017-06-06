# asprin
> A general framework for qualitative and quantitative optimization in answer set programming.

## Usage
```bash
$ asprin [number_of_models] [options] [files]
```
By default, asprin loads its library `asprin.lib`. This may be disabled with option `--no-asprin-lib`.

## Building
`asprin` requires Python (version 2.7 is tested), and the [python module of clingo](https://github.com/potassco/clingo). For installation instructions of the latter, please read [here](https://github.com/potassco/clingo/blob/master/INSTALL) the section on Building the Python Module.


## Example
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

#const composite=pareto.

#preference(q,pareto){
  **p(X)
} : composite=pareto.

#preference(q,lexico){
  X :: **p(X)
} : composite=lexico.

#preference(q,and){
  **q(X)
} : composite=and.

#preference(r,neg){
  **q
}.

%
% optimize statement
%

#const opt=r.
#optimize(opt).


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
Time         : 0.091s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.088s
```

## Contributors

* Javier Romero
