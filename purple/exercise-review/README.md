# 演習の結果を突き合わせる

## シナリオ

あなたは株式会社サンプルの SOC（ブルー）の担当者です。2026-09-15 の深夜（UTC）に、
内部の検証担当（レッド）とパープル演習 `PX-2026-09` を行いました。舞台は本番から切り離したラボ
（`lab-lnx01`・`lab-web01`・`lab-win01`）で、レッドは作業用の端末 `lab-red01`（`10.20.0.50`）から手順を実行しました。

演習が終わり、レッドの実行記録と、SIEM に届いたイベントとアラートが手元にそろいました。
計画の手順ごとに「検知」「ログのみ（ログは届いたがアラートが無い）」「ログなし」を判定し、
演習の手順に結びつかないアラートが無いかも確かめてください。

- レッドは、手順ごとの目印（`marker`、例: `px:S03`）を、コマンドの引数・ファイル名・表示名・User-Agent のどこかに入れました。
  イベントやアラートに目印があれば、その手順のものです。
- SSH の手順（`S02`・`S03`）は目印を付けられません。送信元が `10.20.0.50` で、ルールが計画の `expected_rule` と同じものを、その手順のアラートとします。
- `lab-lnx01` では毎日 02:00 に、`svc-backup` が sudo で夜間バックアップを動かします。そのたびにアラート `R140` が鳴ることは、SOC で把握済みです。

時刻はすべて UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `plan.csv` | エミュレーション計画。手順・ATT&CK の技術 ID・対象ホスト・期待するテレメトリ・期待するルール |
| `red_log.jsonl` | レッドの実行記録。1 行 1 手順。`status`（`done` / `skipped`）・開始時刻 `started`・目印 `marker` |
| `events.jsonl` | 00:00〜04:00 に SIEM に届いたイベント。ふだんの動きも混ざっている |
| `alerts.jsonl` | 同じ時間帯に SIEM が出したアラート |

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 実行され、イベントは SIEM に届いたのに、アラートが 1 つも出なかった手順は？ | `log-only-step` | 10 | 手順の ID。`4P{S01}` の形 |
| 2. 実行されたのに、イベントが SIEM に 1 件も届かなかった手順は？ | `no-log-step` | 10 | 手順の ID。`4P{S01}` の形 |
| 3. 検知できた手順のうち、いちばん遅かったものは、実行からアラートまで何秒かかった？ | `slowest-seconds` | 20 | `started` から、その手順の最初のアラートまでの秒数。`4P{120}` の形 |
| 4. どの手順にも結びつかず、把握済みのものでもないアラートの送信元 IP アドレスは？ | `unplanned-source` | 30 | `4P{192.0.2.1}` の形 |

## ヒント

1. まず `red_log.jsonl` から、実行した手順（`status` が `done`）と目印を出します。目印ごとに `grep -c` で `events.jsonl` と `alerts.jsonl` を数えると、表が作れます。
2. 実行しなかった手順は、ログが無くて当然です。「見逃し」と数えないように、`status` を先に確かめます。
3. 遅延は手順ごとに「最初のアラートの時刻 − `started`」です。同じ手順でアラートが何度も鳴っても、使うのは最初の 1 つです。
4. 目印も無く、送信元が `10.20.0.50` でもないアラートを探します。レッドのものだと決めつけて閉じていたら、演習の陰で本物を見逃していたことになります。

## 片付け

```bash
docker compose down -v
```

## English

# Reconciling exercise results

### Scenario

You work in Sample Corp's SOC (blue). Late on 2026-09-15 (UTC) you ran purple exercise `PX-2026-09` with the
internal testers (red). It took place in a lab cut off from production (`lab-lnx01`, `lab-web01`, `lab-win01`),
and red ran every step from its workstation `lab-red01` (`10.20.0.50`).

The exercise is over, and you now have red's execution log plus the events and alerts that reached the SIEM.
Classify every planned step as detected, log only (events arrived but no alert) or no log, and check for alerts
that do not belong to any step.

- Red put a per-step marker (`marker`, for example `px:S03`) into a command argument, file name, display name or
  User-Agent. An event or alert that contains the marker belongs to that step.
- The SSH steps (`S02`, `S03`) cannot carry a marker. Alerts from `10.20.0.50` whose rule matches the step's
  `expected_rule` in the plan belong to that step.
- Every day at 02:00, `svc-backup` runs the nightly backup with sudo on `lab-lnx01`, and alert `R140` fires each
  time. The SOC already knows about it.

All times are UTC.

### Evidence

| File | Contents |
|---|---|
| `plan.csv` | The emulation plan: step, ATT&CK technique ID, target host, expected telemetry and expected rule |
| `red_log.jsonl` | Red's execution log, one step per line: `status` (`done` / `skipped`), start time `started` and `marker` |
| `events.jsonl` | Events that reached the SIEM between 00:00 and 04:00, mixed with normal activity |
| `alerts.jsonl` | Alerts the SIEM raised in the same period |

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which step was run and reached the SIEM as events, but raised no alert at all? | `log-only-step` | 10 | The step ID: `4P{S01}` |
| 2. Which step was run, but not a single event reached the SIEM? | `no-log-step` | 10 | The step ID: `4P{S01}` |
| 3. Of the detected steps, how many seconds did the slowest take from execution to alert? | `slowest-seconds` | 20 | Seconds from `started` to that step's first alert: `4P{120}` |
| 4. What is the source IP address of the alert that belongs to no step and is not a known one? | `unplanned-source` | 30 | `4P{192.0.2.1}` |

### Hints

1. Start from `red_log.jsonl`: list the steps that ran (`status` is `done`) and their markers. Count each marker in `events.jsonl` and `alerts.jsonl` with `grep -c` and you have your table.
2. A step that was never run has no log for good reason. Check `status` first so you do not count it as a miss.
3. The delay per step is "time of the first alert − `started`". If a step raised several alerts, use only the first.
4. Look for an alert with no marker whose source is not `10.20.0.50`. Closing it as "just red" would have meant missing a real attack hidden behind the exercise.

### Clean up

```bash
docker compose down -v
```
