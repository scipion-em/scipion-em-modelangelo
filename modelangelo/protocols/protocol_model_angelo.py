# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Pablo Conesa 
# *              Roberto Marabini
# *
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

import os.path

from pwem.objects import Volume, AtomStruct, VolumeMask
from pyworkflow.protocol import params, LEVEL_ADVANCED
from pyworkflow.utils import Message
from pwem.protocols import EMProtocol
from pyworkflow.protocol import GPU_LIST, USE_GPU
from pwem.convert.headers import Ccp4Header

from modelangelo import Plugin

OUTPUT_NAME = "pruned"
OUTPUT_RAW_NAME = "raw"


class ProtModelAngelo(EMProtocol):
    """
    ModelAngelo is an automatic atomic model building program for cryo-EM maps.
    With or without providing a sequence.

    AI Generated:

    Model Builder (ProtModelAngelo) - User Manual
        Overview

        The Model Builder protocol performs automatic atomic model
        construction from cryo-EM density maps using ModelAngelo.
        Its primary objective is to generate protein backbone and
        atomic interpretations directly from reconstructed volumes,
        reducing the amount of manual intervention typically required
        during structural interpretation. The protocol is designed to
        support both sequence-guided and sequence-independent model
        building workflows, making it suitable for a broad range of
        cryo-EM projects.

        In practical biological research, this protocol is commonly
        used after obtaining a refined cryo-EM reconstruction with
        sufficient local resolution to support atomic interpretation.
        It is especially valuable for accelerating the transition from
        density maps to biologically meaningful structural models,
        enabling downstream tasks such as structural validation,
        functional interpretation, ligand analysis, or comparative
        modeling.

        Inputs and Biological Context

        The protocol requires a refined cryo-EM map as the main input.
        The quality of the final atomic model strongly depends on the
        interpretability of this volume. Maps with high local detail,
        clear secondary structure features, and accurate sharpening
        generally produce the most reliable results.

        Optionally, one or more protein sequences may be provided.
        When sequences are available, the protocol attempts to assign
        residues and generate biologically interpretable chain models
        consistent with the supplied amino acid information. This mode
        is particularly important for experimentally characterized
        proteins, known complexes, or assemblies with well-defined
        subunit composition.

        When no sequence information is available, the protocol can
        still perform sequence-independent tracing. In this scenario,
        the resulting model primarily represents the geometry of the
        backbone and secondary structure organization rather than a
        fully assigned amino acid sequence. This mode is useful during
        exploratory analyses, for unknown proteins, or for rapid
        structural inspection before biochemical annotation.

        Masking and Region Selection

        An optional volume mask can be supplied to restrict the
        reconstruction area used during model building. From a
        biological perspective, masking is often critical when the map
        contains solvent regions, neighboring particles, flexible
        densities, or heterogeneous assemblies.

        Applying an appropriate mask allows the protocol to focus on
        the biologically relevant region while reducing ambiguity and
        avoiding spurious tracing outside the target structure. In
        large macromolecular complexes, masking can substantially
        improve model continuity and overall interpretability.

        The mask should ideally include the ordered structural core
        while excluding noisy peripheral regions. Excessively tight
        masks may truncate meaningful density, whereas overly broad
        masks may reduce model quality by introducing irrelevant
        features.

        Sequence-Guided Modeling

        When sequences are provided, the protocol attempts to combine
        density interpretation with sequence assignment. This produces
        models that are easier to validate biologically and directly
        compatible with downstream structural biology workflows.

        Sequence-guided modeling is especially useful for identifying
        domain organization, residue positions, catalytic motifs, or
        interaction interfaces. In multi-subunit assemblies, providing
        accurate sequence information helps distinguish different
        chains and improves the biological interpretability of the
        final reconstruction.

        However, users should remain cautious when interpreting poorly
        resolved regions. Flexible loops, disordered termini, or weak
        densities may still lead to uncertain assignments even when
        sequence information is available.

        Sequence-Independent Modeling

        The sequence-independent mode is intended for situations where
        no reliable amino acid sequences are available. In this mode,
        the protocol focuses on tracing the structural framework of
        the macromolecule directly from the density map.

        This approach is particularly valuable in exploratory cryo-EM
        projects, environmental samples, partially characterized
        assemblies, or rapid preliminary analyses. Although the
        resulting models may lack residue-level annotation, they still
        provide biologically meaningful information regarding overall
        fold organization, secondary structure arrangement, and
        connectivity.

        Researchers often use these initial traces as starting points
        for later manual refinement or sequence assignment.

        Hardware and Computational Considerations

        The protocol supports both GPU and CPU execution, although GPU
        acceleration is generally preferred for practical cryo-EM
        workloads due to significantly improved execution speed. In
        most biological projects involving medium or large maps, GPU
        execution substantially reduces turnaround time and enables
        more efficient iterative analysis.

        Only a single GPU device is intended for execution at a time.
        This simplifies resource allocation and ensures stable
        behavior during automated model generation.

        Advanced Configuration

        Advanced users may optionally provide a configuration file to
        customize the behavior of the underlying modeling pipeline.
        This enables fine control over preprocessing, masking,
        inference behavior, sampling strategies, or model refinement
        parameters.

        Such customization is generally intended for expert users who
        need to adapt the workflow to unusual datasets, highly
        heterogeneous maps, or specialized computational environments.
        For most biological applications, the default settings are
        sufficient and provide reliable performance without requiring
        manual optimization.

        Outputs and Their Interpretation

        The protocol produces atomic structure files representing the
        interpreted cryo-EM density. Depending on the workflow, the
        outputs may include both processed and intermediate structural
        models. These models can subsequently be inspected in
        molecular visualization software, refined further, or used in
        downstream biological interpretation.

        The resulting structures should always be evaluated in the
        context of map quality and local resolution. Well-resolved
        alpha helices and beta sheets are generally modeled more
        reliably than flexible or poorly ordered regions. Biological
        validation through visual inspection, sequence consistency,
        stereochemical analysis, and comparison with known structures
        remains essential.

        Practical Recommendations

        For most cryo-EM studies, the best results are obtained from
        maps that have already undergone careful refinement,
        sharpening, and masking. Providing accurate sequences whenever
        available substantially improves residue assignment and model
        interpretability.

        In challenging cases involving conformational variability,
        partial occupancy, or low local resolution, users should
        interpret automatically generated models cautiously and
        consider additional manual refinement steps.

        Sequence-independent tracing can serve as an excellent
        exploratory starting point, but final biological conclusions
        should ideally rely on validated sequence assignments and
        careful structural inspection.

        Final Perspective

        Automatic model building represents a major advance in
        cryo-EM structural biology because it accelerates the
        conversion of density maps into biologically interpretable
        molecular models. By combining density interpretation,
        sequence information, and automated structural inference, this
        protocol enables researchers to rapidly obtain structural
        hypotheses suitable for visualization, validation, and
        downstream biological discovery.
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
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputVolume', params.PointerParam,
                      pointerClass=Volume,
                      label='Refined volume', important=True,
                      help='Refined cryo-em map.')

        form.addParam('inputSequenceS', params.MultiPointerParam,
                      pointerClass="Sequence", allowsNull=True, important=True,
                      label='Protein sequences',
                      help="Include here one or more sequences to be modeled\n"
                           "Leave empty to use the *model_no_seq* option.")

        form.addParam('inputMask', params.PointerParam,
                      pointerClass=VolumeMask,
                      label='Volume mask', allowsNull=True, important=True,
                      help='Search will be done inside the mask.\n'
                           'That is, voxels inside the mask should be NON zero.')

        form.addHidden(USE_GPU, params.BooleanParam, default=True,
                       label="Use GPU for execution",
                       help="This protocol has both CPU and GPU implementation. "
                            "Select the one you want to use.")

        form.addHidden(GPU_LIST, params.StringParam, default='0',
                       expertLevel=LEVEL_ADVANCED,
                       label="Choose GPU ID (single one)",
                       help="GPU device to be used")

        form.addParam('configFile', params.FileParam,
                      label="Configuration File",
                      default="",
                      expertLevel=LEVEL_ADVANCED,
                      help="""This option is only for VERY advanced users.\n
