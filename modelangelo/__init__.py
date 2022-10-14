# **************************************************************************
# *
# * Authors:     Pablo Conesa
# *
# * CNB CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import datetime
import os

import pwem
import pyworkflow
from pyworkflow.utils import runJob
from scipion.install.funcs import VOID_TGZ

__version__ = "3.0.1"
_logo = "icon.jpeg"
_references = ['mabioarxive']

# TODO: move to constants
MA_VERSION = 'git'
MODEL_ANGELO_ENV_ACTIVATION_VAR = "MODEL_ANGELO_ENV_ACTIVATION"

# models
MODELS_VERSION = '0.1'
MODELS_PKG_NAME = 'modelangelomodels'
TORCH_HOME_VAR = 'TORCH_HOME'

class Plugin(pwem.Plugin):

    @classmethod
    def _defineVariables(cls):
        cls._addVar(MODEL_ANGELO_ENV_ACTIVATION_VAR, cls.getActivationCmd(MA_VERSION))
        cls._defineEmVar(TORCH_HOME_VAR, MODELS_PKG_NAME + "-" + MODELS_VERSION)

    @classmethod
    def getModelAngeloCmd(cls, *args):

        cmd = cls.getCondaActivationCmd()
        cmd += cls.getVar(MODEL_ANGELO_ENV_ACTIVATION_VAR) + " && "
        cmd += "model_angelo"
        return cmd

    @classmethod
    def getEnviron(cls):
        environ = pyworkflow.utils.Environ(os.environ)
        torch_home = cls.getVar(TORCH_HOME_VAR)
        # For GPU, we need to add to LD_LIBRARY_PATH the path to Cuda/lib
        environ.set(TORCH_HOME_VAR, torch_home)
        return environ
    @classmethod
    def getActivationCmd(cls, version):
        return'conda activate modelangelo-' + version

    @classmethod
    def defineBinaries(cls, env):

        def defineModelAngeloInstallation(version):

            installed = "last-pull-%s.txt" % datetime.datetime.now().strftime("%y%h%d-%H%M%S")

            # For modelangelo
            modelangelo_commands = []
            modelangelo_commands.append(('git clone https://github.com/3dem/model-angelo.git', 'model-angelo'))
            modelangelo_commands.append((getCondaInstallation(version), 'env-created.txt'))
            modelangelo_commands.append(('cd model-angelo && git pull && touch ../%s' % installed, installed))

            env.addPackage('modelangelo', version=version,
                           commands=modelangelo_commands,
                           tar=VOID_TGZ,
                           default=True)

        def getCondaInstallation(version):
            installationCmd = cls.getCondaActivationCmd()
            installationCmd += 'conda create -y -n modelangelo-' + version + ' python=3.9 && '
            installationCmd += cls.getActivationCmd(version) + ' && '
            installationCmd += 'cd model-angelo && python -m pip install -r requirements.txt && '
            installationCmd += 'conda install -y pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch && '
            installationCmd += 'python -m pip install -e . && '
            installationCmd += 'touch ../env-created.txt'

            return installationCmd

        # Define model angelo installations
        defineModelAngeloInstallation(MA_VERSION)

        # Models download
        installationCmd = ""
        installationCmd += 'export TORCH_HOME=$PWD && '
        installationCmd += cls.getCondaActivationCmd() + " " +  cls.getActivationCmd(MA_VERSION) + ' && '
        installationCmd += 'python -m model_angelo.utils.setup_weights --bundle-name original && '
        installationCmd += 'python -m model_angelo.utils.setup_weights --bundle-name original_no_seq'


        env.addPackage('modelangelomodels', version="0.1",
                       commands=[(installationCmd,["hub/checkpoints/model_angelo/original_no_seq/success.txt",
                                                   "hub/checkpoints/model_angelo/original/success.txt"])],
                       tar=VOID_TGZ,
                       default=True)



