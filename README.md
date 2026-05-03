# openmm-test
记录分别尝试使用Amber System与OpenMM System进行分子动力学模拟的练习。

## 使用AmberTools26准备体系

## 使用Mayachemtools

### 1. 分子对接结果的`relax`

在POSEX[1]一文中，作者提出了Relax对接结果的方法，可以使用`MayaChemTools`的脚本`OpenMMPerformMinimization.py`来实现：

```bash
python $MAYACHEMTOOLS/bin/OpenMMPerformMinimization.py -i 8v6y_prot.pdb \
-s 7_D.sdf  \
--forcefieldParams "biopolymer,amber14-all.xml,smallMolecule,openff-2.2.1,water,amber14/tip3pfb.xml"   \
--restraintAtoms yes   \
--restraintAtomsParams "selection,CAlphaProtein"   \
--restraintSpringConstant 2.5   \
--systemParams "constraints,BondsInvolvingHydrogens,nonbondedMethodNonPeriodic,NoCutoff,rigidWater,yes"   \
--simulationParams "minimizationMaxSteps,0,minimizationTolerance,0.24"   \
--outputParams "minimizationDataSteps,100,minimizationDataStdout,yes,minimizationDataLog,yes"   \
--platform CPU   \
--platformParams "threads,0"   \
--overwrite   \
--outfilePrefix 8V6Y_7_complex_relaxed
```

其中：
- `8v6y_prot.pdb` 是包含必要水的蛋白结构文件。
- `7_D.sdf` 是Flare Docking的一个pose。

## 文献
1. Yize Jiang, Xinze Li, Yuanyuan Zhang, et al. “PoseX: AI Defeats Physics Approaches on Protein-Ligand Cross Docking.” arXiv:2505.01700. Preprint, arXiv, April 26, 2026. https://doi.org/10.48550/arXiv.2505.01700.
