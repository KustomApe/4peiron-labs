# SSH への総当たりを追う

## シナリオ

あなたは株式会社サンプルの情報システム部の担当者です。
公開 Web サーバー `web01`（Ubuntu 24.04）について、委託先から「見覚えのないユーザーがいる」と連絡がありました。

サーバーの `/var/log/auth.log` を 1 週間分（2026-09-07〜09-13）預かりました。
社内の管理者は `10.0.x.x` から鍵でログインします。委託先の保守担当は `192.0.2.40` から `webadmin` にパスワードでログインします。
それ以外の動きを探し、何が起きたかを確かめてください。

サーバーの時計は UTC です。ログの時刻もそのまま UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `auth.log.1` | 2026-09-07 から 09-13 06:25 ごろまでの認証ログ（ローテーション済み） |
| `auth.log` | それ以降、09-13 の終わりまでの認証ログ |

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 何度もパスワードを試したあと、最後にログインに成功した送信元 IP アドレスは？ | `attacker-ip` | 10 | `4P{192.0.2.1}` の形 |
| 2. その IP が入ったアカウント名は？ | `compromised-user` | 10 | `4P{username}` の形（ログのとおり小文字） |
| 3. その IP が初めてログインに成功した時刻は？ | `first-login` | 20 | UTC、秒まで、小数は切り捨て。`4P{2026-01-02T03:04:05}` の形 |
| 4. そのセッションの中で新しく作られたユーザー名は？ | `new-user` | 20 | `4P{username}` の形 |

## ヒント

1. `Failed password` の行を送信元ごとに数え、`Accepted` の行と見比べます。`grep` と `awk`、`sort | uniq -c` が使えます。
2. `Accepted password for <ユーザー> from <IP>` の形を読みます。
3. 2 つのファイルにまたがります。同じ IP の `Accepted` が複数あれば、いちばん早いものです。
4. ログイン後の `sudo:` の行と、`useradd` が出した行を時刻順に読みます。正規の管理者が作ったユーザーと取り違えないようにします。

## 片付け

```bash
docker compose down -v
```

## English

# Tracing an SSH brute-force attack

### Scenario

You work in the IT department of Sample Corp. A contractor reports an unfamiliar user on the public web
server `web01` (Ubuntu 24.04).

You were handed one week of `/var/log/auth.log` (2026-09-07 to 09-13). In-house admins log in with keys from
`10.0.x.x`. The contractor's maintenance staff log in to `webadmin` with a password from `192.0.2.40`.
Find the activity that does not fit and work out what happened.

The server clock is UTC, so the log timestamps are UTC.

### Evidence

| File | Contents |
|---|---|
| `auth.log.1` | Authentication log from 2026-09-07 to about 09-13 06:25 (rotated) |
| `auth.log` | Authentication log from then to the end of 09-13 |

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which source IP address tried many passwords and finally logged in? | `attacker-ip` | 10 | `4P{192.0.2.1}` |
| 2. Which account did that IP log in to? | `compromised-user` | 10 | `4P{username}` (lowercase, as in the log) |
| 3. When did that IP first log in successfully? | `first-login` | 20 | UTC to the second, fraction dropped: `4P{2026-01-02T03:04:05}` |
| 4. Which new user was created during that session? | `new-user` | 20 | `4P{username}` |

### Hints

1. Count `Failed password` lines per source and compare them with the `Accepted` lines. `grep`, `awk` and `sort | uniq -c` help.
2. Read lines of the form `Accepted password for <user> from <IP>`.
3. The activity spans both files. If the IP has several `Accepted` lines, take the earliest.
4. Read the `sudo:` and `useradd` lines after the login in time order. Do not confuse it with a user an admin created legitimately.

### Clean up

```bash
docker compose down -v
```
