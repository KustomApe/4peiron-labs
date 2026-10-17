# 公開資産の棚卸し

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームの一員です。契約書と診断範囲（スコープ）には双方が署名済みで、
今回の作業は「インターネットから見える資産が、会社の資産台帳と一致しているか」を書類の上で確かめることです。
対象のホストにアクセスはしません。手元の書き出しだけを読み、報告書に載せる指摘をまとめます。

情報システム部から、正式な資産台帳、権威 DNS から書き出した公開ゾーン、証明書の透明性（CT）ログを
検索して保存した JSON を受け取りました。評価の基準日は **2026-10-01（UTC）** です。

## 証拠ファイル

| ファイル | 内容 |
|---|---|
| `asset_inventory.csv` | 会社の正式な資産台帳。`exposure` は公開（`public`）か社内限定（`internal`）か、`status` は稼働中（`active`）か廃止済み（`retired`）か |
| `dns/example.co.jp.zone` | `example.co.jp` の公開ゾーン（BIND 形式、2026-09-30 書き出し） |
| `dns/sample-shop.example.zone` | ブランド用ドメイン `sample-shop.example` の公開ゾーン |
| `ct_log.json` | 自社ドメインの証明書を CT ログで検索した結果（crt.sh と同じ項目） |

## 設問

答えはどれも完全修飾ドメイン名（FQDN）で、**小文字、末尾のドットなし**で書きます。形式の例: `4P{host.example.co.jp}`

| # | サイトのフラグ名 | 点 | 設問 |
|---|---|---|---|
| 1 | `shadow-host` | 10 | 公開 DNS で名前解決できる（A / AAAA / CNAME がある）のに、資産台帳に載っていないホスト名はどれですか。台帳の管理外で立てられた資産として報告します。 |
| 2 | `expired-cert` | 10 | 公開 DNS に載っているホスト名のうち、CT ログにある**いちばん新しい証明書**が、基準日の時点ですでに期限切れのものはどれですか。証明書の更新漏れとして報告します。 |
| 3 | `exposed-admin` | 20 | 資産台帳では社内限定（`internal`）とされているのに、公開ゾーンにグローバル IP アドレスで載っている管理画面のホスト名はどれですか。公開範囲の見直しが必要な指摘として報告します。 |

## ヒント

1. 台帳のホスト名には大文字や末尾のドットが混じっています。比べる前に表記をそろえましょう。ゾーンファイルでは、ドットで終わらない名前に `$ORIGIN` が付きます。`_dmarc` のような `_` で始まる名前はホストではありません。
2. 1 つのホストに証明書が何枚もあります。同じ証明書が precert と最終証明書の 2 行で載ることもあります。ホストごとに `not_before` がいちばん新しいものだけを見ましょう。
3. 名前に `admin` が入っていても、公開するために作った文書サイトもあります。名前だけでなく、台帳の `exposure` 列と突き合わせましょう。

## 片付け

```bash
docker compose down -v
```

## English

# Public Asset Inventory

## Scenario

You are on a security assessment team engaged by Sample Corp. Both sides have signed the contract and the scope.
This task is a paper review: check whether the assets visible from the internet match the company's asset
inventory. You do not touch any host. You read the exports you were given and write findings for the report.

The IT department handed you the official asset inventory, the public zones exported from the authoritative
DNS server, and a saved JSON search of Certificate Transparency (CT) logs. The reference date for the assessment
is **2026-10-01 (UTC)**.

## Evidence files

| File | What it is |
|---|---|
| `asset_inventory.csv` | The official asset inventory. `exposure` is `public` or `internal`; `status` is `active` or `retired` |
| `dns/example.co.jp.zone` | Public zone for `example.co.jp` (BIND format, exported 2026-09-30) |
| `dns/sample-shop.example.zone` | Public zone for the brand domain `sample-shop.example` |
| `ct_log.json` | CT log search results for the company's domains (same fields as crt.sh) |

## Questions

Every answer is a fully qualified domain name, **lowercase, no trailing dot**. Format example: `4P{host.example.co.jp}`

| # | Flag name | Points | Question |
|---|---|---|---|
| 1 | `shadow-host` | 10 | Which hostname resolves in public DNS (has an A / AAAA / CNAME record) but is missing from the asset inventory? You will report it as an asset set up outside inventory control. |
| 2 | `expired-cert` | 10 | Among the hostnames in public DNS, which one's **newest** certificate in the CT log had already expired on the reference date? You will report it as a missed renewal. |
| 3 | `exposed-admin` | 20 | Which management console is marked `internal` in the inventory but is published in the public zone with a global IP address? You will report it as exposure that needs to be reviewed. |

## Hints

1. Inventory hostnames mix uppercase and trailing dots. Normalize before comparing. In a zone file, names that do not end with a dot get `$ORIGIN` appended. Names starting with `_`, such as `_dmarc`, are not hosts.
2. Each host has several certificates, and one certificate can appear twice (precertificate and final certificate). For each host, look only at the one with the latest `not_before`.
3. A name containing `admin` can still be a documentation site that is meant to be public. Compare against the inventory's `exposure` column, not just the name.

## Cleanup

```bash
docker compose down -v
```
