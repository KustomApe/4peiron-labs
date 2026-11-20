# サーバーの棚卸し — 解説

フラグを取ったあとに読む解説です。サイトでは、そのフラグを取った人にだけ表示されます。
答えそのものは書いていません。自分で見つけたものと、ここに書いた筋道を照らしてください。

## `uid-zero`

【調べ方】`/etc/passwd` は `:` で区切られた表で、UID は 3 列目です。`awk -F: '$3 == 0 {print $1}' etc/passwd` で、UID が 0 のアカウントだけを出します。`grep ':0:'` は GID など別の列にも当たるので、列を指定して比べます。
【考え方】Linux の特権は名前ではなく UID で決まります。名前が `root` でなくても、UID が 0 なら root と同じ力を持ちます。
【検知と対策】UID が 0 のアカウントは `root` だけにします。`awk` の確認を定期的に流し、増えたら通知します。`/etc/passwd` の変更は、監査ログ（auditd など）で記録します。

## `login-shell`

【調べ方】`/etc/shells` に載っているシェルの一覧と、UID が 1〜999 のシステムアカウントのシェル（7 列目）を突き合わせます。
【考え方】システムアカウントは、サービスを動かすためのもので、人が入る必要はありません。ログインできるシェルが付いていると、そのアカウントへの総当たりや、鍵の置き場所を使った侵入の入口になります。
【検知と対策】システムアカウントのシェルは `/usr/sbin/nologin` か `/bin/false` にします。新しく作るときは `useradd --system --shell /usr/sbin/nologin` を使います。

## `writable-cron`

【調べ方】root の cron（`/etc/crontab`・`/etc/cron.d/`・ユーザーごとの crontab）から、実行されるスクリプトのパスを集めます。コメントアウトされた行は動かないので除きます。そのパスの権限を `filelist.txt` で見て、「その他」に書き込み権限（`w`）が付いたものを探します。
【考え方】root が実行するファイルを、ほかのユーザーが書き換えられるなら、そのユーザーは root の力を使えます。権限の弱いファイルが、そのまま権限昇格の経路になります。
【検知と対策】root で動くスクリプトは、所有者を root にして `chmod go-w` します。置き場所のディレクトリも、書き込める人を絞ります。ファイルの権限の変更や、`world-writable` なファイルを定期的に探して通知します（`find / -perm -0002 -type f`）。

## `nopasswd-all`

【調べ方】`/etc/sudoers` と `/etc/sudoers.d/` の中のファイルを読みます。`NOPASSWD: ALL` が付いた行のうち、UID が 1000 以上の人間のユーザーに当たるものを探します。グループ（`%グループ名`）に付いている場合は、`group` ファイルでそのメンバーを確かめます。
【考え方】パスワードなしで何でも root で実行できるなら、そのユーザーのアカウントが乗っ取られた時点で、サーバー全体が取られます。設定が移行用の一時的なものだったかどうかも、ファイル名やコメントから読み取ります。
【検知と対策】`NOPASSWD` は、必要なコマンドだけに絞ります（`ALL` にしない）。移行のために足した設定は、終わったら消します。`sudoers` の変更は `visudo -c` で確かめ、監査ログに残します。

## English

# Server inventory audit — write-up

Read this after you capture a flag. The site shows it only to people who captured that flag.
It does not contain the answers. Compare what you found with the reasoning here.

### `uid-zero`

[How to investigate] `/etc/passwd` is a `:`-separated table and the UID is column 3. `awk -F: '$3 == 0 {print $1}' etc/passwd` prints only accounts with UID 0. `grep ':0:'` also matches other columns such as the GID, so compare a specific column.
[Reasoning] Linux privilege depends on the UID, not the name. An account with UID 0 has root's power even if it is not named `root`.
[Detection and defense] Keep `root` as the only UID 0 account. Run the `awk` check on a schedule and alert when the list grows. Record changes to `/etc/passwd` in an audit log (such as auditd).

### `login-shell`

[How to investigate] Compare the shells listed in `/etc/shells` with the shell (column 7) of the system accounts with UID 1 to 999.
[Reasoning] System accounts exist to run services and nobody needs to log in as them. If one has a usable shell, it becomes an entry point for brute force or for a planted key.
[Detection and defense] Give system accounts `/usr/sbin/nologin` or `/bin/false` as the shell. When you create one, use `useradd --system --shell /usr/sbin/nologin`.

### `writable-cron`

[How to investigate] Collect the script paths that root's cron runs (`/etc/crontab`, `/etc/cron.d/`, per-user crontabs). Skip commented-out lines, which do not run. Check those paths' permissions in `filelist.txt` and look for ones where "other" has write permission (`w`).
[Reasoning] If another user can rewrite a file that root executes, that user can use root's power. A file with weak permissions becomes a privilege-escalation path as it is.
[Detection and defense] Make root-run scripts owned by root and apply `chmod go-w`. Restrict who can write to the directory they live in as well. Search for permission changes and world-writable files on a schedule and alert on them (`find / -perm -0002 -type f`).

### `nopasswd-all`

[How to investigate] Read `/etc/sudoers` and the files in `/etc/sudoers.d/`. Among lines with `NOPASSWD: ALL`, find the one that applies to a human user with UID 1000 or higher. If it is set on a group (`%groupname`), check its members in the `group` file. Also read from the file name and comments whether the setting was meant to be temporary, for a migration.
[Reasoning] If a user can run anything as root without a password, taking over that account takes over the whole server.
[Detection and defense] Limit `NOPASSWD` to the commands that are needed (not `ALL`). Remove settings added for a migration once it is done. Check `sudoers` changes with `visudo -c` and record them in an audit log.
