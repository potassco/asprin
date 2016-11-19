# asprin
A general framework for qualitative and quantitative optimization in answer set programming.

## Usage
```bash
$ asprin.py [files] [number_of_models] 
```
Currently, for computing many optimal models, asprin does projection on the atoms of the preference specification. 

## Example
```
$ cat examples/example1.lp 

1 { a(X) : dom(X) }.
dom(1..5).
#show a/1.

#preference(p1,subset) { 
  a(X) : dom(X)
}.
#optimize(p1).

$ ./asprin.py asprin.lib examples/example1.lp 0
asprin version 3.0.0
Reading from asprin.lib ...
Solving...
Answer: 1
a(3)
OPTIMUM FOUND
Answer: 2
a(5)
OPTIMUM FOUND
Answer: 3
a(1) a(2)
Answer: 4
a(1)
OPTIMUM FOUND
Answer: 5
a(2)
OPTIMUM FOUND
Answer: 6
a(4)
OPTIMUM FOUND

Models		: 6
  Optimum	: yes
  Optimal	: 5

```

## Contributors

* Javier Romero
