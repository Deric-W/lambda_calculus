lambda_calculus
===============

Welcome to lambda_calculus`s documentation.

This project implements basic operations of the `Lambda calculus <https://en.wikipedia.org/wiki/Lambda_calculus>`_
as a python package and contains helpers to define custom ones.

It is intended to be used for educational purposes and is not optimized for speed.
Furthermore, it expects all terms to be finite, which means the absence of cycles.
:py:class:`RecursionError` may be raised when using an infinite term or the evaluation is too complex.

.. toctree::
   :maxdepth: 2

   installation
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
