# サーバーの棚卸し

## シナリオ

あなたは株式会社サンプルの情報システム部に入ったばかりの担当者です。社内の会員ポータルを動かしている
Linux サーバー `portal-01` の管理を、前任者から引き継ぐことになりました。

引き継ぎの前に「おかしな設定が残っていないか棚卸しをしてほしい」と頼まれ、サーバーの設定ファイルと
ファイル一覧のコピーを受け取りました。サーバーそのものには触れません。受け取ったテキストファイルだけを
`grep` や `awk` で読んで、危ない設定を見つけてください。

## 証拠ファイル

コンテナの中では `/evidence` にあります。サーバーと同じディレクトリ構成で置いてあります。

| ファイル | 内容 |
|---|---|
| `etc/passwd` | アカウントの一覧（`名前:x:UID:GID:説明:ホーム:シェル`） |
| `etc/group` | グループの一覧（`名前:x:GID:メンバー`） |
| `etc/shells` | ログインに使えるシェルの一覧 |
| `etc/sudoers`, `etc/sudoers.d/*` | `sudo` で誰が何をできるかの設定 |
| `etc/crontab`, `etc/cron.d/*` | システムの定期実行の設定（6 列目が実行ユーザー） |
| `var/spool/cron/crontabs/*` | ユーザーごとの定期実行の設定（ファイル名のユーザーとして動く） |
| `etc/systemd/system/*.service` | 自作のサービスの設定 |
| `filelist.txt` | `find / -xdev -printf '%M %u %g %s %TY-%Tm-%Td %TH:%TM %p\n'` の出力。列は「権限 所有者 グループ サイズ 日付 時刻 パス」。シンボリックリンクにはリンク先を ` -> ` の後ろに付けてあります |

## 設問

| # | フラグ名 | 点 | 問い | 答えの形 |
|---|---|---|---|---|
| 1 | `uid-zero` | 10 | `root` のほかに UID が 0 のアカウントがあります。そのアカウント名は？ | `4P{<アカウント名>}` 例: `4P{hanako}` |
| 2 | `login-shell` | 10 | UID が 1〜999 のシステムアカウントのうち、`etc/shells` に載っているシェル（ログインできるシェル）を持つものが 1 つあります。そのアカウント名は？ | `4P{<アカウント名>}` 例: `4P{hanako}` |
| 3 | `writable-cron` | 20 | cron で **root として** 定期実行されているスクリプトのうち、所有者でもグループでもない「その他（other）」のユーザーまで書き換えられるものが 1 つあります。その絶対パスは？（コメントアウトされた行は動きません） | `4P{<絶対パス>}` 例: `4P{/usr/local/bin/example.sh}` |
| 4 | `nopasswd-all` | 30 | UID が 1000 以上のユーザーのうち、パスワードを入力せずに、どんなコマンドでも root として実行できるユーザーが 1 人います。そのユーザー名は？ | `4P{<ユーザー名>}` 例: `4P{hanako}` |

答えはすべて小文字で、ファイルに書かれているとおりに入力します。

## ヒント

1. `etc/passwd` は `:` で区切られた表です。`awk -F: '{print $1, $7}' etc/passwd` のように書くと、1 列目（名前）と 7 列目（シェル）だけを表示できます。UID は 3 列目です。`awk` では `$3 == 1234` のように条件を書くと、その条件に合う行だけが表示されます。`grep ':0:'` だと GID などにも当たってしまうので注意しましょう。
2. まず `cat etc/shells` でログインできるシェルを確かめます。`/usr/sbin/nologin` や `/bin/false` はログインさせないためのシェルです。`awk -F: '$3 >= 1 && $3 <= 999 {print $1, $7}' etc/passwd` で、システムアカウントとそのシェルを並べてみましょう。
3. まず root で動くジョブを集めます。`etc/crontab` と `etc/cron.d/*` は 6 列目がユーザー名、`var/spool/cron/crontabs/root` は root のジョブです。次に、そのスクリプトの権限を `grep '<パス>' filelist.txt` で確かめます。権限の文字列 `-rwxr-xr-x` は「種類・所有者 3 文字・グループ 3 文字・その他 3 文字」で、その他の 2 文字目（全体の 9 文字目）が `w` なら誰でも書き換えられます。先頭が `l` のシンボリックリンクはいつも `rwxrwxrwx` と表示されるので、対象から外します。
4. `grep -r NOPASSWD etc/sudoers etc/sudoers.d/` で候補を探します。行の最後が `ALL` かどうか（決まったコマンドだけか、何でもか）を見ます。`%` で始まる名前はユーザーではなくグループなので、`etc/group` でそのグループのメンバーを調べましょう。`#` で始まる行は無効です。