Below is an example of a config file:

{
  "standardize_mrc_args":
    {
      "target_voxel_size": 1.5,
      "crop_z": 0,
      "bfactor_to_apply": 0,
      "auto_mask": false
    },
  "ca_infer_args":
    {
      "model_checkpoint": "chkpt.torch",
      "bfactor": 0,
      "batch_size": 4,
      "stride": 16,
      "dont_mask_input": true,
      "threshold": 0.05,
      "save_real_coordinates": false,
      "save_cryo_em_grid": false,
      "do_nucleotides": false,
      "save_backbone_trace": false,
      "save_ca_grid": false,
      "crop": 6
    },
  "gnn_infer_args":
    {
      "num_rounds": 3,
      "crop_length": 200,
      "repeat_per_residue": 3,
      "esm_model": "esm1b_t33_650M_UR50S",
      "aggressive_pruning": false,
      "seq_attention_batch_size": 200
    }
}
""")

    # -------------------------- INSERT steps functions -----------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep(self.convertInputStep)
        self._insertFunctionStep(self.predictStep)
        self._insertFunctionStep(self.createOutputStep)

    # --------------------------- STEPS functions ------------------------------
    def convertInputStep(self):
        """ convert 3D maps to MRC '.mrc' format
            with extension mrc, map extension is not handled by modelangelo
        """
        vol = self.inputVolume.get()
        inVolName = vol.getFileName()
        if inVolName.endswith(".mrc"):
            self.newFn = inVolName
        else:
            self.newFn = self._getExtraPath("inputVol.mrc")
            origin = vol.getOrigin(force=True).getShifts()
            sampling = vol.getSamplingRate()
            Ccp4Header.fixFile(inVolName, self.newFn, origin, sampling, Ccp4Header.START)  # ORIGIN

    def predictStep(self):
        seqs = self.inputSequenceS
        mask = self.inputMask.get()
        configFile = self.configFile.get()

        args = []
        if seqs:
            fasta = self.createInputFastaFile(seqs)
            args.extend(["build", "--fasta-path", fasta])
        else:
            args.append("build_no_seq")

        args.extend(["--volume-path", self.newFn,
                     "--output-dir", self._getExtraPath()])

        if mask:
            args.extend(["--mask-path", mask.getFileName()])

        # Gpu or cpu
        args.extend(["--device", ("%s" % self.getGpuList()[0]) if self.useGpu else "cpu"])

        if configFile:
            args.extend(["-c", configFile])

        try:
            # Call model angelo:
            self.runJob(Plugin.getModelAngeloCmd(), args)
        except Exception:
            # Modelangelo does not show error in the stdout, nor stderr we
            # should go and read the error information from a log file
            with open(self._getExtraPath("model_angelo.log")) as log:
                for line in log.read().splitlines():
                    self.error(line)
            self.info("ERROR: %s." % line)
            raise ChildProcessError("Model angelo has failed: %s. See error log "
                                    "for more details." % line) from None

    def createOutputStep(self):
        """Register atomic models, raw and pruned"""
        # check if files exists before registering
        # I think build_no_seq creates a single output file (no raw file)
        if os.path.exists(self._getExtraPath('extra_raw.cif')):
            self._registerAtomStruct(OUTPUT_RAW_NAME, self._getExtraPath('extra_raw.cif'))
        self._registerAtomStruct(OUTPUT_NAME, self._getExtraPath('extra.cif'))

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []
        gpus = self.getGpuList()

        if len(gpus) > 1:
            errors.append('Only one GPU can be used.')

        return errors

    # -------------------------- UTILS functions ------------------------------
    def createInputFastaFile(self, seqs):
        """ Get sequence as string and create the corresponding fasta file. """

        fastaFileName = self._getExtraPath('sequence.fasta')

        with open(fastaFileName, "w") as f:
            for seq in seqs:
                s = seq.get()
                f.write(f"> {s.getId()}\n")
                f.write(f"{s.getSequence()}\n")

        return fastaFileName

    def _registerAtomStruct(self, name, path):
        if not os.path.exists(path):
            raise FileNotFoundError("Output %s not found." % path)

        output = AtomStruct(filename=path)
        self._defineOutputs(**{name: output})
        self._defineSourceRelation(self.inputVolume, output)

        seqs = self.inputSequenceS
        if seqs:
            for seq in seqs:
                self._defineSourceRelation(seq, output)
