# 階層化（tiering）の決まり（情報システム部、2026-04 版）

- **Tier 0**: ドメインそのものを管理できるもの。DC（`dc01`・`dc02`）と、次のグループに
  **直接または入れ子で**入っているアカウント: `Domain Admins`、`Enterprise Admins`、`Schema Admins`、`Administrators`
- **Tier 1**: サーバー（`hosts.csv` で tier 1）
- **Tier 2**: 社員の端末（`hosts.csv` で tier 2）

Tier 0 のアカウントは、Tier 1・Tier 2 の機器に**対話型（ログオンの種類 2）やリモートデスクトップ（10）で
ログオンしてはいけない**。資格情報が下の階層の機器のメモリに残るため。
ネットワーク経由のログオン（3）やサービス（5）は、この決まりの対象外とする。
