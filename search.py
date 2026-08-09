import cubiomes
from cubiomes import Generator, MCVersion, Structure

def find_witch_huts(seed):
    # 使用 MC 1.21 版本（或 26.2，但 cubiomes 目前最高支持 1.21）
    gen = Generator(MCVersion.MC_1_21, seed)
    gen.set_biome_cache(True)
    
    # 设置搜索范围：整个世界（-3000万 到 +3000万）
    huts = []
    # cubiomes 提供 getStructurePositions，但需要遍历区域
    # 这里用更高效的方法：遍历所有可能的沼泽群系
    # 使用 cubiomes 的 find_structures 函数
    for x, z in gen.find_structures(Structure.SWAMP_HUT, 0, 0, 0):
        huts.append((x, z))
    
    return huts

if __name__ == "__main__":
    seed = -1421144132636065691
    huts = find_witch_huts(seed)
    if huts:
        # 按 Z 坐标排序（升序，最小 Z 即最低纬度）
        huts.sort(key=lambda p: p[1])
        lowest = huts[0]
        with open("results.txt", "w") as f:
            f.write(f"找到 {len(huts)} 个女巫小屋\n")
            f.write("所有坐标 (X, Z):\n")
            for x, z in huts:
                f.write(f"  x={x}, z={z}\n")
            f.write(f"\n最低纬度（最小 Z）女巫小屋: x={lowest[0]}, z={lowest[1]}\n")
    else:
        with open("results.txt", "w") as f:
            f.write("未找到任何女巫小屋\n")
