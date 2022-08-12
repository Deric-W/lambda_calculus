# lambda_calculus

The `lambda_calculus` package contains classes which implement basic operations of the lambda calculus.

To use it, simply import the classes `Variable`, `Abstraction` and `Application` from this package
and nest them to create more complex lambda terms.

You can also use the `visitors` subpackage to define your own operations on terms.

## Requirements

Python >= 3.10 is required to use this package.

## Examples

(λy.(λx.(λy. + x y)) y 3) 4

```python
from lambda_calculus import Variable, Abstraction, Application

term = Application(Variable("+"), Variable("x"))
term = Application(term, Variable("y"))
term = Abstraction("y", term)
term = Abstraction("x", term)
term = Application(term, Variable("y"))
term = Application(term, Variable("3"))
term = Abstraction("y", term)
term = Application(term, Variable("4"))
```

using utility methods:

```python
from lambda_calculus import Variable, Abstraction, Application

x = Variable.with_valid_name("x")
y = Variable.with_valid_name("y")

term = Application.with_arguments(Variable.with_valid_name("+"), (x, y))
term = Abstraction.curried(("x", "y"), term)
term = Application.with_arguments(term, (y, Variable.with_valid_name("3")))
term = Abstraction("y", term)
term = Application(term, Variable.with_valid_name("4"))
```