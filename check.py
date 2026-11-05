#!/usr/bin/env python3
"""發布前檢查：格式、條數 1,000～30,000、比上一版少不超過一成、檔案 2 MB 以內。沒過就結束碼 1，不發布。"""
import json, os, sys
new_path, old_path = sys.argv[1], sys.argv[2]
new = json.load(open(new_path))
assert new.get("format") == 1, "format 不對"
n = len(new["entries"])
assert 1000 <= n <= 30000, f"條數 {n} 不在 1,000～30,000"
assert os.path.getsize(new_path) <= 2_000_000, "檔案超過 2 MB"
for e in new["entries"]:
    assert isinstance(e.get("t"), str) and 2 <= len(e["t"]) <= 40, f"名稱不對：{e}"
    assert all(isinstance(z, str) and len(z) <= 40 for z in e.get("zh", [])), f"中文名不對：{e}"
if os.path.exists(old_path):
    old = json.load(open(old_path))
    m = len(old["entries"])
    assert n >= m * 0.9, f"條數從 {m} 掉到 {n}，超過一成"
    assert new["version"] > old["version"], "版本沒有比較新"
print(f"檢查通過：{n} 條")
