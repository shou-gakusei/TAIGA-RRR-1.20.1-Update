"""把 mod jar 内 refmap 的 SRG 中间名 (m_xxxxx_/f_xxxxx_) 还原成 official 名。

背景：ForgeGradle 6 在 dev 环境做 deobf 时只 remap 了 refmap 里的类名，
方法/字段名仍保留 SRG，导致 Mixin 在 official 命名的 dev 运行时里
"could not find any targets matching 'Lnet/minecraft/client/Minecraft;m_91270_()...'"。

用法:
    python tools/patch_refmaps.py <jar> [<jar> ...]
    python tools/patch_refmaps.py --all            # libs/*.jar + 全部 deobf 缓存 jar
"""
import os
import re
import shutil
import sys
import zipfile

TSRG = ("C:/Users/111/.gradle/caches/forge_gradle/minecraft_user_repo/de/oceanlabs/"
        "mcp/mcp_config/1.20.1-20230612.114412/srg_to_official_1.20.1.tsrg")
CACHE = "C:/Users/111/.gradle/caches/forge_gradle/deobf_dependencies/local"
LIBS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs")

SRG_RE = re.compile(r'[mf]_\d+_')


def load_map():
    m = {}
    with open(TSRG, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("\t"):
                continue
            p = line.split()
            if len(p) < 2:
                continue
            tok = p[0]
            if SRG_RE.fullmatch(tok):
                m[tok] = p[2] if "(" in p[1] else p[1]
    return m


def patch_jar(path, srg2off):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        hits = []
        contents = {}
        for n in names:
            if not n.endswith(".json"):
                continue
            try:
                t = z.read(n).decode("utf-8")
            except Exception:
                continue
            if not SRG_RE.search(t):
                continue
            new = SRG_RE.sub(lambda mo: srg2off.get(mo.group(0), mo.group(0)), t)
            if new != t:
                contents[n] = new
                hits.append((n, len(SRG_RE.findall(t))))
        if not contents:
            return None
        if not os.path.exists(path + ".bak"):
            shutil.copy2(path, path + ".bak")
        tmp = path + ".tmp"
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = contents.get(item.filename)
                zout.writestr(item, data.encode("utf-8") if data is not None else zin.read(item.filename))
    os.replace(tmp, path)
    return hits


def collect_all():
    jars = []
    if os.path.isdir(LIBS):
        jars += [os.path.join(LIBS, f) for f in os.listdir(LIBS) if f.endswith(".jar")]
    for root, _, fs in os.walk(CACHE):
        jars += [os.path.join(root, f) for f in fs if f.endswith(".jar")]
    return jars


def main():
    args = sys.argv[1:]
    jars = collect_all() if (not args or args[0] == "--all") else args
    srg2off = load_map()
    print("srg tokens:", len(srg2off))
    for j in jars:
        try:
            hits = patch_jar(j, srg2off)
        except Exception as e:
            print("!! FAIL", j, e)
            continue
        if hits:
            print("patched", os.path.basename(j), hits)
    print("done")


if __name__ == "__main__":
    main()
