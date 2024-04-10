# **************************************************************************
# *
# * Authors:     Pablo Conesa
# *
# * CNB CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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
from datetime import datetime as dt
import os

import pwem
import pyworkflow.utils as pwutils
from scipion.install.funcs import VOID_TGZ

from .constants import *

__version__ = "3.1.1"
_logo = "logo.jpeg"
_references = ['jamali2023']


class Plugin(pwem.Plugin):

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(MODEL_ANGELO_ACTIVATION_VAR, '')
        cls._defineVar(MODEL_ANGELO_ENV_ACTIVATION_VAR, cls.getActivationCmd(MA_VERSION))
        cls._defineEmVar(TORCH_HOME_VAR, MODELS_PKG_NAME + "-" + MODELS_VERSION)
        cls._defineVar(MODEL_ANGELO_CUDA_LIB, pwem.Config.CUDA_LIB)

    @classmethod
    def getModelAngeloCmd(cls):
        cmd = cls.getVar(MODEL_ANGELO_ACTIVATION_VAR)
        if not cmd:
            cmd = cls.getCondaActivationCmd()
            cmd += cls.getVar(MODEL_ANGELO_ENV_ACTIVATION_VAR)
        cmd += " && model_angelo"
        return cmd

    @classmethod
    def getEnviron(cls):
        environ = pwutils.Environ(os.environ)
        torch_home = cls.getVar(TORCH_HOME_VAR)
        environ.set(TORCH_HOME_VAR, torch_home)

        cudaLib = cls.getVar(MODEL_ANGELO_CUDA_LIB)
        environ.addLibrary(cudaLib)

        return environ

    @classmethod
    def getActivationCmd(cls, version):
        return 'conda activate modelangelo-' + version

    @classmethod
    def defineBinaries(cls, env):

        def defineModelAngeloInstallation(version):
            installed = "last-pull-%s.txt" % dt.now().strftime("%y%h%d-%H%M%S")

            modelangelo_commands = [
                ('git clone https://github.com/3dem/model-angelo.git', 'model-angelo'),
                (getCondaInstallation(version), 'env-created.txt'),
                ('cd model-angelo && git pull && touch ../%s' % installed, installed)
            ]

            env.addPackage('modelangelo', version=version,
                           commands=modelangelo_commands,
                           tar=VOID_TGZ,
                           default=True)

        def getCondaInstallation(version):
            installationCmd = cls.getCondaActivationCmd()
            installationCmd += 'conda create -y -n modelangelo-' + version + ' python=3.10 && '
            installationCmd += cls.getActivationCmd(version) + ' && '
            installationCmd += 'conda install -y pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia && '
            installationCmd += 'cd model-angelo && '
            installationCmd += 'pip install -e . && '
            installationCmd += 'touch ../env-created.txt'

            return installationCmd

        defineModelAngeloInstallation(MA_VERSION)

        # Models download
        installationCmd = ""
        installationCmd += 'export TORCH_HOME=$PWD && '
        installationCmd += cls.getCondaActivationCmd() + " " + cls.getActivationCmd(MA_VERSION) + ' && '
        installationCmd += 'python -m model_angelo.utils.setup_weights --bundle-name original && '
        installationCmd += 'python -m model_angelo.utils.setup_weights --bundle-name original_no_seq'

        env.addPackage('modelangelomodels', version=MODELS_VERSION,
                       commands=[(installationCmd, [f"hub/checkpoints/model_angelo_v{MODELS_VERSION}/original_no_seq/success.txt",
                                                    f"hub/checkpoints/model_angelo_v{MODELS_VERSION}/original/success.txt"])],
                       tar=VOID_TGZ,
                       default=True)
