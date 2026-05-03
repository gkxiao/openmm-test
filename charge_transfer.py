#!/usr/bin/env python3
"""
charge_transfer.py - 替换 MOL2 文件中的电荷列（最后一列），保留原始空白格式
用法:
    python charge_transfer.py lig_opt.mol2 lig_bound_bcc.mol2 [output.mol2]
"""

import sys
import shutil


def parse_mol2(filepath):
    """提取原子电荷（最后一列）、原子类型序列、键集合"""
    with open(filepath) as f:
        lines = f.readlines()

    atom_start = None
    bond_start = None
    for i, line in enumerate(lines):
        if line.startswith('@<TRIPOS>ATOM'):
            atom_start = i + 1
        elif line.startswith('@<TRIPOS>BOND'):
            bond_start = i + 1
        elif line.startswith('@<TRIPOS>') and i > 0:
            if atom_start is not None and bond_start is None:
                bond_start = i
            if bond_start is not None:
                break

    if atom_start is None:
        raise ValueError("找不到 @<TRIPOS>ATOM 块")

    atom_end = bond_start if bond_start is not None else len(lines)

    charges = []
    atom_types = []
    for line in lines[atom_start:atom_end]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            charge = float(parts[-1])
        except ValueError:
            raise ValueError(f"无法解析电荷: {line}")
        charges.append(charge)
        atom_types.append(parts[5])

    bonds = set()
    if bond_start is not None:
        for line in lines[bond_start:]:
            line = line.strip()
            if not line or line.startswith('@'):
                break
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                a = int(parts[1])
                b = int(parts[2])
            except ValueError:
                continue
            bonds.add(frozenset((a, b)))

    return charges, atom_types, bonds


def check_topology(opt_types, opt_bonds, bound_types, bound_bonds):
    if opt_types != bound_types:
        print("错误：原子类型序列不一致", file=sys.stderr)
        for i, (t1, t2) in enumerate(zip(opt_types, bound_types)):
            if t1 != t2:
                print(f"  第{i+1}个原子: opt={t1}, bound={t2}", file=sys.stderr)
        return False
    if opt_bonds != bound_bonds:
        print("错误：键连接关系不一致", file=sys.stderr)
        only_opt = opt_bonds - bound_bonds
        only_bound = bound_bonds - opt_bonds
        if only_opt:
            print(f"  仅opt有的键: {only_opt}", file=sys.stderr)
        if only_bound:
            print(f"  仅bound有的键: {only_bound}", file=sys.stderr)
        return False
    return True


def replace_charges_in_file(bound_path, new_charges, output_path, backup=True):
    if backup and bound_path == output_path:
        shutil.copy2(bound_path, bound_path + ".bak")
        print(f"已备份原文件至 {bound_path}.bak")

    with open(bound_path, 'r') as fin, open(output_path, 'w') as fout:
        in_atom = False
        atom_idx = 0
        for line in fin:
            if line.startswith('@<TRIPOS>ATOM'):
                in_atom = True
                fout.write(line)
                continue
            elif line.startswith('@<TRIPOS>'):
                in_atom = False
                fout.write(line)
                continue

            if in_atom and line.strip():
                # 保留原空白，仅替换最后一列
                parts = line.rsplit(None, 1)
                if len(parts) == 2:
                    prefix, _ = parts
                    new_line = f"{prefix} {new_charges[atom_idx]:.6f}\n"
                else:
                    # 后备方案：整行拆分再组合
                    fields = line.split()
                    fields[-1] = f"{new_charges[atom_idx]:.6f}"
                    new_line = " ".join(fields) + "\n"
                fout.write(new_line)
                atom_idx += 1
            else:
                fout.write(line)

        if atom_idx != len(new_charges):
            print(f"警告：实际替换 {atom_idx} 个原子，期望 {len(new_charges)} 个", file=sys.stderr)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    opt_file = sys.argv[1]
    bound_file = sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else bound_file

    try:
        opt_charges, opt_types, opt_bonds = parse_mol2(opt_file)
        bound_charges, bound_types, bound_bonds = parse_mol2(bound_file)
    except FileNotFoundError as e:
        print(f"文件不存在: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"解析错误: {e}", file=sys.stderr)
        sys.exit(1)

    print("检查拓扑一致性...")
    if not check_topology(opt_types, opt_bonds, bound_types, bound_bonds):
        print("拓扑不一致，终止操作。", file=sys.stderr)
        sys.exit(1)
    print("拓扑一致，开始替换电荷...")

    replace_charges_in_file(bound_file, opt_charges, out_file, backup=(out_file == bound_file))
    print(f"完成！输出文件：{out_file}")
    if out_file == bound_file:
        print("原文件已覆盖，备份为 .bak")


if __name__ == "__main__":
    main()
