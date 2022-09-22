# lambda_calculus

![Tests](https://github.com/Deric-W/lambda_calculus/actions/workflows/Tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/Deric-W/lambda_calculus/branch/main/graph/badge.svg?token=SU3982mC17)](https://codecov.io/gh/Deric-W/lambda_calculus)

The `lambda_calculus` package contains classes which implement basic operations of the lambda calculus.

To use it, simply import the classes `Variable`, `Abstraction` and `Application` from this package
and nest them to create more complex lambda terms.

You can also use the `visitors` subpackage to define your own operations on terms or
use predefined ones from the `terms` subpackage.

## Notice

This package is intended to be used for educational purposes and is not optimized for speed.

Furthermore, it expects all terms to be finite, which means the absence of cycles.

`RecursionError` may be raised if the visitors get passed an infinite term or the evaluation is too complex.

## Requirements

Python >= 3.10 is required to use this package.

## Installation

```sh
python3 -m pip install lambda-calculus
```

## Examples

(λy.(λx.(λy. + x y)) y 3) 4

### Nesting

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

### Utility Methods

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

### Method Chaining

```python
from lambda_calculus import Variable, Abstraction, Application

x = Variable.with_valid_name("x")
y = Variable.with_valid_name("y")

term = Variable("+") \
    .apply_to(x, y) \
    .abstract("x", "y") \
    .apply_to(y, Variable("3")) \
    .abstract("y") \
    .apply_to(Variable("4"))
```

### Evaluation

```python
from lambda_calculus import Variable, Application
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor

assert BetaNormalisingVisitor().skip_intermediate(term) == Application.with_arguments(
    Variable("+"),
    (Variable("4"), Variable("3"))
)
```