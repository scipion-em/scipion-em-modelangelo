====================
Modelangelo   plugin
====================

This plugin provide a wrapper for `Model angelo <https://github.com/3dem/model-angelo>`_ which allows *de novo* atomic modelling


Installation
------------

a) Stable version

.. code-block::

    scipion3 installp -p scipion-em-modelangelo

b) Developer's version

    * download repository

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-modelangelo.git

    * install

    .. code-block::

        scipion3 installp -p path_to_scipion-em-modelangelo --devel

Modelangelo will be installed automatically with the plugin using a Conda environment.


Protocols
---------

* Model builder

Tests
-----

* scipion3 tests modelangelo.tests.tests_model_angelo.TestModelAngel

