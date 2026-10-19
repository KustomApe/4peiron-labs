# 深刻度の決め方（SS 社 診断チーム、2026 年版）

## 1. 起こりやすさ × 影響 で決める

| 起こりやすさ ＼ 影響 | low | medium | high |
|---|---|---|---|
| **low**    | Low    | Low    | Medium |
| **medium** | Low    | Medium | High |
| **high**   | Medium | High   | Critical |

## 2. 公開範囲で調整する

対象が社内からしか届かない（`exposure` が `internal`）ときは、1 段下げる（Critical → High → Medium → Low）。
Low より下にはしない。インターネットから届く（`internet`）ときはそのまま。

## 3. 載せてはいけないもの

`evidence` に、パスワード・トークン・秘密鍵・セッションの値などの**秘密の値をそのまま書かない**。
`********` のように伏せるか、先頭の数文字だけを残す（例: `sk_test_ab…`）。

## 4. 重複

同じ対象（`host` と `location`）の同じ種類（`category`）の所見は 1 つにまとめる。
残すのは先に書かれたもの（`id` の番号が小さいほう）で、あとのものは削る。