## 片付け

```bash
docker compose down -v
```

## English

# Server Inventory

## Scenario

You have just joined the IT department of Sample Corp. You are taking over `portal-01`, the Linux server
that runs the company's customer portal, from the previous administrator.

Before the handover you are asked to audit the server for dangerous leftovers. You receive copies of its
configuration files and a file listing. You never touch the server itself: read the text files with
`grep` and `awk` and find the risky settings.

## Evidence

Inside the container the files are under `/evidence`, laid out like the server's own directories.

| File | What it is |
|---|---|
| `etc/passwd` | Accounts (`name:x:UID:GID:comment:home:shell`) |
| `etc/group` | Groups (`name:x:GID:members`) |
| `etc/shells` | Shells that may be used to log in |
| `etc/sudoers`, `etc/sudoers.d/*` | Who may run what with `sudo` |
| `etc/crontab`, `etc/cron.d/*` | System scheduled jobs (column 6 is the user that runs the job) |
| `var/spool/cron/crontabs/*` | Per-user scheduled jobs (run as the user named by the file) |
| `etc/systemd/system/*.service` | Custom service units |
| `filelist.txt` | Output of `find / -xdev -printf '%M %u %g %s %TY-%Tm-%Td %TH:%TM %p\n'`. Columns: mode, owner, group, size, date, time, path. Symbolic links have their target appended after ` -> ` |

## Questions

| # | Flag name | Points | Question | Answer format |
|---|---|---|---|---|
| 1 | `uid-zero` | 10 | Besides `root`, one account has UID 0. What is its name? | `4P{<account>}` e.g. `4P{hanako}` |
| 2 | `login-shell` | 10 | One system account (UID 1–999) has a shell listed in `etc/shells`, so it can log in. What is its name? | `4P{<account>}` e.g. `4P{hanako}` |
| 3 | `writable-cron` | 20 | One script that cron runs **as root** can be modified by "other" users (neither the owner nor the group). What is its absolute path? (Commented-out lines do not run.) | `4P{<absolute path>}` e.g. `4P{/usr/local/bin/example.sh}` |
| 4 | `nopasswd-all` | 30 | One user with UID 1000 or higher can run any command as root without typing a password. Who? | `4P{<user>}` e.g. `4P{hanako}` |

Enter every answer in lowercase, exactly as written in the files.

## Hints

1. `etc/passwd` is a table separated by `:`. `awk -F: '{print $1, $7}' etc/passwd` prints only column 1 (name) and column 7 (shell). The UID is column 3. In `awk`, a condition such as `$3 == 1234` prints only the lines that match. `grep ':0:'` also matches GIDs and other columns, so be careful.
2. Start with `cat etc/shells` to see which shells allow logging in. `/usr/sbin/nologin` and `/bin/false` exist to prevent logins. Try `awk -F: '$3 >= 1 && $3 <= 999 {print $1, $7}' etc/passwd` to list system accounts and their shells.
3. First collect the jobs that run as root: in `etc/crontab` and `etc/cron.d/*` the user is column 6, and `var/spool/cron/crontabs/root` holds root's own jobs. Then check each script's mode with `grep '<path>' filelist.txt`. A mode such as `-rwxr-xr-x` reads "type, owner (3), group (3), other (3)"; if the second "other" character (the 9th character overall) is `w`, anyone can modify the file. Symbolic links (first character `l`) always show `rwxrwxrwx`, so leave them out.
4. Look for candidates with `grep -r NOPASSWD etc/sudoers etc/sudoers.d/`. Check whether the rule ends in `ALL` (any command) or names specific commands. A name starting with `%` is a group, not a user, so look up its members in `etc/group`. Lines starting with `#` are disabled.

## Clean up

```bash
docker compose down -v
```
