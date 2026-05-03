# 使用 AmberTools26 准备蛋白-配体复合物 MD 体系

本教程介绍如何利用 AmberTools26 中的工具，将一个已在 Schrödinger 等软件中完成结构优化、加氢、确定质子化状态和互变异构体的蛋白‑配体复合物，制备成可直接用于 Amber MD 模拟的溶剂化拓扑（`.prmtop`）和坐标（`.inpcrd`）文件。流程保留蛋白中原有的水分子、氢原子及优化好的氢键网络，并自动处理残基/原子名与 Amber 力场的兼容性问题。

## 前置条件

- 已安装 AmberTools26（推荐通过 `conda` 或 `mamba` 安装 `ambertools=26`）。
- 已准备好以下文件：
  - **蛋白结构文件**（来自 Schrödinger）：`4zlz_prot.pdb`，含氢、含结晶水/功能性水，质子化状态和互变异构体已正确设定。
  - **配体结构文件**：`ligand.sdf`，含氢，三维结构合理，质子化状态正确。
- 激活 AmberTools26 环境：
  ```bash
  conda activate AmberTools26
  ```

## 1. 蛋白结构文件处理

目标：保留所有原子（尤其是氢）和水分子的坐标，仅修正残基名与原子名使之符合 Amber 规范，并重新格式化。

### 1.1 使用 `pdb4amber` 进行最小化清理

```bash
pdb4amber -i 4zlz_prot.pdb -o 4zlz_prot_ready.pdb --no-conect
```

**选项说明**：
- `-i`：输入 PDB 文件。
- `-o`：输出 PDB 文件。
- `--no-conect`：不写入 CONECT 记录，让 LEaP 自动处理键连。
- **不加 `-y`**：保留氢原子。
- **不加 `-d`**：保留水分子。
- **不加 `-p`**：不删除非标准残基（若文件中有配体或离子，也会保留；本例蛋白文件已分离配体，故无影响）。

**`pdb4amber` 会自动完成**：
- 将 HIS 依据氢位置重命名为 HID、HIE 或 HIP。
- 检测二硫键（SG‑SG ≤ 2.5 Å）并将 CYS 重命名为 CYX。
- 标准化原子名（如 `H` → `H1`，`HD1` → `HD1` 等，依据内置映射表）。
- 重新编号残基，添加必要的 `TER` 卡片。

### 1.2 验证处理结果

```bash
# 检查残基名称，应包含 HID/HIE/HIP/CYX 等
grep "^ATOM" 4zlz_prot_ready.pdb | awk '{print $4}' | sort -u

# 检查原子名称（确保没有无法识别的奇怪名称）
grep "^ATOM" 4zlz_prot_ready.pdb | awk '{print $3}' | sort -u
```

如果仍有 Amber 不接受的原子名（例如某些特殊氢），可使用 `parmed` 针对性修正。例如：

```bash
parmed 4zlz_prot_ready.pdb << EOF
change atomname from @H to H1
outparm 4zlz_prot_fixed.pdb
quit
EOF
```
通常情况下 `pdb4amber` 已能处理绝大多数情形，此步骤为可选。

## 2. 配体文件处理

目标：为配体生成 Amber 格式的 MOL2 文件（含电荷）和力场参数文件，**保留原有三维结构，不进行几何优化**。

### 2.1 准备力场参数文件（构象无关）

使用 `antechamber` 几何优化、计算 AM1‑BCC 电荷、生成力场文件。

从一个可靠的低能构象（例如经过几何优化的结构，不必是结合构象）生成 ligand.frcmod：

```bash
# 几何优化与电荷计算
antechamber -fi sdf -i ligand.sdf -fo mol2 -o ligand_temp.mol2 -c bcc -nc 0 -at gaff2
# 此命令会检查 GAFF2 中缺失的参数，并生成补充文件 `ligand.frcmod`。
parmchk2 -i ligand_temp.mol2 -f mol2 -o ligand.frcmod
```

**选项说明**：
- `-nc 0`：配体净电荷，请根据实际情况修改（例如 `-nc -1`）。
- `-ek "maxcyc=1000,,scfconv=1.d-8"`：这里可以使用优化过的结构（例如 maxcyc=1000 做几何优化），因为力场参数不依赖具体构象。
- `-at gaff2`：使用 GAFF2 原子类型。

### 2.2 为结合构象分配电荷（构象相关）

使用结合口袋中的配体构象（从 Schrodinger 导出的 ligand.sdf）计算电荷，跳过几何优化：
```bash
antechamber -fi sdf -i ligand.sdf -fo mol2 -o ligand_charge.mol2 -c bcc -nc 0 -at gaff2 -ek "maxcyc=0,scfconv=1.d-8"
```
**选项说明**：
- `-nc 0`：配体净电荷，请根据实际情况修改（例如 `-nc -1`）。
- `-ek "maxcyc=0"`：关键选项，**禁止几何优化**，保留输入结构的坐标和氢位置。
- `-at gaff2`：使用 GAFF2 原子类型。

## 3. 使用 LEaP 构建溶剂化体系

创建一个名为 `leap.in` 的输入文件，内容如下：

