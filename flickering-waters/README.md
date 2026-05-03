使用mayachemtools实现`POSEX MD-RELAX`协议，可以重现[《“闪烁”水对接——重建关键相互作用的策略》](http://blog.molcalx.com.cn/2026/05/02/docking-with-flickering-water.html)的结果。


```bash
python /public/gkxiao/software/mayachemtools/bin/OpenMMPerformMinimization.py \
  -i 8v6y_prot.pdb \
  -s 7_D.sdf \                          # 指定独立的小分子对接结果文件
  --smallMolID LIG \                    # 可选：指定配体在输出PDB中的残基名，默认为LIG
  --forcefieldParams "biopolymer,amber14-all.xml,smallMolecule,openff-2.2.1,water,amber14/tip3pfb.xml" \
  --restraintAtoms yes \
  --restraintAtomsParams "selection,CAlphaProtein" \
  --restraintSpringConstant 2.5 \
  --systemParams "constraints,BondsInvolvingHydrogens,nonbondedMethodNonPeriodic,NoCutoff,rigidWater,yes" \
  --simulationParams "minimizationMaxSteps,0,minimizationTolerance,0.24" \
  --outputParams "minimizationDataSteps,100,minimizationDataStdout,yes,minimizationDataLog,yes" \
  --platform CPU \
  --platformParams "threads,0" \
  --overwrite \
  --outfilePrefix 8V6Y_7_complex_relaxed
```

其中：
- `8v6y_prot.pdb` 是包含必要水的蛋白结构文件。
- `7_D.sdf` 是Flare Docking的一个pose。
- 没有使用--waterBox yes，保留原有水分子（包括共晶水），但不添加额外水盒子
