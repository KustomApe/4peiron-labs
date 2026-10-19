# 所見の下書きを直す

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームのまとめ役です。3 人の診断員が書いた所見の下書き
（`findings_draft.json`）がそろいました。報告書にする前に、チームの決まり（`rubric.md`）に沿って
品質チェックをしてください。

対象の機器にはアクセスしません。下書きと決まりだけを読みます。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `findings_draft.json` | 所見の下書き 12 件。起こりやすさ（`likelihood`）・影響（`impact`）・公開範囲（`exposure`）・書いた人がつけた深刻度（`severity`）・証拠の抜き書き（`evidence`） |
| `rubric.md` | 深刻度の決め方・載せてはいけないもの・重複のまとめ方 |

調査用のコンテナには `python3` と `jq` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 決まりに従ってまとめるとき、重複として削る所見は？ | `duplicate` | 10 | 所見の ID。`4P{F-00}` の形 |
| 2. `evidence` に、秘密の値を伏せずにそのまま書いてしまった所見は？ | `secret-leak` | 10 | 所見の ID。`4P{F-00}` の形 |
| 3. 重複を削ったあと、書いた人がつけた深刻度が決まりで求めたものと違う所見は？ | `wrong-severity` | 20 | 所見の ID。`4P{F-00}` の形 |
| 4. 重複を削り、深刻度を決まりのとおりに直すと、High 以上（High と Critical）の所見は何件？ | `high-count` | 30 | 件数。`4P{10}` の形 |

## ヒント

1. タイトルの言い回しは人によって違います。比べるのは `host`・`location`・`category` の 3 つです。
2. `********` や、先頭の数文字のあとを `…` で切ったものは、伏せてあります。
3. まず表で深刻度を出し、`exposure` が `internal` なら 1 段下げます。Low より下にはなりません。
4. 3 で見つけた所見も、直した深刻度で数えます。

## 片付け

```bash
docker compose down -v
```

## English

# Fixing draft findings

### Scenario

You lead a security assessment team under contract with Sample Corp. The draft findings from three testers
(`findings_draft.json`) are in. Before they go into the report, run a quality check against the team's rules (`rubric.md`).

You do not touch any target system. Read only the drafts and the rules.

### Evidence

| File | Contents |
|---|---|
| `findings_draft.json` | Twelve draft findings: `likelihood`, `impact`, `exposure`, the author's `severity` and an `evidence` excerpt |
| `rubric.md` | How to rate severity, what must not appear, and how to merge duplicates |

The analyst container has `python3` and `jq`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Following the rules, which finding is removed as a duplicate? | `duplicate` | 10 | The finding ID: `4P{F-00}` |
| 2. Which finding writes a secret value into `evidence` without masking it? | `secret-leak` | 10 | The finding ID: `4P{F-00}` |
| 3. After removing the duplicate, which finding's author-assigned severity differs from what the rules give? | `wrong-severity` | 20 | The finding ID: `4P{F-00}` |
| 4. After removing the duplicate and correcting severities, how many findings are High or above (High and Critical)? | `high-count` | 30 | The count: `4P{10}` |

### Hints

1. Authors word titles differently. Compare `host`, `location` and `category`.
2. `********`, or a value cut off with `…` after its first few characters, counts as masked.
3. Take the severity from the table first, then lower it one step if `exposure` is `internal`. It never goes below Low.
4. Count the finding from question 3 with its corrected severity.

### Clean up

```bash
docker compose down -v
```
