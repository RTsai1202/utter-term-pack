#!/usr/bin/env python3
"""從 Wikidata（CC0）抽科技、產品、公司的多語名稱，產生 Utter 的公開術語詞包（未簽章）。

用法：python3 Tools/term-pack/build.py --out <term-pack.json> [--min-sitelinks 20]
只送 SPARQL 查詢（不含任何使用者資料）；依序送、帶 User-Agent、失敗退避（Wikimedia API 禮節）。
"""
import argparse, csv, io, json, re, sys, time, urllib.parse, urllib.request, datetime

# P31 直接屬於這些類別的項目（Q 代碼 2026-11-05 由 Wikidata API 核對英文標籤）
CLASSES = {
    "Q7397": "software", "Q117349473": "ai-model", "Q115305900": "llm", "Q9143": "programming-language",
    "Q1668024": "online-service", "Q9135": "os", "Q1130645": "open-source", "Q4830453": "business",
    "Q783794": "company", "Q3966": "hardware", "Q166142": "application", "Q620615": "mobile-app",
    "Q6368": "web-browser", "Q193424": "web-service", "Q3220391": "social-network", "Q870780": "chatbot",
    "Q19723451": "smartphone-model", "Q431289": "brand", "Q7889": "video-game", "Q218616": "game-platform",
    "Q341": "free-software", "Q1058914": "software-company",
}
UA = "UtterTermPack/0.1 (https://github.com/RTsai1202/utter-term-pack)"
QUERY = """SELECT ?item ?sl ?en ?zh ?zhh ?zhg WHERE {
  ?item wdt:P31 wd:%s ; wikibase:sitelinks ?sl . FILTER(?sl >= %d)
  ?item rdfs:label ?en FILTER(lang(?en)="en")
  OPTIONAL { ?item rdfs:label ?zh FILTER(lang(?zh)="zh-tw") }
  OPTIONAL { ?item rdfs:label ?zhh FILTER(lang(?zhh)="zh-hant") }
  OPTIONAL { ?item rdfs:label ?zhg FILTER(lang(?zhg)="zh") }
}"""

def fetch(cls, min_sl):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY % (cls, min_sl)})
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"Accept": "text/csv", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
        except Exception as e:
            print(f"{cls} 第 {attempt + 1} 次失敗：{e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"{cls} 一直查不到，停止（不發布不完整的詞包）")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-sitelinks", type=int, default=20)
    ap.add_argument("--max", type=int, default=30000)
    a = ap.parse_args()
    entries = {}
    for cls, cat in CLASSES.items():
        rows = fetch(cls, a.min_sitelinks)
        print(f"{cls} {cat}: {len(rows)}", file=sys.stderr)
        for r in rows:
            en = re.sub(r"\s*\([^)]*\)\s*$", "", r["en"].strip())
            if not (2 <= len(en) <= 40) or not re.search(r"[A-Za-z]", en):
                continue
            qid = r["item"].rsplit("/", 1)[-1]
            e = entries.setdefault(qid, {"id": qid, "t": en, "c": cat, "sl": int(r["sl"]), "zh": []})
            for z in (r.get("zh"), r.get("zhh"), r.get("zhg")):
                # 「Slack (軟體)」這類消歧義括號拿掉
                z = re.sub(r"\s*[（(][^）)]*[）)]\s*$", "", (z or "").strip())
                if z and z != en and z not in e["zh"] and re.search(r"[一-鿿]", z):
                    e["zh"].append(z)
        time.sleep(2)
    items = sorted(entries.values(), key=lambda e: (-e["sl"], e["t"]))[: a.max]
    pack = {
        "format": 1,
        "version": int(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H")),
        "source": "Wikidata (CC0 1.0), https://www.wikidata.org/",
        # 不放 Wikidata id：App 用不到
        "entries": [{"t": e["t"], "c": e["c"], "zh": e["zh"]} for e in items],
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, separators=(",", ":"))
    print(f"寫出 {len(items)} 條：{a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
