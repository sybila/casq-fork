.. code::

       ______      _____ ____ 
      / ____/___ _/ ___// __ \
     / /   / __ `/\__ \/ / / /
    / /___/ /_/ /___/ / /_/ / 
    \____/\__,_//____/\___\_\ 

|pipeline status| |coverage report| |black| |rtd| |gpl|

|pypi-version| |pypi-python| |pypi-wheel| |pypi-downloads| |deps|

.. |pipeline status| image:: https://gitlab.inria.fr/soliman/casq/badges/master/pipeline.svg
   :target: https://gitlab.inria.fr/soliman/casq/commits/master
   :alt: pipeline status

.. |coverage report| image:: https://gitlab.inria.fr/soliman/casq/badges/master/coverage.svg
   :target: https://gitlab.inria.fr/soliman/casq/commits/master
   :alt: coverage report

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
   :alt: Code style: black

.. |rtd| image:: https://readthedocs.org/projects/casq/badge/?version=latest
   :target: https://casq.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |gpl| image:: https://img.shields.io/pypi/l/casq
   :target: https://gitlab.inria.fr/soliman/casq/raw/master/LICENSE
   :alt: PyPI - License

.. |pypi-version| image:: https://img.shields.io/pypi/v/casq
   :target: https://pypi.org/project/casq/
   :alt: PyPI

.. |pypi-python| image:: https://img.shields.io/pypi/pyversions/casq
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/casq/

.. |pypi-wheel| image:: https://img.shields.io/pypi/wheel/casq
   :target: https://pypi.org/project/casq/
   :alt: PyPI - Wheel

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/casq
   :target: https://pypi.org/project/casq/
   :alt: PyPI - Downloads

.. |deps| image:: https://img.shields.io/librariesio/release/pypi/casq
   :target: https://pypi.org/project/casq/
   :alt: Libraries.io dependency status for latest release

**CaSQ** converts `CellDesigner`_ models to Boolean models encoded in
`SBML-Qual`_ with a rather strict semantics defined in a
`published article`_.

This extension allows also generating partially specified Boolean networks in .aeon
format from `CellDesigner`_ models. Possible use in `AEON`_ tool for further
analyses.

.. _`CellDesigner`: http://celldesigner.org
.. _`SBML-Qual`: http://sbml.org
.. _`published article`: https://academic.oup.com/bioinformatics/article/36/16/4473/5836892
.. _`AEON`: https://biodivine.fi.muni.cz/aeon/

Install
=======

CaSQ is provided as a Python3 package, you can install it from the
https://github.com/sybila/casq-fork.git.


Command-line usage
==================

Just follow the instructions::

   $ casq --help
   usage: casq [-h] [-v] [-D] [-c] [-s] [-r S] [-f FIXED] [-n] [-u [UPSTREAM ...]]
            [-d [DOWNSTREAM ...]] [-a] [-b] [-g GRANULARITY] [-i INPUT] [-C]
            [infile] [outfile]

    Convert CellDesigner models to SBML-qual with a rather strict semantics.
    Copyright (C) 2019, Sylvain.Soliman@inria.fr GPLv3.
    Convert CellDesigner models to partially specified Boolean networks in .aeon format.
    Copyright (C) 2024, xfrak@fi.muni.cz GPLv3.

    positional arguments:
        infile                CellDesigner File
        outfile               SBML-Qual/BMA json File/.aeon File

    options:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -D, --debug           Display a lot of debug information
      -c, --csv             Store the species information in a separate CSV (and .bnet) file
      -s, --sif             Store the influence information in a separate SIF file
      -r S, --remove S      Delete connected components in the resulting model if
                            their size is smaller than S. A negative
                            S leads to keep only the biggest(s) connected component(s)
      -f FIXED, --fixed FIXED
                            A CSV file containing input values or knock-ins/knock-outs,
                            one per line, with name in the
                            first column and the value in the second.
      -n, --names           Use the names as IDs in the SBML file
      -u [UPSTREAM ...], --upstream [UPSTREAM ...]
                            Only species upstream of this/these species will be kept
      -d [DOWNSTREAM ...], --downstream [DOWNSTREAM ...]
                            Only species downstream of this/these species will be kept
      -a, --aeon            Output to partially specified Boolean networks in .aeon format
      -b, --bma             Output to BMA json format
      -g GRANULARITY, --granularity GRANULARITY
                            When exporting to BMA, use this granularity
      -i INPUT, --input INPUT
                            When exporting to BMA, nodes with no input should be set to
                            this value
      -C, --colourConstant  When exporting to BMA, colour all variables pink
                            (defaults to colour by compartment)

