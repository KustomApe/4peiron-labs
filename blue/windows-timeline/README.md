# Windows のイベントログで時系列を作る

## シナリオ

あなたは株式会社サンプルの SOC 担当です。
ドメイン `CORP` に参加しているファイルサーバー `FS01` で、夜間に Security ログが消去されたというアラートが上がりました。

ログはイベント転送（WEF）で収集サーバーにほぼリアルタイムで集めていたため、消去より前のイベントも残っています。
2026-09-21〜09-25 の Security ログと System ログを、1 行 1 イベントの JSON（JSON Lines）に書き出して預かりました。
フィールド名は Windows のイベントと同じです（`EventData.LogonType`、`EventData.CommandLine` など）。

時刻（`TimeCreated`）は UTC です。管理者 `adm-tanaka` は踏み台 `JUMP01`（`10.10.0.5`）から RDP で作業します。
変更票のある作業は正規のものです。夜間の不審なログオンから始まる一連の操作を追ってください。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `security.jsonl` | Security ログ（4624, 4625, 4634, 4672, 4688, 4720, 4722, 4732, 1102 など） |
| `system.jsonl` | System ログ（7045, 7036, 104 など） |

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 攻撃者が作ったアカウント名は？ | `new-account` | 10 | ログのとおり。`4P{account_name}` の形 |
| 2. そのアカウントが追加されたローカルグループ名は？ | `added-group` | 20 | ログの `TargetUserName` のとおり（大文字小文字も同じ）。`4P{Group Name}` の形 |
| 3. 攻撃者がインストールしたサービスの名前は？ | `service-name` | 20 | 7045 の `ServiceName` のとおり。`4P{ServiceName}` の形 |
| 4. Security ログが消去された時刻は？ | `log-cleared` | 30 | UTC、秒まで、小数は切り捨て。`4P{2026-01-02T03:04:05}` の形 |

## ヒント

1. `EventID` 4625 を `EventData.IpAddress` ごとに数え、同じ送信元からの 4624（`LogonType` が `"10"`）を探します。値は文字列なので `jq 'select(.EventData.LogonType=="10")'` のように比べます。
2. 4624 の `TargetLogonId` は、その後の操作の `SubjectLogonId` と一致します。UAC があると 1 回の RDP で 2 つのログオン ID ができ、`TargetLinkedLogonId` で結ばれています。
3. 7045 にはログオン ID がありません。時刻と、4688 の `CommandLine`（`sc.exe` など）で突き合わせます。定義更新のたびに入る一時ドライバーは関係ありません。
4. 消去されたのが Security ログか System ログかを区別します。Security ログの消去は 1102、System ログの消去は 104 です。

## 片付け

```bash
docker compose down -v
```

## English

# Building a timeline from Windows event logs

### Scenario

You are a SOC analyst at Sample Corp. An alert fired overnight: the Security log was cleared on `FS01`, a file
server joined to the `CORP` domain.

Logs were forwarded in near real time to a collector (WEF), so events from before the clearing survive.
You were handed the Security and System logs for 2026-09-21 to 09-25 exported as JSON Lines, one event per line.
Field names match Windows events (`EventData.LogonType`, `EventData.CommandLine`, and so on).

`TimeCreated` is UTC. The administrator `adm-tanaka` works over RDP from the jump host `JUMP01` (`10.10.0.5`).
Work done under a change ticket is legitimate. Follow the chain of actions that starts with a suspicious logon at night.

### Evidence

| File | Contents |
|---|---|
| `security.jsonl` | Security log (4624, 4625, 4634, 4672, 4688, 4720, 4722, 4732, 1102, ...) |
| `system.jsonl` | System log (7045, 7036, 104, ...) |

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which account did the attacker create? | `new-account` | 10 | As in the log: `4P{account_name}` |
| 2. Which local group was that account added to? | `added-group` | 20 | Exactly as `TargetUserName` (same case): `4P{Group Name}` |
| 3. What is the name of the service the attacker installed? | `service-name` | 20 | Exactly as `ServiceName` in 7045: `4P{ServiceName}` |
| 4. When was the Security log cleared? | `log-cleared` | 30 | UTC to the second, fraction dropped: `4P{2026-01-02T03:04:05}` |

### Hints

1. Count event 4625 by `EventData.IpAddress`, then look for 4624 with `LogonType` `"10"` from the same source. Values are strings, so compare like `jq 'select(.EventData.LogonType=="10")'`.
2. The `TargetLogonId` of a 4624 matches the `SubjectLogonId` of later actions. With UAC, one RDP logon creates two logon IDs linked by `TargetLinkedLogonId`.
3. Event 7045 has no logon ID. Match it by time and by the `CommandLine` of a 4688 (such as `sc.exe`). The temporary drivers installed by definition updates are unrelated.
4. Tell apart clearing the Security log from clearing the System log: 1102 is the Security log, 104 is the System log.

### Clean up

```bash
docker compose down -v
```
