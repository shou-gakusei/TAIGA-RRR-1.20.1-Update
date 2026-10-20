# TAIGARRR（1.20.1 移植版）

> **TAIGARRR** 是一个 **Tinkers' Construct（匠魂）** 的扩展模组，本仓库为其 Minecraft `1.20.1`（Forge）的移植与重构版本。
> 在游戏中新增 **37 种匠魂材料**，并为它们补齐矿石、存储块、锭/粒/粉、熔融流体、材料特性（Traits）与合金配方。

- Mod ID：`taiga`
- 当前版本：`1.20.1-1.3.3`
- 协议：**MIT**
- 运行环境：Minecraft `1.20.1` + Forge `47.4.8` 及以上

---

## 简介 / Introduction

TAIGARRR 最初是一套基于 KubeJS 的匠魂材料扩展（基于TAIGARR），本仓库将其机械改写为独立 Forge 模组：
以 `tools/gen_content.py` 解析原始 KubeJS 配置，自动生成数据包（资源/配方/标签/世界生成/联动），
并配合 Java 侧代码完成材料注册。

TAIGA is a **Tinkers' Construct addon** ported to a standalone Forge mod for Minecraft 1.20.1.
It adds **37 new Tinkers' materials** with their ores, storage blocks, ingots/nuggets/dusts,
molten fluids, traits and alloy recipes, plus optional integration with several popular mods.

## 特性 / Features

- **37 种全新匠魂材料**：包含 `abyssum`、`aurorium`、`dilithium`、`eezo`、`vibranium`、`uru`、`valyrium` 等。
- **完整矿物链**：每种材料拥有矿石（含不同挖掘等级）、粗矿/粗矿块、锭/粒/粉、存储块，以及对应的熔炼、铸造、合金配方。
- **熔融流体**：每种材料提供 `molten_<name>` 流体，并接入匠魂冶炼炉 / 铸造盆。
- **自定义材料特性**：如 `berserker`（狂暴）、`soul_eater`（噬魂者）、`unstable`（不稳定）。
- **世界生成**：矿石通过 Forge `biome_modifier` 注入对应生物群系。
- **联动生态（可选）**：
  - **Create / Ponder / Flywheel**：处理配方（milling 产出随机矿石等）。
  - **Farmer's Delight**（`tese_leshi` / areca-delight）、**Create-Meowchanics**：槟榔油作冶炼炉燃料等。
  - **Curios / JEI / KubeJS + Rhino**：联动配方与展示。
  - **Re-Avaritia**（`avaritia`）：奇点（singularity）支持。
  - **FTB Quests / FTB Library / FTB Teams**：任务数据生成（`tools/gen_ftbq.py`）。
  - **SlashBlade: Resharped**（`SlashBladeResharped`）：「刀锻冶匠魂」方向的直接 API 依赖；**tinker_rapier** 兼容性验证。（还没搓好）
  - **moreharvestinglevel**：材料挖掘等级 5/6/7 依赖其注册（**必需**依赖）。

## 依赖 / Dependencies

| 类型 | 模组 | Mod ID | 说明 |
| --- | --- | --- | --- |
| 必需 | Minecraft | `minecraft` | 1.20.1 |
| 必需 | Forge | `forge` | 47.4.8+ |
| 必需 | Mantle | `mantle` | `[1.11.0,)` |
| 必需 | Tinkers' Construct | `tconstruct` | `[3.10.0,)` |
| 必需 | More Harvesting Level | `moreharvestinglevel` | 提供材料挖掘等级 5/6/7 |
| 可选 | Create | `create` | 处理工序联动 |
| 可选 | areca-delight | `tese_leshi` | 槟榔油燃料等 |
| 可选 | laowu | `laowu` | 哈气进入硝化合金配方 |
| 可选 | Re-Avaritia | `avaritia` | 奇点支持 |
| 可选 | SlashBlade: Resharped | `slashblade` | 刀锻冶匠魂 API |
| 可选 | Curios / JEI / KubeJS | `curios` / `jei` / `kubejs` | 联动配方与展示 |

## 环境要求 / Requirements

- **JDK 17**（ForgeGradle 6 使用 JDK 17 工具链编译为 Java 17 字节码）。
- **Gradle 8.x**（项目自带 `gradlew` / `gradlew.bat` 包装器，无需单独安装）。
- 能够访问 Maven 仓库（Forge / SlimeKnights / Create / Modrinth 等）。

## 从源码构建 / Build from Source

`libs/` 目录中的第三方预编译 jar **不纳入版本库**（见 `.gitignore`），需先下载。

```bash
# 1. 克隆仓库
git clone https://github.com/shou-gakusei/TAIGA-RRR-1.20.1-Update.git
cd TAIGA-RRR-1.20.1-Update

# 2. 下载第三方依赖 jar 到 libs/（二选一）
bash libs/_dl.sh          # Linux / Git Bash
python libs/_dl.py        # Windows / Python

# 3. （可选）从原始 KubeJS 配置重新生成数据包与资源
#    注意：gen_content.py 依赖开发者本地的原始来源路径，
#    仓库中已提交生成结果，普通构建无需执行此步。
# python tools/gen_content.py

# 4. 构建
./gradlew build           # Windows: gradlew.bat build
```

构建产物位于 `build/libs/taiga3-1.20.1-1.3.3.jar`。

## 安装 / Installation

将生成的 `taiga3-1.20.1-1.3.3.jar` 放入 Minecraft 客户端的 `mods/` 文件夹，
并确保已安装上述**必需**依赖（Forge、Mantle、Tinkers' Construct、More Harvesting Level）。

## 项目结构 / Project Layout

```
taiga3/
├── build.gradle / settings.gradle / gradle.properties   # ForgeGradle 构建配置
├── libs/                  # 第三方预编译 jar（gitignore，需自行下载）
│   ├── _dl.sh / _dl.py    # 依赖下载脚本
├── src/main/
│   ├── java/com/whfwtf/taiga/   # 材料注册等 Java 代码
│   └── resources/               # 数据包 / 资源（已生成并入库）
└── tools/
    ├── gen_content.py    # 从原始 KubeJS 生成数据包与资源
    ├── gen_ftbq.py       # 生成 FTB Quests 任务数据
    └── patch_refmaps.py  # refmap 修正工具
```

## 许可证 / License

本项目以 **MIT 协议** 开源。详见仓库 LICENSE（如有）。

## 鸣谢 / Credits

- 作者：**Zkaface, Chefe, Team Threshold**
- 基于 Tinkers' Construct 生态，感谢 SlimeKnights 及各联动模组作者。
