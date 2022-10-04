Installation
============

.. toctree::
   :maxdepth: 2

Overview over the most common ways of installing this project.

Installation from PyPI
----------------------

If you just want to get started or receive updates you can use
the package available on `PyPI <https://pypi.org/project/lambda-calculus/>`_ and
install it with the following command:

.. code:: bash

    python3 -m pip install lambda-calculus

`Sematic Versioning <https://semver.org/>`_ is is attempted to be adhered to.

Installation from source
------------------------

This project adheres to `PEP 517 <https://peps.python.org/pep-0517>`_ and
can be build using `build <https://pypi.org/project/build/>`_:

.. code:: bash

    python3 -m build

The resulting wheel should be platform and machine independent
because this is a pure python project.
