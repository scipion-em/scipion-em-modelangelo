# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Pablo Conesa (you@yourinstitution.email)
# *
# * your institution
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
# *  e-mail address 'you@yourinstitution.email'
# *
# **************************************************************************


"""
Describe your python module here:
This module will provide the traditional Hello world example
"""

# TODO the test:
# Use 26126 (emdb) and 7tu5 (pdb) + small mask

import os.path

from pwem.objects import Volume, AtomStruct, Sequence, VolumeMask
from pyworkflow.protocol import params, LEVEL_ADVANCED
from pyworkflow.utils import Message
from pwem.protocols import EMProtocol
from pyworkflow.protocol import GPU_LIST, USE_GPU

from modelangelo import Plugin

OUTPUT_NAME="pruned"
OUTPUT_RAW_NAME="raw"


class ProtModelAngelo(EMProtocol):
    """
    ModelAngelo is an automatic atomic model building program for cryo-EM maps. With or without providing a sequence.
    """
    _label = 'model builder'

    _possibleOutputs = {
        OUTPUT_NAME: AtomStruct,
        OUTPUT_RAW_NAME: AtomStruct
    }

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputVolume', params.PointerParam,
                      pointerClass=Volume,
                      label='Refined volume', important=True,
                      help='Refined cryo em map.')

        # TODO: Multipointer param fo sequences, save to same fasta file.
        form.addParam('inputSequence', params.PointerParam,
                      pointerClass=Sequence,
                      label='Protein sequence', allowsNull=True, important=True,
                      help='Sequence of model into the refined volume.')

        form.addParam('inputMask', params.PointerParam,
                      pointerClass=VolumeMask,
                      label='Volume mask', allowsNull=True, important=True,
                      help='Mask. Search will be done inside the mask (non zero space).')


        form.addHidden(USE_GPU, params.BooleanParam, default=True,
                       label="Use GPU for execution",
                       help="This protocol has both CPU and GPU implementation.\
                                   Select the one you want to use.")
        form.addHidden(GPU_LIST, params.StringParam, default='0',
                       expertLevel=LEVEL_ADVANCED,
                       label="Choose GPU IDs",
                       help="Add a list of GPU devices that can be used")


    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep(self.predictStep)
        self._insertFunctionStep(self.createOutputStep)

    def predictStep(self):
        sequence = self.inputSequence.get()
        mask = self.inputMask.get()

        mode = "build" if sequence else "build_no_seq"

        args = [mode ,"-v" , self.inputVolume.get().getFileName(), "-o", self._getExtraPath()]

        if sequence:
            # Save the fasta file
            fasta = self._getExtraPath('sequence.fasta')
            sequence.exportToFile(fasta)
            args.append("-f")
            args.append(fasta)

        if mask:
            args.append("-m")
            args.append(mask.getFileName())

        # Gpu or cpu
        args.append("-d")
        # TODO: Use ore than 1 GPU?
        args.append(("%s" % self.getGpuList()[0]) if self.useGpu.get() else "cpu")

        # Call model angelo:
        self.runJob(Plugin.getModelAngeloCmd(), args )


    def createOutputStep(self):
        # register how many times the message has been printed
        # Now count will be an accumulated value

        self._registerAtomStruct(OUTPUT_NAME, self._getExtraPath('extra.cif'))

        self._registerAtomStruct(OUTPUT_RAW_NAME, self._getExtraPath('extra_raw.cif'))

    def _registerAtomStruct(self,name, path):


        if not os.path.exists(path):
            raise Exception("Output %s not found." % path)

        output = AtomStruct(filename=path)
        self._defineOutputs(**{name: output})
        self._defineSourceRelation(self.inputVolume, output)

        if self.inputSequence.get():
            self._defineSourceRelation(self.inputSequence, output)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        return summary

    def _methods(self):
        methods = []

        return methods
