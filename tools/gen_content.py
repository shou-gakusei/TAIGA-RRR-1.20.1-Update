#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAIGA3 内容生成器
以实例内 KubeJS 的 1.20.1 复刻为第一手来源，把 data/ 与 assets/ 内容按 ID 映射
机械改写为 taiga 命名空间，并补齐脚本里以 JS 表达的配方/标签/世界生成/联动内容。

用法: python tools/gen_content.py
输出: src/main/resources/**  (data/ 与 assets/)

只读来源:
  KJS = D:/other/pcl/.minecraft/versions/机霸动力-新时代-0.4/kubejs
  REF = E:/111/mod.dev/参考模组/taigarr (dust 纹理 / lang 兜底)
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

KJS = Path(r"D:\other\pcl\.minecraft\versions\机霸动力-新时代-0.4\kubejs")
REF = Path(r"E:\111\mod.dev\参考模组\taigarr\src\main\resources")
OUT = Path(__file__).resolve().parent.parent / "src" / "main" / "resources"

# ----------------------------------------------------------------------------
# 材料总表（从 kubejs/startup_scripts/tconstruct_register_fluids/taiga_fluids.js 解析）
# ----------------------------------------------------------------------------

def parse_materials():
    src = (KJS / "startup_scripts/tconstruct_register_fluids/taiga_fluids.js").read_text(encoding="utf-8")
    names = re.search(r"const taiga_items = \[(.*?)\];", src, re.S).group(1)
    names = [n.strip().strip("'") for n in names.replace("\n", " ").split(",") if n.strip()]
    levels = dict(re.findall(r"let (level_\d+) = '([^']+)'", src))

    row_re = re.compile(
        r"\[(\d+),\s*(0x[0-9A-Fa-f]+),\s*(\d+),\s*(.+?),\s*\[([\d.,\s]+)\],\s*\[([\d.,\s]+)\],\s*(.+?)\],\s*//\s*(\w+)"
    )
    mats = {}
    for m in row_re.finditer(src):
        temp, color, tier, lvl, head, handle, trait, name = m.groups()
        lvl = lvl.strip()
        lvl = levels.get(lvl, lvl.strip("'"))
        if lvl.startswith("'"):
            lvl = lvl.strip("'")
        head = [x.strip() for x in head.split(",")]
        handle = [x.strip() for x in handle.split(",")]
        trait = trait.strip()
        if trait in levels:  # 理论上不会发生
            trait = levels[trait]
        mats[name] = dict(
            name=name,
            temperature=int(temp),
            color=color,
            tier=int(tier),
            harvest=lvl,                     # 例如 moreharvestinglevel:level_7 / minecraft:netherite
            head_durability=int(head[0]),
            head_speed=float(head[1]),
            head_attack=float(head[2]),
            handle_mod=float(handle[0]),
            handle_durability=int(handle[1]),
            trait=trait,                     # 例如 tconstruct:jagged / taiga:berserker
        )
    assert len(mats) == len(names), f"解析到 {len(mats)} 行，期望 {len(names)}"
    return names, mats


MATS_ORDER, MATS = parse_materials()
MATS_SET = set(MATS_ORDER)

# ----------------------------------------------------------------------------
# 方块/物品清单（来自 kubejs startup_scripts）
# ----------------------------------------------------------------------------

# 有矿石方块的 15 种材料：whfwtf 9 个 + taigablocks 6 个
ORE_MINEABLE = {                      # material -> 所需工具 tag
    "abyssum": "forge:needs_netherite_tool",
    "aurorium": "forge:needs_netherite_tool",
    "dilithium": "minecraft:needs_iron_tool",
    "eezo": "forge:needs_netherite_tool",
    "jauxum": "minecraft:needs_iron_tool",
    "karmesine": "minecraft:needs_iron_tool",
    "osram": "minecraft:needs_diamond_tool",
    "ovium": "minecraft:needs_iron_tool",
    "tiberium": "minecraft:needs_diamond_tool",
}
ORE_LEVEL_TAG = {                     # material -> moreharvestinglevel 等级 tag
    "duranite": 5, "prometheum": 5, "palladium": 5,
    "uru": 6, "valyrium": 6,
    "vibranium": 7,
}
ORE_MATS = list(ORE_MINEABLE) + list(ORE_LEVEL_TAG)                    # 15
GENERIC_ORE_TIERS = {5: ["duranite", "prometheum", "palladium"],
                     6: ["uru", "valyrium"],
                     7: ["vibranium"]}

