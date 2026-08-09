#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "cubiomes/include/cubiomes.h"// 修改了这一行

uint64_t lcg_next(uint64_t *seed) {
    *seed = *seed * 6364136223846793005ULL + 1442695040888963407ULL;
    return *seed;
}
int lcg_next_int(uint64_t *seed, int bound) {
    return (int)((lcg_next(seed) >> 17) % bound);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <seed> [radius]\n", argv[0]);
        return 1;
    }
    uint64_t seed = strtoull(argv[1], NULL, 10);
    int radius = (argc > 2) ? atoi(argv[2]) : 50000;

    Generator gen;
    initGenerator(&gen, MC_1_21, seed);

    const int spacing = 32;
    const int separation = 8;
    const int salt = 10387313;

    int min_cx = -radius / 16;
    int max_cx = radius / 16;
    int min_cz = -radius / 16;
    int max_cz = radius / 16;

    int min_rx = min_cx / spacing;
    int max_rx = max_cx / spacing;
    int min_rz = min_cz / spacing;
    int max_rz = max_cz / spacing;

    typedef struct { int x, y, z; } Pos;
    Pos *results = malloc(10000 * sizeof(Pos));
    int count = 0;

    for (int rx = min_rx; rx <= max_rx; rx++) {
        for (int rz = min_rz; rz <= max_rz; rz++) {
            uint64_t region_seed = (rx * 341873128712ULL + rz * 132897987541ULL + seed + salt) & 0xFFFFFFFFFFFFFFFFULL;
            uint64_t rng = region_seed;
            int ox = lcg_next_int(&rng, spacing - separation);
            int oz = lcg_next_int(&rng, spacing - separation);
            int cx = rx * spacing + ox;
            int cz = rz * spacing + oz;

            if (cx < min_cx || cx > max_cx || cz < min_cz || cz > max_cz)
                continue;

            int bx = cx * 16 + 8;
            int bz = cz * 16 + 8;

            int biome = getBiomeAt(&gen, bx, 0, bz);
            if (biome != 6 && biome != 27)
                continue;

            int y = getHeight(&gen, bx, bz, Heightmap_WorldSurfaceWG);
            if (y < 0) continue;

            results[count].x = bx;
            results[count].y = y;
            results[count].z = bz;
            count++;
            if (count >= 10000) break;
        }
        if (count >= 10000) break;
    }

    // 按 Z 升序排序
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (results[i].z > results[j].z) {
                Pos tmp = results[i];
                results[i] = results[j];
                results[j] = tmp;
            }
        }
    }

    if (count == 0) {
        printf("未找到任何女巫小屋\n");
    } else {
        printf("找到 %d 个女巫小屋：\n", count);
        for (int i = 0; i < count; i++) {
            printf("X=%d, Y=%d, Z=%d", results[i].x, results[i].y, results[i].z);
            if (i == 0) printf(" ← 最低纬度");
            printf("\n");
        }
    }

    free(results);
    return 0;
}
