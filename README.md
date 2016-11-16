# asprin
A general framework for qualitative and quantitative optimization in answer set programming.

## Usage
```bash
$ asprin.py [files] [number_of_models] 
```
Currently, for computing many optimal models, asprin does projection on the atoms of the preference specification. 

## Example
```
$ asprin.py examples/example1.lp asprin.lib 0
asprin version 3.0.0
Reading from examples/example1.lp ...
Solving...
Answer: 
a(3) 1 "b"
OPTIMUM FOUND
Answer: 
a(5) 1 "b"
OPTIMUM FOUND
Answer: 
a(1) a(2) 1 "b"
Answer: 
a(1) 1 "b"
OPTIMUM FOUND
Answer: 
a(2) 1 "b"
OPTIMUM FOUND
Answer: 
a(4) 1 "b"
OPTIMUM FOUND

Models          : 6
  Optimum       : yes
  Optimal       : 5
```

## Contributors

* Javier Romero
