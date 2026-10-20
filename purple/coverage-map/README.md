# 検知のカバレッジを測る

## シナリオ

あなたは株式会社サンプルのパープルチームで、検証のまとめ役をしています。
2026-10-14 に、レッドと検知カバレッジのエミュレーションを行いました。計画した手順は `S01`〜`S10` で、それぞれ ATT&CK の技術に対応します。
レッドはコマンドの末尾に `# px:S01` のような目印を付け、テレメトリはコマンドラインや対象をそのまま記録しています。

検証が終わったいま、やることは「どの手順が検知できて、どこに穴があったか」を証拠から突き合わせることです。
**「検知できなかった」には 2 つの意味がある**ことに注意します。ひとつは**テレメトリは届いたのにルールが鳴らなかった**（ルールの穴）、もうひとつは**そもそもテレメトリが届かなかった**（可視性の穴）です。この 2 つは直し方がまったく違うので、分けて数えます。

### 突き合わせの決まり

- 実行したかどうかは `red_log.jsonl` の `status` で決める。`done` の手順だけを数え、`skipped` は判定しない。
- ある手順の**テレメトリが届いた**とは、その手順の目印（`marker`）が `events.jsonl` のどれかの行のどこかに現れること。
- ある手順が**検知された**とは、その手順の目印を持つ行が `alerts.jsonl` にあること。
- 目印の付かないアラート（例: インターネットからの良性なスキャン）は、どの手順にも結びつけない。
- `rules.json` の各ルールには、カバーするつもりの `techniques` と、当てている `hosts` が書いてある。

時刻はすべて UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `plan.csv` | エミュレーション計画。手順 `S01`〜`S10`・ATT&CK 技術・対象ホスト・期待したテレメトリ |
| `red_log.jsonl` | レッドの実行記録。`status`（`done` / `skipped`）・`host`・`started`・`marker` |
| `events.jsonl` | その日のテレメトリ。平常時の動きに、目印付きのレッドの手順が混ざっている |
| `alerts.jsonl` | 鳴ったアラート。手順由来のものは `marker` を持つ |
| `rules.json` | 検知ルール。`id`・`name`・カバーする `techniques`・当てている `hosts` |

調査用のコンテナには `python3` と `jq` が入っています。小さなスクリプトで突き合わせると確実です。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 実行され、テレメトリも届いたのに、どのルールも鳴らなかった手順は？ | `blind-step` | 10 | 手順の ID。`4P{S00}` の形 |
| 2. 2 つ以上のホストで実行されたのに、一部のホストでしか検知できなかった技術は？ | `partial-technique` | 15 | 技術 ID。`4P{T1000.000}` の形 |
| 3. もっとも多くの異なる手順にまたがって鳴ったルールは？（1 本で何でも拾う＝精度が低い） | `widest-rule` | 20 | ルール ID。`4P{R100}` の形 |
| 4. 実行した（`done`）手順のうち、1 つ以上のアラートが出たものはいくつ？ | `covered-count` | 25 | 件数。`4P{0}` の形 |

## ヒント

1. まず `done` の手順ごとに、目印が `events.jsonl` に出るか・`alerts.jsonl` に出るかの 2 つを別々に調べます。「テレメトリは出た（events にある）が、アラートは出なかった（alerts に無い）」手順が答えです。テレメトリも出ていない手順は、別の穴（可視性）なので混ぜないこと。
2. 技術ごとに、実行したホストの集合と、検知できたホストの集合を作ります。実行が 2 ホスト以上で、検知がその一部だけの技術を探します。同じ技術でも、ホストによって当てているルールが違うことがあります。
3. アラートを目印で手順に結びつけ、ルールごとに「結びついた手順の集合」を作ります。その集合がいちばん大きいルールが答えです。特定の技術に当てたルールは 1 手順にしか出ませんが、汎用的なルールは複数の手順で鳴ります。
4. 3 の数え方と同じく、手順を軸に「1 件でもアラートが出たか」を見ます。ルールの数ではなく、**手順の数**を数えます。

## 片付け

```bash
docker compose down -v
```

## English

# Measure your detection coverage

### Scenario

You coordinate exercises on Sample Corp's purple team. On 2026-10-14 you ran a detection-coverage emulation
with red. The planned steps are `S01` to `S10`, each mapped to an ATT&CK technique. Red ended every command
with a marker such as `# px:S01`, and the telemetry records the command line and target as is.

Now that the exercise is over, your job is to reconcile the evidence and ask "what did we detect, and where are
the gaps?" **"Not detected" means two different things.** Either the telemetry arrived but no rule fired (a rule
gap), or no telemetry arrived at all (a visibility gap). The two call for completely different fixes, so count
them apart.

#### Reconciliation rules

- Whether a step ran is decided by `status` in `red_log.jsonl`. Count only `done` steps; never judge a `skipped` one.
- A step's **telemetry arrived** if its marker appears anywhere in some line of `events.jsonl`.
- A step was **detected** if a line in `alerts.jsonl` carries its marker.
- Alerts with no marker (e.g. a benign scan from the internet) are tied to no step.
- Each rule in `rules.json` lists the `techniques` it means to cover and the `hosts` it runs on.

All times are UTC.

### Evidence

| File | Contents |
|---|---|
| `plan.csv` | The emulation plan: steps `S01`–`S10`, ATT&CK technique, target host, expected telemetry |
| `red_log.jsonl` | Red's execution log: `status` (`done` / `skipped`), `host`, `started`, `marker` |
| `events.jsonl` | The day's telemetry; marked red steps are mixed into normal activity |
| `alerts.jsonl` | The alerts that fired; step-related ones carry a `marker` |
| `rules.json` | Detection rules: `id`, `name`, covered `techniques`, deployed `hosts` |

The analyst container has `python3` and `jq`. A small reconciliation script is the safest way.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which step ran and sent telemetry, yet no rule fired? | `blind-step` | 10 | The step ID: `4P{S00}` |
| 2. Which technique ran on two or more hosts but was detected on only some of them? | `partial-technique` | 15 | The technique ID: `4P{T1000.000}` |
| 3. Which rule fired across the most distinct steps? (one rule catching everything = low fidelity) | `widest-rule` | 20 | The rule ID: `4P{R100}` |
| 4. Of the steps that ran (`done`), how many raised at least one alert? | `covered-count` | 25 | The count: `4P{0}` |

### Hints

1. For each `done` step, check two things separately: does the marker appear in `events.jsonl`, and in `alerts.jsonl`? The answer is the step with telemetry (in events) but no alert (not in alerts). A step with no telemetry at all is a different (visibility) gap — do not mix it in.
2. Per technique, build the set of hosts it ran on and the set of hosts where it was detected. Look for a technique that ran on two or more hosts but was detected on only some. The same technique can be covered by different rules on different hosts.
3. Tie alerts to steps by marker, and per rule build the set of steps it fired on. The rule with the largest set is the answer. A rule tuned to one technique fires on a single step, while an over-broad rule fires on several.
4. As in 3, work by step: did it raise at least one alert? Count the number of **steps**, not rules.

### Clean up

```bash
docker compose down -v
```
