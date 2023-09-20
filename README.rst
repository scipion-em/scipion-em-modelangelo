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


Configuration variables
.......................

There are some variables related to the model-angelo installation. If you have installed
model-angelo within Scipion, you may define `MODEL_ANGELO_ENV_ACTIVATION` for specifying
how to activate the environment. This variable with be used together with the general
conda activation to generate the final model-angelo command. For example:

.. code-block::

    MODEL_ANGELO_ENV_ACTIVATION = conda activate model_angelo

If this variable is not defined, a default value will be provided that will work if the
latest version is installed.

If model-angelo is installed already outside Scipion, one could define `MODEL_ANGELO_ACTIVATION`.
This variable will provide an activation (or load) command that can be anything and the Scipion
conda activate will not be prepended. For example (loading model-angelo as a module):

.. code-block::

    MODEL_ANGELO_ACTIVATION = module load model-angelo/main

If you need to use CUDA different from the one used during Scipion installation (defined by *CUDA_LIB*), you can add *MODEL_ANGELO_CUDA_LIB* variable to the config file.

Protocols
---------

* Model builder

Tests
-----

* scipion3 tests modelangelo.tests.tests_model_angelo.TestModelAngel

