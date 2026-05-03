## 使用QUICK计算rwRESP电荷

```bash
export QUICK_BASIS=/home/gkxiao/.conda/miniforge/envs/AmberTools26/AmberTools/src/quick/basis
quick.cuda 4zlz_resp.inp
antechamber -i 4zlz_resp.out -fi quick -o 4zlz_rwresp.mol2 -fo mol2 -c resp -s 2 -rn LIG -at gaff2
```

## 文献

(1) Tripathy, V.; Palos, E.; Merz, K. M.; Paesani, F.; Götz, A. W. QUICK and Robust ESP and RESP Charges for Computational Biochemistry: Open-Source GPU Implementation. J. Chem. Inf. Model. 2026, 66 (6), 3173–3187. https://doi.org/10.1021/acs.jcim.5c03200.
