import json, re, zipfile, shutil, os

TSRG = "C:/Users/111/.gradle/caches/forge_gradle/minecraft_user_repo/de/oceanlabs/mcp/mcp_config/1.20.1-20230612.114412/srg_to_official_1.20.1.tsrg"
JAR  = "E:/111/mod.dev/taiga3/libs/architectury-9.2.14-forge.jar"
BACK = "E:/111/mod.dev/taiga3/libs/architectury-9.2.14-forge.jar.bak"
REFMAP_NAME = "architectury-forge-refmap.json"

srg2off = {}
with open(TSRG, encoding="utf-8") as f:
    for line in f:
        if not line.startswith("\t"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        tok = parts[0]
        if re.match(r'^[mf]_\d+_$', tok):
            off = parts[2] if '(' in parts[1] else parts[1]
            srg2off[tok] = off

def remap_value(v):
    def repl(m):
        return srg2off.get(m.group(0), m.group(0))
    return re.sub(r'[mf]_\d+_', repl, v)

def walk(o):
    if isinstance(o, dict):
        for k in list(o.keys()):
            o[k] = walk(o[k])
        return o
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, str):
        return remap_value(o)
    return o

with zipfile.ZipFile(JAR) as z:
    data = z.read(REFMAP_NAME).decode("utf-8")
refmap = json.loads(data)
refmap = walk(refmap)
new_refmap = json.dumps(refmap, indent=2, ensure_ascii=False)

if not os.path.exists(BACK):
    shutil.copy(JAR, BACK)
    print("backed up original ->", BACK)

tmp = JAR + ".tmp"
with zipfile.ZipFile(JAR) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == REFMAP_NAME:
            zout.writestr(item, new_refmap)
        else:
            zout.writestr(item, zin.read(item.filename))
shutil.move(tmp, JAR)
print("repackage done:", JAR)

mm = refmap["mappings"]["named:intermediary"]["dev/architectury/mixin/forge/MixinMinecraft"]
print("patched MixinMinecraft:", json.dumps(mm, ensure_ascii=False))
print("patched MixinChunkSerializer:",
      json.dumps(refmap["mappings"]["named:intermediary"]["dev/architectury/mixin/forge/MixinChunkSerializer"], ensure_ascii=False))
