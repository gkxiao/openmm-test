# openmm-test
记录分别尝试使用Amber System与OpenMM System进行分子动力学模拟的练习。

## 使用AMBER工具链

### QUICK计算rwRESP电荷

```bash
# QUICK计算
export QUICK_BASIS=/home/gkxiao/.conda/miniforge/envs/AmberTools26/AmberTools/src/quick/basis
quick.cuda 4zlz_resp.inp
# 生成rwRESP电荷的mol2文件
antechamber -i 4zlz_resp.out -fi quick -o 4zlz_rwresp.mol2 -fo mol2 -c resp -s 2 -rn LIG -at gaff2
# 生成GAFF2力场参数文件
parmchk2 -i 4zlz_rwresp.mol2 -f mol2 -o lig.frcmod
```
参见`QUICK`目录


## 使用AmberTools26准备体系

## 使用Mayachemtools

### 1. `POSEX MD-Relax`协议
在POSEX[1]一文中，作者提出了MD-Relax协议来处理对接结果：

#### 平台与力场
弛豫计算在OpenMM 7.7平台上实现。系统使用标准的分子力场（如Amber力场）进行参数化，以计算分子间相互作用能。

#### 约束条件
为了在优化过程中保持蛋白结构的整体折叠，对蛋白质骨架原子（backbone atoms）施加了位置约束。约束力通过一个简谐势能项实现：

F = 0.5 * k * [ (x-x₀)² + (y-y₀)² + (z-z₀)² ]

其中，力常数 \(k = 10\)，\(x_0,y_0,z_0\) 是原子在原始（预测）结构中的三维坐标。

这意味着骨架原子可以移动，但偏离初始位置会受到惩罚。新添加的原子（如优化过程中可能添加的氢原子）则不受此约束，可以自由移动。

#### 动力学参数
- **积分器**：采用朗之万（Langevin）热浴来维持恒温。
- **温度**：设定为 300 K（室温）。
- **摩擦系数**：1 ps⁻¹。
- **时间步长**：0.004 ps（即4飞秒）。这是分子动力学模拟中常用、可平衡计算效率与数值稳定性的时间步长。

#### 收敛标准
能量最小化迭代持续进行，直至系统能量梯度收敛阈值 \(\le 10\ \text{kJ/mol/nm}\)，确保结构优化至局部能量极小点。

#### 流程目标
该协议核心为**受约束的分子动力学优化（Constrained molecular dynamics optimization）**。
并非长时间尺度动力学构象采样，而是短时能量最小化过程：快速修复AI预测结构中分子内/分子间立体碰撞（clashes），优化键长、键角等立体化学参数，让预测结合姿势在物理上更合理。

#### 使用`OpenMMPerformMinimization.py`实现
`POSEX MD-Relax`协议可以使用`MayaChemTools`的脚本`OpenMMPerformMinimization.py`来实现：

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

## 文献
1. Yize Jiang, Xinze Li, Yuanyuan Zhang, et al. “PoseX: AI Defeats Physics Approaches on Protein-Ligand Cross Docking.” arXiv:2505.01700. Preprint, arXiv, April 26, 2026. https://doi.org/10.48550/arXiv.2505.01700.
