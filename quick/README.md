## 使用QUICK计算rwRESP电荷

```bash
# QUICK计算
export QUICK_BASIS=/home/gkxiao/.conda/miniforge/envs/AmberTools26/AmberTools/src/quick/basis
quick.cuda 4zlz_resp.inp
# 生成rwRESP电荷
antechamber -i 4zlz_resp.out -fi quick -o 4zlz_rwresp.mol2 -fo mol2 -c resp -s 2 -rn LIG -at gaff2
# 生成力场参数文件
parmchk2 -i 4zlz_rwresp.mol2 -f mol2 -o lig.frcmod
```

注意：
- rwRESP计算的参数组合为：ESPGRID_SPACING=0.05 f_rwt=431.0， 这相当昂贵，但是在CUDA加速下我认为相当快
- 推荐的均衡计算速度与稳健性的组合是：ESPGRID_SPACING=0.25 f_rwt=17.0 ，这是QUICK的默认参数
- 在后续的AMBER 系统参数准备中，要确保结合构象使用的电荷与生成力场参数文件（FRCMOD文件）是一致的。

将rwRESP电荷迁移到结合构象上：

```bash
antechamber -fi sdf -i lig_bound.sdf -fo mol2 -o lig_bound_framework.mol2 -s 2 -at gaff2 -c bcc
```
注意：此处 -c bcc 是临时的，只是为了让 antechamber 生成一个“完整”的 mol2 文件，包含正确的原子类型和连接信息。稍后我们会替换电荷。

将 `4zlz_rwresp.mol2` 中每个原子的 RESP 电荷值，精确地复制到 lig_bound_framework.mol2 的对应原子上。这通常通过编写脚本（如 awk, python）或使用编辑器（如 vi, emacs）的宏来完成。你必须确保原子的顺序和类型完全匹配，并保存为lig_bound_rwresp.mol2。

```bash
charge_transfer.py 4zlz_rwresp.mol2 lig_bound_framework.mol2 lig_bound_rwresp.mol2
```

这个新的文件`lig_bound_rwresp.mol2`可以用于准备后续的top7与rst7等AMBER系统文件。当然，也可以直接用这个文件生成力场参数文件lig.frcmod。

## 文献

(1) Tripathy, V.; Palos, E.; Merz, K. M.; Paesani, F.; Götz, A. W. QUICK and Robust ESP and RESP Charges for Computational Biochemistry: Open-Source GPU Implementation. J. Chem. Inf. Model. 2026, 66 (6), 3173–3187. https://doi.org/10.1021/acs.jcim.5c03200.
