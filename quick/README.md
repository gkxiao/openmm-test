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

## 文献

(1) Tripathy, V.; Palos, E.; Merz, K. M.; Paesani, F.; Götz, A. W. QUICK and Robust ESP and RESP Charges for Computational Biochemistry: Open-Source GPU Implementation. J. Chem. Inf. Model. 2026, 66 (6), 3173–3187. https://doi.org/10.1021/acs.jcim.5c03200.
