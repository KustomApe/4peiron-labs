# 誤検知を切り分ける

## シナリオ

あなたは株式会社サンプルの SOC（ブルー）で、検知アラートの一次トリアージを担当しています。
2026-10-16 はパープルの検証日で、レッドが手順 `E01`〜`E05` を実行しました。ところがこの日は、検証とは関係のないアラートもいつもより多く、キューが溢れました。

やることは、その日のアラートを 3 つに仕分けることです。

- **演習由来（真の検知）**… レッドの手順に結びつくもの。目印 `px:E01` などが付いている。
- **環境ノイズ**… ふだんの動きや、インターネットからの無差別な通信。
- **設定ミス（既知の良性ツール）**… 脆弱性スキャナや監視エージェントなど、インベントリに載っている正規のツールが、ルールに引っかかっているもの。

仕分けができたら、**演習の検知を一切隠さずに、どのルールを安全に抑制できるか**まで決めます。

### 仕分けの決まり

- レッドの手順は `red_log.jsonl` にあり、それぞれ `marker`（`px:E01` など）を持つ。
- アラートに `marker` が付き、その値がレッドの手順の目印と一致すれば、**演習由来**。
- `marker` の無いアラートは、演習には結びつかない（＝偽陽性の候補）。
- `inventory.json` の `sources` は、IP・役割・持ち主がわかっている**良性**の発生源。`service_accounts` は良性のサービスアカウント。

時刻はすべて UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `alerts.jsonl` | その日に鳴ったアラート。`rule_id`・`host`・`src_ip`・（演習由来なら）`marker` |
| `red_log.jsonl` | レッドの手順 `E01`〜`E05`。`marker`・`source`・`host` |
| `rules.json` | 検知ルール。`id`・`name`・`technique` |
| `inventory.json` | 既知の良性の発生源（スキャナ・監視・CI）とサービスアカウント |

調査用のコンテナには `python3` と `jq` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. その日のアラートのうち、演習の手順に結びつくもの（真の検知）は何件？ | `exercise-alerts` | 10 | 件数。`4P{0}` の形 |
| 2. 演習に結びつかないアラート（偽陽性）が、いちばん多かったルールは？ | `top-fp-rule` | 20 | ルール ID。`4P{R100}` の形 |
| 3. インベントリに載っている良性の発生源のうち、偽陽性をいちばん多く出したのはどれ？（アローリスト入りの最優先） | `allowlist-source` | 20 | IP アドレス。`4P{10.0.0.1}` の形 |
| 4. 演習の検知に一度も使われておらず、良性の発生源からしか鳴っていない（＝丸ごと抑制しても演習を隠さない）ルールは？ | `suppress-safe` | 30 | ルール ID。`4P{R100}` の形 |

## ヒント

1. レッドの手順の目印を集め、その目印を持つアラートを数えます。残りが偽陽性の候補です。
2. 目印の無いアラートだけを、ルール別に数えます。いちばん多いルールが答えです。演習由来の分は数えないこと。
3. 目印の無いアラートの発生源を数えますが、**`inventory.json` に載っている IP に限って**比べます。いちばん件数の多い良性の発生源が、まず止めるべき相手です。
4. ルールごとに「演習由来のアラートがあるか」「アラートの発生源がすべて良性か」を見ます。演習で一度でも鳴ったルールを止めると検知が消えるので外します。残るのは、良性の発生源からしか鳴っていないルールです。

## 片付け

```bash
docker compose down -v
```

## English

# Triage the false positives

### Scenario

You run first-line alert triage in Sample Corp's SOC (blue). 2026-10-16 was a purple test day, and red ran
steps `E01` to `E05`. But that day also brought more unrelated alerts than usual, and the queue overflowed.

Your job is to sort the day's alerts into three buckets.

- **Exercise (true positives)** — tied to a red step; they carry a marker such as `px:E01`.
- **Environmental noise** — normal activity, or indiscriminate traffic from the internet.
- **Misconfiguration (known-good tools)** — a legitimate tool listed in the inventory, such as a vulnerability
  scanner or a monitoring agent, tripping a rule.

Once sorted, decide **which rule you can safely suppress without hiding any exercise detection**.

#### Sorting rules

- Red's steps are in `red_log.jsonl`, each with a `marker` (such as `px:E01`).
- If an alert has a `marker` equal to a red step's marker, it is an **exercise** alert.
- An alert with no `marker` is tied to no step (a false-positive candidate).
- `inventory.json`'s `sources` are **known-good** origins with a known IP, role and owner. `service_accounts`
  are known-good service accounts.

All times are UTC.

### Evidence

| File | Contents |
|---|---|
| `alerts.jsonl` | The alerts that fired that day: `rule_id`, `host`, `src_ip`, and (for exercise ones) a `marker` |
| `red_log.jsonl` | Red's steps `E01`–`E05`: `marker`, `source`, `host` |
| `rules.json` | Detection rules: `id`, `name`, `technique` |
| `inventory.json` | Known-good sources (scanner, monitoring, CI) and service accounts |

The analyst container has `python3` and `jq`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Of the day's alerts, how many are tied to an exercise step (true positives)? | `exercise-alerts` | 10 | The count: `4P{0}` |
| 2. Which rule produced the most alerts that are not tied to the exercise (false positives)? | `top-fp-rule` | 20 | The rule ID: `4P{R100}` |
| 3. Among the known-good sources in the inventory, which raised the most false positives? (top allowlist candidate) | `allowlist-source` | 20 | The IP address: `4P{10.0.0.1}` |
| 4. Which rule was never used for an exercise detection and fired only from known-good sources (so suppressing it whole hides no exercise)? | `suppress-safe` | 30 | The rule ID: `4P{R100}` |

### Hints

1. Collect red's step markers and count the alerts carrying one. What is left are the false-positive candidates.
2. Count only the alerts with no marker, grouped by rule. The rule with the most is the answer. Do not count the exercise alerts.
3. Count the sources of the marker-less alerts, but compare **only the IPs listed in `inventory.json`**. The known-good source with the most is the one to allowlist first.
4. For each rule, check whether it has any exercise alert and whether all of its alert sources are known-good. Drop any rule that fired for the exercise even once (suppressing it would lose detection). What remains is a rule that fired only from known-good sources.

### Clean up

```bash
docker compose down -v
```
