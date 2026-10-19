# 権限の棚卸し

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームの一員です。今回は、社内の Linux サーバー
`app01.example.co.jp` の**設定レビュー**を任されました。サーバーにはログインせず、情報システム部の担当者が
収集スクリプトで書き出した設定とファイルの一覧だけを読みます。

見たいのは、「だれが・何に・どこまでできるか」が、会社の決めたロール表と合っているかです。
報告書に載せる指摘を拾ってください。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `passwd`・`group` | アカウントとグループ（`/etc/passwd`・`/etc/group` の写し） |
| `sudoers` | `/etc/sudoers` と `/etc/sudoers.d/*` をまとめたもの |
| `crontab` | `/etc/crontab` と `/etc/cron.d/*` をまとめたもの。6 列目が、そのジョブを動かすユーザー |
| `files.jsonl` | 主なファイルとディレクトリの一覧。`mode` は 8 進数の 4 桁（例: `0644`、`4755`） |
| `suid_baseline.txt` | 同じ版のディストリビューションを新しく入れたときに、SUID / SGID が付いているファイル |
| `secrets_inventory.csv` | 秘密の値（パスワード・鍵・トークン）を含むと分かっているファイル |
| `role_matrix.csv` | 会社のロール表。`full_admin_allowed` が `yes` の人だけが、すべてのコマンドを root で動かしてよい |

調査用のコンテナには `python3` と `jq` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. root が cron で定期的に動かすファイルのうち、だれでも書き換えられるものは？ | `writable-root-job` | 10 | フルパス。`4P{/path/to/file}` の形 |
| 2. SUID か SGID が付いているのに、ベースラインに無いファイルは？ | `unexpected-suid` | 10 | フルパス。`4P{/path/to/file}` の形 |
| 3. ロール表では許されていないのに、すべてのコマンドを root で動かせる（`sudo`）アカウントは？ | `excess-admin` | 20 | アカウント名。`4P{name}` の形 |
| 4. 秘密の値を含むファイルのうち、所有者でもグループでもない「その他」の人が読めるものは何個？ | `readable-secrets` | 30 | 個数。`4P{10}` の形 |

## ヒント

1. `crontab` で 6 列目が `root` の行に出てくるファイルを、`files.jsonl` で引きます。`mode` の最後の桁が「その他」で、`2` のビット（書き込み）が立っているかを見ます。だれでも書けても、動かすのが root でなければこの設問の答えではありません。
2. `mode` が 4 桁のとき、先頭の桁が特殊なビットです。`4` が SUID、`2` が SGID、`1` がスティッキービット。ディレクトリの `1777` は、この設問とは別のものです。
3. `sudoers` の `%` で始まる行はグループへの許可です。グループの人は `group` で引きます。決まったコマンドだけを許す行は「すべてのコマンド」ではありません。
4. 「その他」の桁で `4` のビット（読み取り）が立っているかを見ます。`6` や `4` だけでなく、`5` や `7` でも読めます。

## 片付け

```bash
docker compose down -v
```

## English

# Reviewing who can do what

### Scenario

You are on a security assessment team under contract with Sample Corp. This time you have a **configuration review**
of the internal Linux server `app01.example.co.jp`. You do not log in to it. You read only the settings and the
file listing that the IT department exported with a collection script.

The question is whether "who can do what, and how far" matches the company's role matrix. Pick out findings for the report.

### Evidence

| File | Contents |
|---|---|
| `passwd`, `group` | Accounts and groups (copies of `/etc/passwd` and `/etc/group`) |
| `sudoers` | `/etc/sudoers` and `/etc/sudoers.d/*` combined |
| `crontab` | `/etc/crontab` and `/etc/cron.d/*` combined. Column 6 is the user the job runs as |
| `files.jsonl` | Key files and directories. `mode` is four octal digits (e.g. `0644`, `4755`) |
| `suid_baseline.txt` | Files that carry SUID / SGID on a fresh install of the same distribution release |
| `secrets_inventory.csv` | Files known to contain secrets (passwords, keys, tokens) |
| `role_matrix.csv` | The role matrix. Only people with `full_admin_allowed` = `yes` may run every command as root |

The analyst container has `python3` and `jq`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which file that root runs from cron can anyone modify? | `writable-root-job` | 10 | The full path: `4P{/path/to/file}` |
| 2. Which file carries SUID or SGID but is not in the baseline? | `unexpected-suid` | 10 | The full path: `4P{/path/to/file}` |
| 3. Which account can run every command as root through `sudo` although the role matrix does not allow it? | `excess-admin` | 20 | The account name: `4P{name}` |
| 4. How many of the files containing secrets can be read by "others" (neither the owner nor the group)? | `readable-secrets` | 30 | The count: `4P{10}` |

### Hints

1. Take the files on `crontab` lines whose column 6 is `root` and look them up in `files.jsonl`. The last digit of `mode` is "others"; check whether its `2` bit (write) is set. A world-writable file run by someone other than root is not the answer here.
2. With four digits, the first one holds the special bits: `4` is SUID, `2` is SGID, `1` is the sticky bit. A `1777` directory is a different matter.
3. Lines starting with `%` in `sudoers` grant a group; look up its members in `group`. A line that allows only specific commands is not "every command".
4. Check whether the `4` bit (read) is set in the "others" digit. Not only `4` and `6` but also `5` and `7` allow reading.

### Clean up

```bash
docker compose down -v
```