# 粗矿物品（15 个）；dilithium/tiberium 为晶体
RAW_DROPS = {                        # ore material -> 掉落物 id
    "dilithium": "taiga:dilithium_crystal",
    "abyssum": "taiga:raw_abyssum",
    "aurorium": "taiga:raw_aurorium",
    "eezo": "taiga:raw_eezo",
    "jauxum": "taiga:raw_jauxum",
    "karmesine": "taiga:raw_karmesine",
    "osram": "taiga:raw_osram",
    "ovium": "taiga:raw_ovium",
    "tiberium": "taiga:tiberium_crystal",
    "duranite": "taiga:raw_duranite",
    "palladium": "taiga:raw_palladium",
    "prometheum": "taiga:raw_prometheum",
    "uru": "taiga:raw_uru",
    "valyrium": "taiga:raw_valyrium",
    "vibranium": "taiga:raw_vibranium",
}
RAW_ITEMS = ["taiga:dilithium_crystal", "taiga:raw_abyssum", "taiga:raw_aurorium",
             "taiga:raw_duranite", "taiga:raw_eezo", "taiga:raw_jauxum", "taiga:raw_karmesine",
             "taiga:raw_osram", "taiga:raw_ovium", "taiga:raw_palladium", "taiga:raw_prometheum",
             "taiga:raw_uru", "taiga:raw_valyrium", "taiga:raw_vibranium", "taiga:tiberium_crystal"]

# 特殊方块
SPECIAL_BLOCKS = ["basalt_rock", "meteorite_cobble_block", "raw_meteorite_block",
                  "raw_obsidiorite_block", "obsidiorite_cobble_block"]

TOOLS = ["dyonite", "nucleum", "solarium"]

# ----------------------------------------------------------------------------
# ID 改写
# ----------------------------------------------------------------------------

WHFWTF_ORE = {"abyssum", "aurorium", "dilithium", "eezo", "jauxum",
              "karmesine", "osram", "ovium", "tiberium"}

WHFWTF_MAP = {
    "whfwtf:basalt_block": "taiga:basalt_rock",
    "whfwtf:meteorite_cobble_block": "taiga:meteorite_cobble_block",
    "whfwtf:raw_meteorite_block": "taiga:raw_meteorite_block",
    "whfwtf:raw_obsidiorite_block": "taiga:raw_obsidiorite_block",
}


def _rewrite_id(text: str) -> str:
    """把一处 'namespace:path' 改成 taiga 命名空间的新 id。"""
    if ":" not in text:
        return text
    ns, path = text.split(":", 1)
    if ns == "taigaingots":
        return f"taiga:{path}_ingot"
    if ns == "taiganuggets":
        return f"taiga:{path}_nugget"
    if ns == "taigametalblocks":
        return f"taiga:{path}"
    if ns == "taigafluids":
        return f"taiga:{path}"
    if ns == "taiga_pickaxe":
        return f"taiga:{path}"
    if ns == "taigaproperties":
        return f"taiga:{path}"
    if ns == "taigablocks":
        if path == "taiga_ore_5":
            return "taiga:ore_5"
        if path == "taiga_ore_6":
            return "taiga:ore_6"
        if path == "taiga_ore_7":
            return "taiga:ore_7"
        return f"taiga:{path}"
    if ns == "whfwtf":
        if path in WHFWTF_MAP:
            return WHFWTF_MAP[path]
        if path in WHFWTF_ORE:
            return f"taiga:{path}_ore"
        if path.endswith("_crystal_block"):
            return f"taiga:{path}"
        if path.endswith("_crystal"):
            return f"taiga:{path}"
        return f"taiga:{path}"
    return text


ID_RE = re.compile(r"\b(taigaingots|taiganuggets|taigametalblocks|taigafluids|taiga_pickaxe|taigaproperties|taigablocks|whfwtf):([a-z0-9_/]+)")


def rewrite_text(text: str) -> str:
    return ID_RE.sub(lambda m: _rewrite_id(m.group(0)), text)


# ----------------------------------------------------------------------------
# 写文件工具
# ----------------------------------------------------------------------------