```tleap
# 加载力场
source leaprc.protein.ff19SB      # 推荐 ff19SB；若需兼容旧版可用 ff14SB
source leaprc.gaff2
source leaprc.water.tip3p          # 若需要 OPC 水模型，改为 leaprc.water.opc

# ----- 配体 -----
loadamberparams ligand.frcmod
lig = loadmol2 ligand_charge.mol2
check lig

# ----- 蛋白（已保留氢、水）-----
prot = loadpdb 4zlz_prot_ready.pdb
check prot

# ----- 复合物 -----
com = combine {prot lig}
savepdb com complex_unsolvated.pdb
saveamberparm com complex_unsolvated.prmtop complex_unsolvated.inpcrd

# ----- 溶剂化 -----
solvatebox com TIP3PBOX 12.0        # 或 solvateoct com TIP3PBOX 12.0
# 注：solvatebox 会保留原有水分子，仅添加 bulk 水并移除重叠的水分子

# ----- 自动中和抗衡离子 -----
# 若只需中和体系（不额外添加盐），应只使用一种反离子，数量设为 0
# 如果只指定一种离子且数量为 0（例如 addions com Na+ 0），tleap 会自动计算体系净电荷，并添加足够数量的该离子以中和体系（数量为净电荷的绝对值，符号相反）。
# 若体系带负电，添加 Na+；若带正电，不添加（因为 Na+ 不能中和正电）
# 若体系带正电，添加 Cl⁻
# 需要根据体系的静电荷，来注释掉下面的一行
# addions com Cl- 0
addions com Na+ 0


# ----- 最终检查与输出 -----
check com
savepdb com complex_solvated.pdb
saveamberparm com complex_solvated.prmtop complex_solvated.inpcrd
quit
```

### 关键点解释

- **自动中和**：`addions com Na+ 0` 是标准做法，需要预先知道体系的静电荷符号。
- **保留原有水分子**：`solvatebox` 不会删除原有结晶水，只会添加 bulk 水并删除与新水严重重叠的分子。
- **保留蛋白氢原子**：直接加载 `4zlz_prot_ready.pdb` 保留了 Schrödinger 优化的氢坐标，LEaP 会读取它们（前提是原子名已兼容）。
- **水模型一致性**：若蛋白中原有水来自 TIP3P，则使用 `leaprc.water.tip3p`；若为 OPC，则改为 `leaprc.water.opc` 并将 `TIP3PBOX` 改为 `OPCBOX`。

## 4. 执行 LEaP

```bash
tleap -f leap.in
```

运行过程中应关注屏幕输出：
- **无 `Error` 出现**，仅可有 `Warning`（如某些原子范德华半径缺失但不影响模拟）。
- 最后会打印体系净电荷，应为 `0.0000`。

## 5. 结果文件

运行成功后，当前目录下将生成：

- `complex_solvated.prmtop`：拓扑文件（用于 AMBER MD）
- `complex_solvated.inpcrd`：坐标文件（用于 AMBER MD）
- `complex_solvated.pdb`：溶剂化复合物 PDB（可视化检查用）
- 以及未溶剂化的复合物文件、独立的蛋白和配体拓扑文件（供后续分析使用）。

## 6. 常见问题与解决

### Q1：`pdb4amber` 处理后，某些残基名仍为 `HIS`，未自动转为 `HID/HIE/HIP`
**原因**：PDB 中该残基的氢原子名称或位置不符合 `pdb4amber` 的识别规则。  
**解决**：在 LEaP 中手动指定（不推荐），或使用 `parmed` 根据实际情况修改：
```bash
parmed 4zlz_prot_ready.pdb << EOF
change resname from :1@HIS to HIE   # 残基序号 1
outparm fixed.pdb
quit
EOF
```

### Q2：LEaP 报错 “Atom XXX in residue YYY not found” 或 “Unknown atom name”
**原因**：PDB 中某些原子名不符合 Amber 力场的命名。  
**解决**：使用 `parmed` 批量修改。先查出原子名，然后更改：
```bash
parmed 4zlz_prot_ready.pdb << EOF
change atomname from @H to H1
change atomname from @H2 to H2
outparm 4zlz_prot_fixed.pdb
quit
EOF
```
再用修正后的文件重新运行 LEaP。

### Q3：如何确认二硫键被正确识别？
**检查**：`pdb4amber` 会将参与二硫键的 CYS 改为 `CYX`。执行：
```bash
grep "CYX" 4zlz_prot_ready.pdb
```
若没有出现 `CYX`，可在 LEaP 中手动添加：
```tleap
bond prot.26.SG prot.84.SG
```

### Q4：`addions` 是否会破坏关键水分子？
`addions` 基于静电势在低能量格点位置放置离子，所需离子数量通常很少（数个），基本不会干扰活性中心或预先优化好的关键水。如果对某个水分子有极高的保留要求，可在溶剂化前将其残基名改为非 `WAT`（如 `WAT1`），使其在 `addions` 过程中不被替换。但通常无此必要。

## 7. 总结

按照本教程操作，你将获得一个完全兼容 Amber 力场、保留原始优化氢位置和质子化状态的溶剂化体系，可直接用于后续的分子动力学模拟。核心步骤可总结为：

1. `pdb4amber` 清理蛋白结构（保留所有原子，自动映射残基/原子名）。
2. `antechamber -c bcc -ek "maxcyc=0"` 为配体计算电荷但不优化几何。
3. `parmchk2` 生成配体参数。
4. LEaP 脚本中加载处理后的蛋白、配体，溶剂化后利用 `addions com Na+ 0` 自动中和。

该流程完全符合 Amber26 手册推荐做法，并最大程度地利用了外部软件（Schrödinger）的结构优化结果。
