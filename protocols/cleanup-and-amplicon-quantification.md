# Post-PCR clean-up and amplicon quantification

#### Clean-up

_**update: from experience I've found that a 1x bead clean-up is preferable to a 1.8x clean-up if you are sequencing on the MinION. The MinION library prep features 1x clean-ups throughout the protocol, and I've found that if a 1.8x clean-up is used on the amplicons it's hard to keep the library concentration high enough throughout the prep, probably because the 1x clean-ups are more stringent bottlenecks. If you're going to be sequencing on the MiSeq, it should be fine to stick with the 1.8x clean-up._

1. Label two sets of DNA Lo-Bind tubes (one set for bead clean-up and the other for eluate with cleaned up amplicons).
2. Allow AMPure XP beads to come up to room temperature, and homogenize thoroughly by vortexing.
3. Add 40 uL (1x) or 72 (1.8x) uL of AMPure XP beads to each tube in one set of the Lo-Bind tubes depending on sequencing platform.
4. Pipette 40 uL of PCR product into corresponding tube with beads.
5. Incubate beads and PCR products at room temperature on a hula mixer for 5 minutes. _if no access to a hula mixer, you can flick mix gently throughout the incubation period._
6. Place tubes on magnetic rack and incubate until the solution is clear.
7. Discard the supernatant being careful to not disturb pellet.
8. Add 200 uL of 80% EtOH to each tube to wash pellet (while being careful to not disturb pellet), incubate 30 seconds, then discard EtOH wash.
9. Repeat previous wash again, pipetting off as much EtOH as possible.
10. Spin tubes down, replace on magnetic rack, and pipette off any additional EtOH. Leave tubes open to dry.
11. Allow pellets to dry (roughly 5 minutes). The pellet should appear matte but not dry to the point where cracks form. DNA yield will drop if the pellet is left to dry too long.
12. When pellet is dry add 31 uL of nuclease-free water to each tube, remove from rack and flick gently to resuspend beads. _if storing amplicons for longer periods of time, qiagen Elution Buffer can be used instead of nuclease-free water._
13. Once pellets have been resuspended, incubate at room temperature on a hula mixer for 5 minutes.
14. Replace tubes on magnetic rack and incubate until solution fully clears.
15. Carefully pipette off 31 uL of supernatant without disturbing beads and place into new Lo-Bind tubes.

#### Quantification

_You should use the Qubit High Sensitivity dsDNA kit_

1. Make up Qubit Mastermix in a falcon tube :

  * 199 uL Buffer _per sample_
  * 1 uL dye _per sample_

2. Add 190 uL mastermix + 10 uL standard 1 into one Qubit tube.
3. Add 190 uL mastermix + 10 uL standard 2 into another Qubit tube.
4. Add 199 uL mastermix + 1 uL cleaned-up PCR products into Qubit tube for each pool.
5. Vortex, spin down and wait 2 minutes.
6. Quantify the concentration of dsDNA in the sample.

  * Negative extraction controls usually have concentrations around 3 or 4 ng/uL. If you have access to gel electrophoresis, you can run these negatives on a gel to check whether there is amplicon contamination or whether the quantifiable levels of dsDNA are simply represent a smear.
  * Negative PCR controls should have concentrations < 1 ng/uL. Ideally these are unquantifiable, but it is challenging to get concentrations this low except in completely ideal lab settings.
  * Properly amplified samples should have concentrations between 5 and 100 ng/uL.
