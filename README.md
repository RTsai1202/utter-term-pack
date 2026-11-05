# Utter 術語詞包

語音輸入 App Utter 用的公開術語詞包：科技、產品、公司的英文名與正式中文名。

- 資料來源：[Wikidata](https://www.wikidata.org/)（CC0 1.0）。只收英文名、中文名與類別，不含任何使用者資料。
- 每週一由 GitHub Actions 重新產生（`build.py`），檢查（`check.py`）後用 Ed25519 簽章（`sign.py`）。檢查沒過就不發布。
- App 只接受用 `public-key.txt` 驗得過、版本比較新的詞包；驗不過一律沿用舊版。
- 下載網址：`https://raw.githubusercontent.com/RTsai1202/utter-term-pack/main/term-pack.json`（簽章在同名 `.sig`）。

程式以 MIT 授權；詞包資料依 Wikidata 的 CC0 1.0。
