"""生成 TAIGA3 的 FTB Quests 章节（config/ftbquests/quests/chapters/*.snbt）。

两个章节：
  1. taiga_alloys       —— 合金线引导（基础材料横排成链，合金按依赖树分层排布）
  2. taiga_integration  —— 与 Create / 拔刀剑 / 匠魂 / 无尽贪婪的联动

数据全部取自项目自身：
  - 材料表   src/main/java/com/whfwtf/taiga/ModMaterials.java
  - 合金配方 src/main/resources/data/taiga/recipes/smeltery/alloy/*.json
  - 中文名   src/main/resources/assets/taiga/lang/zh_cn.json

用法: python tools/gen_ftbq.py
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "run", "config", "ftbquests", "quests")

_lang = json.load(open(os.path.join(ROOT, "src/main/resources/assets/taiga/lang/zh_cn.json"), encoding="utf-8"))


def zh(key, default):
    return _lang.get(key, default)


def pretty(name):
    return name.replace("_", " ").title()


mats = re.findall(r'new Def\("([a-z_]+)"', open(
    os.path.join(ROOT, "src/main/java/com/whfwtf/taiga/ModMaterials.java"), encoding="utf-8").read())

alloys = {}
for f in glob.glob(os.path.join(ROOT, "src/main/resources/data/taiga/recipes/smeltery/alloy/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    out = d["result"]["fluid"].split(":")[1].replace("molten_", "")
    ins = [(i["fluid"].split(":")[1].replace("molten_", ""), i["amount"]) for i in d["inputs"]]
    alloys[out] = {"inputs": ins, "temp": d["temperature"], "out": d["result"]["amount"]}

tier = {}


def calc_tier(m, stack=()):
    if m in tier:
        return tier[m]
    if m not in alloys:
        tier[m] = 0
        return 0
    if m in stack:
        raise RuntimeError("alloy cycle at " + m)
    v = 1 + max(calc_tier(i, stack + (m,)) for i, _ in alloys[m]["inputs"])
    tier[m] = v
    return v


for m in alloys:
    calc_tier(m)

base_mats = [m for m in mats if m not in alloys]

_seq = [0]


def nid(prefix):
    _seq[0] += 1
    return "%s%012X" % (prefix, _seq[0])


# ---------------- SNBT 序列化 ----------------
def snbt_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def snbt_val(v, indent=1):
    if isinstance(v, bool):
        return "1b" if v else "0b"
    if isinstance(v, float):
        return repr(v) + "d"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return snbt_str(v)
    if isinstance(v, dict):
        return compound(v, indent + 1)
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "[" + ", ".join(snbt_val(x) for x in v) + "]"
        pad = "\t" * (indent + 1)
        return "[\n" + ",\n".join(pad + snbt_val(x, indent + 1) for x in v) + "\n" + "\t" * indent + "]"
    raise TypeError(v)


def compound(d, indent):
    pad = "\t" * indent
    lines = ["%s%s: %s" % (pad, k, snbt_val(v, indent)) for k, v in d.items()]
    return "{\n" + ",\n".join(lines) + "\n" + "\t" * (indent - 1) + "}"


def write_chapter(name, chapter, quests):
    os.makedirs(os.path.join(OUT, "chapters"), exist_ok=True)
    body = ",\n".join(compound(q, 2) for q in quests)
    head = {k: v for k, v in chapter.items() if k != "quests"}
    txt = compound(head, 1)
    txt = txt[:txt.rindex("\n}")].rstrip() + ",\n\tquests: [\n" + body + "\n\t]\n}\n"
    path = os.path.join(OUT, "chapters", name + ".snbt")
    open(path, "w", encoding="utf-8").write(txt)
    print("wrote", path, len(quests), "quests")


def quest(qid, x, y, title, desc, tasks, deps, shape=None, size=1.0, rewards=None, icon=None):
    q = {"id": qid, "x": float(x), "y": float(y), "title": title, "description": desc,
         "tasks": tasks, "rewards": rewards or [{"id": nid("3A"), "type": "xp", "xp": 5}],
         "dependencies": deps, "size": size}
    if shape:
        q["shape"] = shape
    if icon:
        q["icon"] = icon
    return q


def item_task(item, count=1):
    return {"id": nid("2A"), "type": "item", "item": item, "count": count}


def fluid_task(fluid, amount):
    return {"id": nid("2A"), "type": "fluid", "fluid": fluid, "amount": amount}


def check_task():
    return {"id": nid("2A"), "type": "checkmark"}

def known_ids():
    known = set()
    # taiga 自身
    for m in mats:
        for suf in ("_ingot", "_nugget", "_dust", "_block", "_ore"):
            known.add("taiga:" + m + suf)
    known |= {"taiga:random_ore", "taiga:dilithium_crystal", "taiga:tiberium_crystal",
              "taiga:tsb_blade", "taiga:tsb_blade_blank", "taiga:raw_meteorite_block",
              "taiga:meteorite_cobble_block", "taiga:basalt_rock", "taiga:obsidiorite_cobble_block"}
    for raw in re.findall(r'"(raw_[a-z_]+)"', open(os.path.join(
            ROOT, "src/main/java/com/whfwtf/taiga/ModItems.java"), encoding="utf-8").read()):
        known.add("taiga:" + raw)
    # 依赖 jar 的 lang
    jar_lang = {
        "TConstruct-1.20.1-3.10.2.92.jar": "tconstruct",
        "SlashBladeResharped-1.20.1-1.9.65.jar": "slashblade",
        "tinker_rapier-1.0.1-1.20.1.jar": "tinker_rapier",
    }
    import zipfile
    for jar, ns in jar_lang.items():
        path = os.path.join(ROOT, "libs", jar)
        if not os.path.exists(path):
            continue
        z = zipfile.ZipFile(path)
        for n in z.namelist():
            if n.endswith("lang/en_us.json"):
                for k in json.loads(z.read(n)).keys():
                    for pre in ("item.", "block."):
                        if k.startswith(pre + ns + "."):
                            rest = k[len(pre + ns + "."):]
                            if "." in rest or " " in rest:
                                continue
                            known.add(ns + ":" + rest)
    return known


def validate(quests, cid):
    good = known_ids()
    bad = []
    for q in quests:
        for task in q["tasks"]:
            item = task.get("item")
            if item and not item.startswith("minecraft:") and item not in good:
                bad.append((q["title"], item))
        icon = q.get("icon")
        if icon and not icon.startswith("minecraft:") and icon not in good:
            bad.append((q["title"] + " (icon)", icon))
    for title, item in bad:
        print("  !! 未知物品:", cid, "|", title, "->", item)
    return bad




# ================= 章节 1：合金线 =================
Q1 = []
ids1 = {}

# 入口
ids1["intro"] = nid("1A")
Q1.append(quest(ids1["intro"], 0, 0, "从一块原矿开始",
                ["TAIGA 有 37 种材料、21 种合金，全部围绕匠魂的冶炼炉展开。",
                 "第一步：把原矿丢进冶炼炉熔化，再在浇筑台上浇筑成锭。",
                 "任务线会按「基础材料 → 一级合金 → 二级 → 三级 → 四级」逐层展开。"],
                [item_task("taiga:aurorium_ingot")], []))

ids1["smeltery"] = nid("1A")
Q1.append(quest(ids1["smeltery"], 0, 2, "冶炼炉三件套",
                ["冶炼炉控制器 + 焦黑储罐/排液口 + 浇筑台。",
                 "本包 21 种合金全部在 800K 熔炼，普通岩浆（1000K）足够；",
                 "只有 duranite / niob / nucleum 这类高熔点材料需要更热的燃料。"],
                [item_task("tconstruct:smeltery_controller")], [ids1["intro"]], shape="gear"))

ids1["cast"] = nid("1A")
Q1.append(quest(ids1["cast"], 0, 4, "浇筑与铸造",
                ["熔融金属从排液口灌进铸型台就能得到锭、粒、粉。",
                 "合金的做法：把两种以上的熔融金属倒进同一个排液口，炉内会按配方自动合成。"],
                [item_task("tconstruct:seared_table")], [ids1["smeltery"]], shape="gear"))

# 基础材料横排成链：按被引用次数排序，常用的放中间（左右交替展开），减少连线交叉
usage = {m: 0 for m in base_mats}
for a in alloys:
    for s, _ in alloys[a]["inputs"]:
        if s in usage:
            usage[s] += 1
ranked = sorted(base_mats, key=lambda m: -usage[m])
order = []
for i, m in enumerate(ranked):          # 0,-1,1,-2,2...
    if i == 0:
        order.append(m)
    elif i % 2 == 1:
        order.append(m)
    else:
        order.append(m)
base_order = []
right, left = [], []
for i, m in enumerate(ranked):
    (left if i % 2 == 1 else right).append(m)
base_order = list(reversed(left)) + right
STEP = 1.75
base_x = {m: (i - (len(base_order) - 1) / 2.0) * STEP for i, m in enumerate(base_order)}

prev = ids1["cast"]
base_ids = {}
for i, m in enumerate(base_order):
    name = zh("item.taiga.%s_ingot" % m, pretty(m) + "锭")
    qid = nid("1A")
    base_ids[m] = qid
    Q1.append(quest(qid, base_x[m], 6, name,
                    ["熔化 %s 的原矿 / 矿石 → 熔融%s（taiga:molten_%s）。" % (name, name, m),
                     "浇筑成锭即可，后续合金都从这些熔融金属开始。"] if i else
                    ["先熔这一种：%s。" % name,
                     "熔化原矿 → 排液 → 浇筑成锭。"],
                    [item_task("taiga:%s_ingot" % m)], [prev]))
    prev = qid

# 合金按依赖树排：x = 父节点 x 均值，同层去重叠
alloy_ids = {}
alloy_x = {}
for t in (1, 2, 3, 4):
    row = sorted([a for a in alloys if tier[a] == t])
    for a in row:
        parents = [alloy_x[s] if s in alloy_x else None for s, _ in alloys[a]["inputs"]]
        parents = [p for p in parents if p is not None]
        if not parents:                       # 全部由基础材料合成
            srcs = [s for s, _ in alloys[a]["inputs"] if s in base_ids]
            idxs = [base_mats.index(s) for s in srcs if s in base_mats]
            alloy_x[a] = (sum(base_x[base_order[j]] for j in idxs) / len(idxs)) if idxs else 0.0
        else:
            alloy_x[a] = sum(parents) / len(parents)
    # 同层居中 + 避免重叠
    if row:
        mid = sum(alloy_x[a] for a in row) / len(row)
        for a in row:
            alloy_x[a] -= mid
    row.sort(key=lambda a: alloy_x[a])
    for i in range(1, len(row)):
        if alloy_x[row[i]] - alloy_x[row[i - 1]] < 2.2:
            alloy_x[row[i]] = alloy_x[row[i - 1]] + 2.2
    for a in row:
        info = alloys[a]
        name = zh("item.taiga:%s_ingot" % a, "") or ""
        name = zh("item.taiga.%s_ingot" % a, pretty(a) + "锭")
        lines = ["熔炼温度 %dK，投入：" % info["temp"]]
        for src, amt in info["inputs"]:
            sn = zh("item.taiga.%s_ingot" % src, pretty(src) + "锭")
            lines.append("· %s ×%d" % (sn, amt))
        lines.append("→ 熔融%s ×%d" % (name, info["out"]))
        deps = []
        for s, _ in info["inputs"]:
            if s in base_ids:
                deps.append(base_ids[s])
            elif s in alloy_ids:
                deps.append(alloy_ids[s])
        qid = nid("1A")
        alloy_ids[a] = qid
        if a == "nitronite":
            tasks = [fluid_task("taiga:molten_nitronite", 1000)]
        else:
            tasks = [item_task("taiga:%s_ingot" % a)]
        Q1.append(quest(qid, alloy_x[a], 6 + 2.0 * t, "%s · T%d" % (name, t), lines, tasks, deps or [ids1["cast"]]))

# 旁支
Q1.append(quest(nid("1A"), 3.5, 2, "三条自定义特性",
                ["berserker 狂战士：命中伤害翻倍，额外损耗耐久。",
                 "soul_eater 噬魂：击杀叠加额外攻击力。",
                 "unstable 不稳定：不稳定就是不稳定。",
                 "把带这些特性的工具做出来，任务自然会告诉你效果。"],
                [check_task()], [ids1["cast"]], shape="diamond"))

Q1.append(quest(nid("1A"), 6.5, 2, "匠魂工具入门",
                ["材料 → 部件 → 工具锻造台组装。",
                 "同一材料做刀头/手柄数值不同，自己配。"],
                [item_task("tconstruct:pickaxe")], [ids1["cast"]], shape="gear"))

last = [alloy_ids[a] for a in alloys if tier[a] == 4]
Q1.append(quest(nid("1A"), 0, 6 + 2 * 5 + 1, "合金线完成",
                ["21 种合金全部点亮，你已经掌握 TAIGA 的完整材料链。",
                 "下一章：把它们交给 Create、拔刀剑和匠魂强化。"],
                [check_task()], last, shape="hexagon", size=1.5))

validate(Q1, "taiga_alloys")
write_chapter("taiga_alloys", {
    "filename": "taiga_alloys", "id": "0F1A000000000001", "group": "", "order_index": 0,
    "title": "TAIGA · 合金线", "subtitle": "从原矿到 21 种合金",
    "icon": "taiga:adamant_ingot", "default_quest_shape": "circle",
    "progression_mode": "flexible",
}, Q1)

# ================= 章节 2：联动 =================
Q2 = []
r = nid("1A")
Q2.append(quest(r, 0, 0, "本章说明",
                ["TAIGA 不是一个封闭的模组，材料链会接进包里的其它玩法：",
                 "· Create 机械动力：研磨、搅拌、压板",
                 "· 拔刀剑：重锋 + 刀锻冶匠魂",
                 "· 匠魂：强化与特性",
                 "· 无尽贪婪：奇点"],
                [check_task()], [], shape="hexagon"))

q = nid("1A")
Q2.append(quest(q, -3, 2, "Create · 把燧石磨成矿",
                ["机械动力的研磨机：燧石 → 随机矿（0.5%）；",
                 "火山岩 scorchia / scoria → 随机矿（5%）。",
                 "这是早期拿到 TAIGA 矿石最省事的路子之一。"],
                [item_task("taiga:random_ore")], [r]))

q2 = nid("1A")
Q2.append(quest(q2, 0, 4, "匠魂 · 给工具上特性",
                ["把 berserker / soul_eater / unstable 贴在工具上试试。",
                 "强化台的槽位不够就先做强化槽。"],
                [check_task()], [q], shape="diamond"))

q3 = nid("1A")
Q2.append(quest(q3, 3, 6, "拔刀剑 · 重锋",
                ["拔刀剑的伤害、Refine、耀魂都在刀本身的 BladeState 里。",
                 "先拿到一把最普通的拔刀剑，再考虑刀锻冶匠魂的专属刀。"],
                [item_task("slashblade:slashblade")], [q2], icon="minecraft:iron_sword"))

q4 = nid("1A")
Q2.append(quest(q4, 6, 8, "刀锻冶匠魂",
                ["匠魂材料 + 刀胚 → 一把由材料决定数值的拔刀剑。",
                 "白鞘 / 大太刀两条线都会在这里展开（移植中）。"],
                [check_task()], [q3], shape="hexagon"))

q5 = nid("1A")
Q2.append(quest(q5, -6, 4, "匠魂西洋剑 · 兼容验证",
                ["同作者的 tinker_rapier 已确认与 TAIGA 的 37 种材料共存。",
                 "它的细剑刃（slender_blade）可以吃 TAIGA 材料。"],
                [item_task("tinker_rapier:rapier_tic")], [r], shape="gear"))

q6 = nid("1A")
Q2.append(quest(q6, -6, 6, "无尽贪婪 · 奇点",
                ["Re-Avaritia 会为 TAIGA 的每种材料自动生成奇点配方。",
                 "压缩机制造机里把 1000 个锭压成奇点。"],
                [check_task()], [q5], shape="diamond"))

validate(Q2, "taiga_integration")
write_chapter("taiga_integration", {
    "filename": "taiga_integration", "id": "0F1A000000000002", "group": "", "order_index": 1,
    "title": "TAIGA · 联动", "subtitle": "Create / 拔刀剑 / 匠魂 / 无尽贪婪",
    "icon": "tconstruct:smeltery_controller", "default_quest_shape": "circle",
    "progression_mode": "flexible",
}, Q2)

# ---------------- 物品 id 校验 ----------------
data_snbt = os.path.join(OUT, "data.snbt")
if not os.path.exists(data_snbt):
    open(data_snbt, "w", encoding="utf-8").write("{\n\tversion: 1\n}")

print("base:", len(base_mats), "alloys:", len(alloys))
