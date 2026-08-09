import sys

# -------------------- 配置参数 --------------------
SPACING = 32
SEPARATION = 8
SALT = 10387313
SEARCH_RADIUS = 10000

LCG_MULTIPLIER = 0x5DEECE66D
LCG_ADDEND = 0xB
LCG_MASK = (1 << 48) - 1

def trunc_div(a, b):
    """向零取整除法（Java 风格）"""
    return (a // b) if a >= 0 else -((-a) // b)

class MCJavaRandom:
    """模拟 Minecraft Java RandomSource"""
    def __init__(self, seed=0):
        self.seed = 0
        self.set_seed(seed)

    def set_seed(self, seed):
        self.seed = (seed ^ LCG_MULTIPLIER) & LCG_MASK

    def next(self, bits):
        self.seed = (self.seed * LCG_MULTIPLIER + LCG_ADDEND) & LCG_MASK
        return self.seed >> (48 - bits)

    def next_int(self, bound):
        if bound <= 0:
            raise ValueError("bound must be positive")
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        bits = self.next(31)
        value = bits % bound
        while bits - value + (bound - 1) < 0:
            bits = self.next(31)
            value = bits % bound
        return value

def get_region_seed(rx, rz, world_seed):
    return (rx * 341873128712 + rz * 132897987541 + world_seed + SALT) & 0xFFFFFFFFFFFFFFFF

def block_to_chunk(x):
    return x >> 4   # 负数也正确，因为 -1 >> 4 = -1（与 Java 一致，但 Java 负数右移仍为负数，而 Minecraft 使用区块坐标，负数区块可行）

def find_swamp_huts(world_seed, radius=SEARCH_RADIUS):
    results = []
    # 搜索半径对应的区块范围（使用向零取整）
    min_rcx = trunc_div(-radius, 16)
    max_rcx = trunc_div(radius, 16)
    min_rcz = trunc_div(-radius, 16)
    max_rcz = trunc_div(radius, 16)

    # 计算区域范围（使用向零取整）
    min_rx = trunc_div(min_rcx, SPACING)
    max_rx = trunc_div(max_rcx, SPACING)
    min_rz = trunc_div(min_rcz, SPACING)
    max_rz = trunc_div(max_rcz, SPACING)

    for rx in range(min_rx, max_rx + 1):
        for rz in range(min_rz, max_rz + 1):
            rng = MCJavaRandom(get_region_seed(rx, rz, world_seed))
            ox = rng.next_int(SPACING - SEPARATION)
            oz = rng.next_int(SPACING - SEPARATION)
            cx = rx * SPACING + ox
            cz = rz * SPACING + oz

            # 转换为方块坐标
            bx = cx << 4
            bz = cz << 4

            # 检查是否在半径内
            if abs(bx) <= radius and abs(bz) <= radius:
                results.append((bx, bz))

    # 去重
    results = list(dict.fromkeys(results))
    return results

def main():
    if len(sys.argv) < 2:
        seed = int(input("请输入世界种子（整数）：").strip())
    else:
        seed = int(sys.argv[1])

    radius = int(sys.argv[2]) if len(sys.argv) > 2 else SEARCH_RADIUS

    candidates = find_swamp_huts(seed, radius)

    if not candidates:
        print(f"在半径 {radius} 范围内未找到候选位置。")
        return

    print(f"找到 {len(candidates)} 个候选位置：")
    for x, z in candidates:
        print(f"  X={x}, Z={z}")

    lowest = min(candidates, key=lambda p: p[1])
    print(f"\n✅ 最低纬度（Z 最小）候选：X={lowest[0]}, Z={lowest[1]}")
    print("⚠️ 注意：需在游戏中验证生物群系（沼泽/红树林沼泽）。")

if __name__ == "__main__":
    main()