def ensure(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(rel: str, obj):
    p = ensure(OUT / rel)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(rel: str, txt: str):
    p = ensure(OUT / rel)
    p.write_text(txt, encoding="utf-8")


def copy_rewrite_json(src: Path, rel_dst: str):
    data = json.loads(src.read_text(encoding="utf-8"))
    write_json(rel_dst, _rewrite_obj(data))


def _rewrite_obj(obj):
    if isinstance(obj, dict):
        return {k: _rewrite_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_rewrite_obj(v) for v in obj]
    if isinstance(obj, str):
        return rewrite_text(obj)
    return obj


def copy_png(src: Path, rel_dst: str):
    if not src.exists():
        missing.append(str(src))
        return
    p = ensure(OUT / rel_dst)
    shutil.copyfile(src, p)


missing = []


def _mk(parent, name, **kw):
    d = {"parent": parent}
    if "textures" in kw:
        d["textures"] = kw["textures"]
    write_json(name, d)


# ---------------------------------------------------------------------------
# 阶段 3：Tinkers 材料数据包（直接搬运 + 改 id）
# ---------------------------------------------------------------------------

def gen_tinkering():
    src_root = KJS / "data/taiga/tinkering"
    for kind in ("materials/definition", "materials/stats", "materials/traits", "tools/materials"):
        for f in sorted((src_root / kind).glob("*.json")):
            copy_rewrite_json(f, f"data/taiga/tinkering/{kind}/{f.name}")
    for kind in ("materials", "models/material"):
        for f in sorted((KJS / f"assets/taiga/tinkering/{kind}").glob("*.json")):
            copy_rewrite_json(f, f"assets/taiga/tinkering/{kind}/{f.name}")
    # 自定义特性（berserker / soul_eater / unstable）定义
    for f in sorted((KJS / "data/taigaproperties/tinkering/modifiers").glob("*.json")):
        copy_rewrite_json(f, f"data/taiga/tinkering/modifiers/{f.name}")


# ---------------------------------------------------------------------------
# 阶段 4：配方搬运（casting / fuel / melting / alloy）
# ---------------------------------------------------------------------------

def gen_recipes_copy():
    for f in sorted((KJS / "data/taiga/recipes").rglob("*.json")):
        rel = f.relative_to(KJS / "data/taiga/recipes").as_posix()
        copy_rewrite_json(f, f"data/taiga/recipes/{rel}")
    for f in sorted((KJS / "data/tconstruct/recipes/melting/taiga").glob("*.json")):
        copy_rewrite_json(f, f"data/taiga/recipes/melting/{f.name}")
    for f in sorted((KJS / "data/tconstruct/recipes/melting/melting/ore").glob("*.json")):
        copy_rewrite_json(f, f"data/taiga/recipes/melting/ore/{f.name}")
    for f in sorted((KJS / "data/tconstruct/recipes/smeltery/alloy").glob("*.json")):
        copy_rewrite_json(f, f"data/taiga/recipes/smeltery/alloy/{f.name}")


# ---------------------------------------------------------------------------
# 阶段 4：KJS 脚本里的配方 / 掉落 / 标签（JSON 化）
# ---------------------------------------------------------------------------

def _shaped(name, pattern, key, result):
    write_json(f"data/taiga/recipes/crafting/{name}.json", {
        "type": "minecraft:crafting_shaped",
        "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()},
        "result": {"item": result},
    })


def _shapeless(name, ingredients, result, count=1):
    write_json(f"data/taiga/recipes/crafting/{name}.json", {
        "type": "minecraft:crafting_shapeless",
        "ingredients": [{"item": i} for i in ingredients],
        "result": {"item": result, "count": count},
    })


def _smelting(name, ingredient, result, xp=0.7, time=200):
    write_json(f"data/taiga/recipes/smelting/{name}.json", {
        "type": "minecraft:smelting",
        "ingredient": {"item": ingredient},
        "result": result,
        "experience": xp,
        "cookingtime": time,
    })


def gen_manual_recipes():
    # 金属：块↔锭↔粒（对齐 server_scripts/taiga/taiga_metals.js）
    for mat in MATS_ORDER:
        ingot, nugget, block = f"taiga:{mat}_ingot", f"taiga:{mat}_nugget", f"taiga:{mat}_block"
        _shaped(f"{mat}_block", ["AAA", "AAA", "AAA"], {"A": ingot}, block)
        _shapeless(f"{mat}_ingot_from_block", [block], ingot, 9)
        _shaped(f"{mat}_ingot", ["AAA", "AAA", "AAA"], {"A": nugget}, ingot)
        _shapeless(f"{mat}_nugget_from_ingot", [ingot], nugget, 9)

    # 粗矿 ↔ 粗矿块（对齐 raw_ore_block.js）
    for item in RAW_ITEMS:
        blk = item + "_block"
        name = item.split(":")[1]
        _shaped(f"{name}_block", ["AAA", "AAA", "AAA"], {"A": item}, blk)
        _shapeless(f"{name}_from_block", [blk], item, 9)

    # 冶炼（对齐 server_scripts/taiga/basalt.js）
    _smelting("basalt_block_from_rock", "taiga:basalt_rock", "taiga:basalt_block")
    _smelting("meteorite_ingot_from_cobble", "taiga:meteorite_cobble_block", "taiga:meteorite_ingot")
    _smelting("meteorite_cobble_from_raw", "taiga:raw_meteorite_block", "taiga:meteorite_cobble_block")
    _smelting("obsidiorite_ingot_from_raw", "taiga:raw_obsidiorite_block", "taiga:obsidiorite_ingot")

    # 镐子（对齐 server_scripts/taiga/pickaxe.js）
    for mat in TOOLS:
        _shaped(f"{mat}_pickaxe", ["AAA", " B ", " B "],
                {"A": f"taiga:{mat}_ingot", "B": "minecraft:iron_ingot"}, f"taiga:{mat}_pickaxe")

    # 矿石掉落表（对齐 tic_recipies/taiga_block_loot_table.js）
    for mat, drop in RAW_DROPS.items():
        write_json(f"data/taiga/loot_tables/blocks/{mat}_ore.json", {
            "type": "minecraft:block",
            "pools": [{
                "rolls": 1.0,
                "bonus_rolls": 0.0,
                "entries": [{"type": "minecraft:item", "name": drop}],
                "conditions": [{"condition": "minecraft:survives_explosion"}],
            }],
        })


def _tag(path, values, replace=False):
    write_json(path, {"replace": replace, "values": values})


def gen_tags():
    # mineable/pickaxe：全部 taiga 方块
    mineable = [f"taiga:{m}_block" for m in MATS_ORDER]
    mineable += [f"taiga:{m}_ore" for m in ORE_MATS]
    mineable += RAW_ITEMS_TO_BLOCKS + [f"taiga:{b}" for b in SPECIAL_BLOCKS]
    _tag("data/minecraft/tags/blocks/mineable/pickaxe.json", mineable)

    # 工具等级标签
    for tag, mats in (("forge:needs_netherite_tool", None), ("minecraft:needs_iron_tool", None),
                      ("minecraft:needs_diamond_tool", None)):
        vals = [f"taiga:{m}_ore" for m, t in ORE_MINEABLE.items() if t == tag]
        if vals:
            _tag(f"data/{tag.split(':')[0]}/tags/blocks/{tag.split(':')[1]}.json", vals)
    for lvl, mats in GENERIC_ORE_TIERS.items():
        _tag(f"data/moreharvestinglevel/tags/blocks/level_{lvl}.json",
             [f"taiga:{m}_ore" for m in mats])

    # basalt 原料（对齐 tweaks/tags.js）
    base = ["minecraft:polished_basalt", "minecraft:basalt"]
    _tag("data/taiga/tags/blocks/basalt_ingredient.json", base)
    _tag("data/taiga/tags/items/basalt_ingredient.json", base)

    # forge 通用标签（便于联动与其它模组取用）
    _tag("data/forge/tags/items/ingots.json", [])  # 占位，避免空标签报错
    for mat in MATS_ORDER:
        _tag(f"data/forge/tags/items/ingots/{mat}.json", [f"taiga:{mat}_ingot"])
        _tag(f"data/forge/tags/items/nuggets/{mat}.json", [f"taiga:{mat}_nugget"])
        _tag(f"data/forge/tags/items/dusts/{mat}.json", [f"taiga:{mat}_dust"])
        _tag(f"data/forge/tags/blocks/storage_blocks/{mat}.json", [f"taiga:{mat}_block"])
    for mat in ORE_MATS:
        _tag(f"data/forge/tags/blocks/ores/{mat}.json", [f"taiga:{mat}_ore"])
        _tag(f"data/forge/tags/items/ores/{mat}.json", [f"taiga:{mat}_ore"])
    for item in RAW_ITEMS:
        name = item.split(":")[1].replace("raw_", "").replace("_crystal", "")
        _tag(f"data/forge/tags/items/raw_materials/{name}.json", [item])

    # 熔融流体 tag（对齐 taiga_fluids.js 的 .tag('tconstruct:molten_x')）
    for name in MATS_ORDER + ["nitronite"]:
        _tag(f"data/tconstruct/tags/fluids/molten_{name}.json", [f"taiga:molten_{name}"])
    _tag("data/tconstruct/tags/fluids/blaze_halwa.json", ["taiga:blaze_halwa"])


RAW_ITEMS_TO_BLOCKS = [i + "_block" for i in RAW_ITEMS]


# ---------------------------------------------------------------------------
# 阶段 6：世界生成
# ---------------------------------------------------------------------------

def gen_worldgen():
    src = KJS / "data/whfwtf"
    for f in sorted((src / "worldgen/configured_feature").glob("*.json")):
        obj = json.loads(f.read_text(encoding="utf-8"))
        # state.Name 是方块 id（可能来自 whfwtf 或 taigablocks）-> 统一按 ID 规则改写
        for t in obj.get("config", {}).get("targets", []):
            nm = t.get("state", {}).get("Name", "")
            if ":" in nm:
                t["state"]["Name"] = _rewrite_id(nm)
        write_json(f"data/taiga/worldgen/configured_feature/{f.name}", obj)

    for f in sorted((src / "worldgen/placed_feature").glob("*.json")):
        obj = json.loads(f.read_text(encoding="utf-8"))
        if obj.get("feature", "").startswith("whfwtf:"):
            obj["feature"] = "taiga:" + obj["feature"].split(":")[1]
        write_json(f"data/taiga/worldgen/placed_feature/{f.name}", obj)

    for f in sorted((src / "forge/biome_modifier").glob("*.json")):
        obj = json.loads(f.read_text(encoding="utf-8"))
        if obj.get("features", "").startswith("whfwtf:"):
            obj["features"] = "taiga:" + obj["features"].split(":")[1]
        write_json(f"data/taiga/forge/biome_modifier/{f.name}", obj)


# ---------------------------------------------------------------------------
# 阶段 8：联动（areca-delight / Create-Meowchanics / Re-Avaritia）
# ---------------------------------------------------------------------------

def gen_compat():
    # 要求1：槟榔油作匠魂冶炼炉燃料（1000°C）
    write_json("data/taiga/recipes/fuel/binlang_oil.json", {
        "type": "tconstruct:melting_fuel",
        "fluid": {"name": "tese_leshi:binlang_oil", "amount": 50},
        "temperature": 1000,
        "duration": 100,
        "rate": 10,
    })

    # 要求3：哈气进入硝化合金配方（1 mB）
    alloy_path = OUT / "data/taiga/recipes/smeltery/alloy/molten_nitronite.json"
    obj = json.loads(alloy_path.read_text(encoding="utf-8"))
    if not any(i.get("fluid") == "laowu:hissing_gas" for i in obj["inputs"]):
        obj["inputs"].append({"fluid": "laowu:hissing_gas", "amount": 1})
    alloy_path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 要求4：奇点
    for mat in MATS_ORDER:
        c = MATS[mat]["color"][2:].lower()
        write_json(f"data/taiga/singularities/{mat}.json", {
            "conditions": [],
            "count": 1000,
            "displayName": f"singularity.taiga.{mat}",
            "enabled": True,
            "ingredient": {"item": f"taiga:{mat}_ingot"},
            "name": f"taiga:{mat}",
            "overlayColor": _lighten(c),
            "recipeEnabled": True,
            "timeCost": 240,
            "underlayColor": c,
        })
    for src_item, sid in ARECA_SINGULARITIES:
        write_json(f"data/tese_leshi/singularities/{sid}.json", {
            "conditions": [],
            "count": 1000,
            "displayName": f"singularity.tese_leshi.{sid}",
            "enabled": True,
            "ingredient": {"item": f"tese_leshi:{src_item}"},
            "name": f"tese_leshi:{sid}",
            "overlayColor": "e0e0e0",
            "recipeEnabled": True,
            "timeCost": 240,
            "underlayColor": "8c8c8c",
        })

    # Create 处理（对齐 tweaks/tweak.js）
    write_json("data/taiga/recipes/create/milling/random_ore_from_flint.json", {
        "type": "create:milling",
        "ingredients": [{"item": "minecraft:flint"}],
        "results": [{"item": "taiga:random_ore", "chance": 0.005}],
    })
    write_json("data/taiga/recipes/create/milling/random_ore_from_scoria.json", {
        "type": "create:milling",
        "ingredients": [{"item": "create:scoria"}],
        "results": [{"item": "taiga:random_ore", "chance": 0.05}],
    })
    write_json("data/taiga/recipes/create/milling/random_ore_from_scorchia.json", {
        "type": "create:milling",
        "ingredients": [{"item": "create:scorchia"}],
        "results": [{"item": "taiga:random_ore", "chance": 0.05}],
    })


ARECA_SINGULARITIES = [
    ("daguo_alloy_ingot", "daguo_alloy"),
    ("ancient_essence_ingot", "ancient_essence"),
    ("nether_essence_ingot", "nether_essence"),
    ("end_essence_ingot", "end_essence"),
]


def _lighten(hex6: str) -> str:
    r, g, b = int(hex6[0:2], 16), int(hex6[2:4], 16), int(hex6[4:6], 16)
    f = lambda v: min(255, int(v + (255 - v) * 0.45))
    return f"{f(r):02x}{f(g):02x}{f(b):02x}"


# ---------------------------------------------------------------------------
# 资源：纹理 / 模型 / 方块状态 / 语言
# ---------------------------------------------------------------------------

TAIGABLOCKS_JAR = next(
    (p for p in (KJS.parent / "mods").glob("*TAIGABlocks*.jar")), None)

WHFWTF_ORE_TEXTURES = ["abyssum", "aurorium", "dilithium", "eezo", "jauxum",
                       "karmesine", "osram", "ovium", "tiberium"]

# 方块 id -> 方块模型贴图 id（同名）
ALL_BLOCKS = ([f"{m}_block" for m in MATS_ORDER]
              + [f"{m}_ore" for m in ORE_MATS]
              + [i.split(":")[1] + "_block" for i in RAW_ITEMS]
              + SPECIAL_BLOCKS)

# 物品 id -> 贴图 id
SIMPLE_ITEMS = ([f"{m}_ingot" for m in MATS_ORDER]
                + [f"{m}_nugget" for m in MATS_ORDER]
                + [f"{m}_dust" for m in MATS_ORDER]
                + [f"{m}_pickaxe" for m in TOOLS]
                + [i.split(":")[1] for i in RAW_ITEMS]
                + ["random_ore"])


def _extract_jar_png(zip_name: str, rel_dst: str):
    import zipfile
    if TAIGABLOCKS_JAR is None:
        missing.append(f"<jar missing> {zip_name}")
        return
    with zipfile.ZipFile(TAIGABLOCKS_JAR) as z:
        try:
            data = z.read(zip_name)
        except KeyError:
            missing.append(f"{TAIGABLOCKS_JAR.name}!{zip_name}")
            return
    p = ensure(OUT / rel_dst)
    p.write_bytes(data)


def gen_textures():
    for mat in MATS_ORDER:
        copy_png(KJS / f"assets/taigaingots/textures/item/{mat}.png",
                 f"assets/taiga/textures/item/{mat}_ingot.png")
        copy_png(KJS / f"assets/taiganuggets/textures/item/{mat}.png",
                 f"assets/taiga/textures/item/{mat}_nugget.png")
        copy_png(REF / f"assets/taiga/textures/items/dust/{mat}.png",
                 f"assets/taiga/textures/item/{mat}_dust.png")
        copy_png(KJS / f"assets/taigametalblocks/textures/block/{mat}_block.png",
                 f"assets/taiga/textures/block/{mat}_block.png")

    for mat in WHFWTF_ORE_TEXTURES:
        copy_png(KJS / f"assets/whfwtf/textures/block/{mat}.png",
                 f"assets/taiga/textures/block/{mat}_ore.png")
    for mat in ORE_LEVEL_TAG:
        _extract_jar_png(f"assets/taigablocks/textures/block/{mat}_ore.png",
                         f"assets/taiga/textures/block/{mat}_ore.png")

    for f in (KJS / "assets/whfwtf/textures/item").glob("*.png"):
        copy_png(f, f"assets/taiga/textures/item/{f.name}")

    block_rename = {"basalt_block": "basalt_rock"}
    for f in (KJS / "assets/whfwtf/textures/block").glob("*.png"):
        name = f.stem
        if name in WHFWTF_ORE_TEXTURES:
            continue                       # 已作为矿石处理
        copy_png(f, f"assets/taiga/textures/block/{block_rename.get(name, name)}.png")

    for mat in TOOLS:
        copy_png(KJS / f"assets/taiga_pickaxe/textures/item/{mat}_pickaxe.png",
                 f"assets/taiga/textures/item/{mat}_pickaxe.png")


def gen_models():
    for item in SIMPLE_ITEMS:
        _mk("minecraft:item/generated", f"assets/taiga/models/item/{item}.json",
            textures={"layer0": f"taiga:item/{item}"})
    for blk in ALL_BLOCKS:
        _mk("minecraft:block/cube_all", f"assets/taiga/models/block/{blk}.json",
            textures={"all": f"taiga:block/{blk}"})
        _mk(f"taiga:block/{blk}", f"assets/taiga/models/item/{blk}.json")
        write_json(f"assets/taiga/blockstates/{blk}.json",
                   {"variants": {"": {"model": f"taiga:block/{blk}"}}})


def _parse_lang(path: Path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def gen_lang():
    zh = _parse_lang(REF / "assets/taiga/lang/zh_CN.lang")
    en = _parse_lang(REF / "assets/taiga/lang/en_US.lang")

    def z(key, fallback):
        return zh.get(key, fallback)

    def e(key, fallback):
        return en.get(key, fallback)

    zh_out, en_out = {}, {}

    def put(k, zv, ev):
        zh_out[k] = zv
        en_out[k] = ev

    for mat in MATS_ORDER:
        zmat = z(f"material.{mat}.name", mat)
        emat = e(f"material.{mat}.name", mat.capitalize())
        put(f"material.taiga.{mat}", zmat, emat)
        put(f"item.taiga.{mat}_ingot", z(f"item.{mat}_ingot.name", f"{zmat}锭"),
            e(f"item.{mat}_ingot.name", f"{emat} Ingot"))
        put(f"item.taiga.{mat}_nugget", z(f"item.{mat}_nugget.name", f"{zmat}粒"),
            e(f"item.{mat}_nugget.name", f"{emat} Nugget"))
        put(f"item.taiga.{mat}_dust", z(f"item.{mat}_dust.name", f"{zmat}粉"),
            e(f"item.{mat}_dust.name", f"{emat} Dust"))
        put(f"block.taiga.{mat}_block", z(f"tile.{mat}_block.name", f"{zmat}块"),
            e(f"tile.{mat}_block.name", f"{emat} Block"))
        put(f"fluid_type.taiga.molten_{mat}", f"熔融{zmat}",
            e(f"fluid.tconstruct.{mat}_fluid.name", f"Molten {emat}"))
        put(f"singularity.taiga.{mat}", f"{zmat}奇点", f"{emat} Singularity")

    for mat in ORE_MATS:
        zmat = z(f"material.{mat}.name", mat)
        emat = e(f"material.{mat}.name", mat.capitalize())
        put(f"block.taiga.{mat}_ore", z(f"tile.{mat}_ore.name", f"{zmat}矿石"),
            e(f"tile.{mat}_ore.name", f"{emat} Ore"))

    for i in RAW_ITEMS:
        name = i.split(":")[1]
        base = name.replace("raw_", "")
        zmat = z(f"material.{base}.name", base)
        emat = e(f"material.{base}.name", base.capitalize())
        if "crystal" in name:
            put(f"item.taiga.{name}", z(f"item.{name}.name", f"{zmat}水晶"),
                e(f"item.{name}.name", f"{emat} Crystal"))
            put(f"block.taiga.{name}_block", f"{zmat}水晶块", f"{emat} Crystal Block")
        else:
            put(f"item.taiga.{name}", f"{zmat}原矿", f"Raw {emat}")
            put(f"block.taiga.{name}_block", f"{zmat}原矿块", f"Raw {emat} Block")

    for mat in TOOLS:
        zmat = z(f"material.{mat}.name", mat)
        emat = e(f"material.{mat}.name", mat.capitalize())
        put(f"item.taiga.{mat}_pickaxe", f"{zmat}镐", f"{emat} Pickaxe")

    put("block.taiga.basalt_rock", "玄武岩", "Basalt Rock")
    put("block.taiga.meteorite_cobble_block", "陨石圆石块", "Meteorite Cobble Block")
    put("block.taiga.raw_meteorite_block", "陨铁原矿块", "Raw Meteorite Block")
    put("block.taiga.raw_obsidiorite_block", "黑陨铁原矿块", "Raw Obsidiorite Block")
    put("block.taiga.obsidiorite_cobble_block", "黑陨铁圆石块", "Obsidiorite Cobble Block")
    put("item.taiga.random_ore", "随机矿石", "Random Ore")
    put("fluid_type.taiga.molten_nitronite", "熔融硝化合金", "Molten Nitronite")
    put("fluid_type.taiga.blaze_halwa", "烈焰哈瓦", "Blaze Halwa")
    put("itemGroup.taiga.items", "TAIGA|物品", "TAIGA Items")
    put("itemGroup.taiga.blocks", "TAIGA|方块", "TAIGA Blocks")

    # 三个自定义特性
    put("modifier.taiga.berserker", "狂暴", "Berserker")
    put("modifier.taiga.berserker.flavor", "狂战士——更高数值，更低耐久", "Berserker - higher values, lower durability")
    put("modifier.taiga.soul_eater", "噬魂者", "Soul Eater")
    put("modifier.taiga.soul_eater.flavor", "伤害随杀敌数提升", "Damage increases as you slay")
    put("modifier.taiga.unstable", "不稳定", "Unstable")
    put("modifier.taiga.unstable.flavor", "真的，它很不稳定！", "Seriously, this is completely unstable!")

    # areca-delight 奇点
    for sid, zname, ename in (("daguo_alloy", "大锅合金", "Daguo Alloy"),
                              ("ancient_essence", "古代精华", "Ancient Essence"),
                              ("nether_essence", "下界精华", "Nether Essence"),
                              ("end_essence", "末地精华", "End Essence")):
        zh_out[f"singularity.tese_leshi.{sid}"] = f"{zname}奇点"
        en_out[f"singularity.tese_leshi.{sid}"] = f"{ename} Singularity"

    for lang, out in (("zh_cn", zh_out), ("en_us", en_out)):
        write_json(f"assets/taiga/lang/{lang}.json", dict(sorted(out.items())))


FLUID_IDS = [f"molten_{m}" for m in MATS_ORDER] + ["molten_nitronite", "blaze_halwa"]


def gen_fluid_assets():
    """流体方块与桶的模型/方块状态。

    流体方块的真实外观由流体渲染器负责，这里只需一个占位模型消除
    “missing model for variant” 告警（与 TConstruct 自身 molten_*_fluid 的做法一致）。
    """
    write_json("assets/taiga/models/block/fluid.json",
               {"textures": {"particle": "tconstruct:fluid/liquid/still"}})
    for fid in FLUID_IDS:
        write_json(f"assets/taiga/blockstates/{fid}.json",
                   {"multipart": [{"apply": {"model": "taiga:block/fluid"}}]})
        write_json(f"assets/taiga/models/item/{fid}_bucket.json", {
            "parent": "forge:item/bucket",
            "loader": "forge:fluid_container",
            "fluid": f"taiga:{fid}",
        })


def gen_assets():
    gen_textures()
    gen_models()
    gen_fluid_assets()
    gen_lang()


JAVA_DIR = Path(__file__).resolve().parent.parent / "src" / "main" / "java" / "com" / "whfwtf" / "taiga"


def gen_java_table():
    """生成 ModMaterials.java（材料名 / 颜色 / 流体温度），与数据包同源。"""
    lines = [
        "package com.whfwtf.taiga;",
        "",
        "import java.util.Arrays;",
        "import java.util.List;",
        "",
        "/**",
        " * 材料总表——由 tools/gen_content.py 从 kubejs/taiga_fluids.js 生成，请勿手改。",
        " */",
        "public final class ModMaterials {",
        "    public record Def(String name, int color, int temperature) {}",
        "",
        "    public static final List<Def> ALL = Arrays.asList(",
    ]
    body = []
    for mat in MATS_ORDER:
        d = MATS[mat]
        body.append(f'            new Def("{mat}", {d["color"]}, {d["temperature"]})')
    lines.append(",\n".join(body) + "\n    );")
    lines += [
        "}",
        "",
    ]
    p = JAVA_DIR / "ModMaterials.java"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines), encoding="utf-8")


def verify():
    """校验：生成的 JSON 中不得残留旧命名空间（白名单除外）。"""
    forbidden = ("taigaingots", "taiganuggets", "taigametalblocks", "taigafluids",
                 "taigaproperties", "whfwtf", "taigablocks", "taiga_pickaxe")
    hits = []
    for p in OUT.rglob("*.json"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for ns in forbidden:
            if ns + ":" in text:
                hits.append(f"{p.relative_to(OUT)}  <- {ns}:")
    return hits


def main():
    gen_tinkering()
    gen_recipes_copy()
    gen_manual_recipes()
    gen_tags()
    gen_worldgen()
    gen_compat()
    gen_assets()
    gen_java_table()
    print("生成完成")
    hits = verify()
    if hits:
        print(f"!! 残留旧命名空间 {len(hits)} 处：")
        for h in hits[:40]:
            print("  ", h)
    else:
        print("ID 校验通过：无残留旧命名空间")
    if missing:
        print(f"缺失来源 {len(missing)} 个，前 30 条：")
        for m in missing[:30]:
            print("  MISSING", m)
    else:
        print("无缺失来源")


if __name__ == "__main__":
    main()
