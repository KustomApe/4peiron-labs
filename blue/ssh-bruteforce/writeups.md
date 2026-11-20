# SSH への総当たりを追う — 解説

フラグを取ったあとに読む解説です。サイトでは、そのフラグを取った人にだけ表示されます。
答えそのものは書いていません。ログから自分で見つけたものと、ここに書いた筋道を照らしてください。

## `attacker-ip`

【調べ方】`Failed password` の行を送信元 IP ごとに数えます（`grep` → `awk` → `sort | uniq -c`）。失敗が突出して多い送信元を、`Accepted` の行と突き合わせます。失敗を重ねたあとで成功に変わった送信元が、疑う相手です。
【考え方】総当たりは「失敗の山のあとに成功が 1 回混じる」形で現れます。保守担当のように、いつも決まった IP から入る正規の利用とは、失敗の数と、成功までの流れで見分けます。
【検知と対策】同じ送信元からの失敗が短時間に積み上がったら通知する（fail2ban などで一時的に遮断する）。パスワードでのログインをやめて鍵だけにし、`PermitRootLogin no` と `AllowUsers` で入れる人を絞ります。

## `compromised-user`

【調べ方】`Accepted password for <ユーザー> from <IP>` の形から、疑わしい IP が入ったアカウントを読み取ります。
【考え方】総当たりは、弱いパスワードの付いた、使われていない・保守用のアカウントに当たりやすいものです。入られたアカウントが何のためのものだったかを、あわせて確かめます。
【検知と対策】共有や保守用のアカウントは、使う期間だけ有効にし、鍵とパスワードの強さを決めておきます。普段使わないアカウントへの成功ログインを、通知の対象にします。

## `first-login`

【調べ方】疑わしい IP の `Accepted` を、ローテーションされた 2 つのログにまたがって集め、いちばん早い時刻を取ります。サーバーの時計が UTC なことも確かめます。
【考え方】侵入の「いつから」が決まると、そこから後の操作（作られたユーザー、実行されたコマンド）を、被害の範囲として洗い出せます。ログが分かれていても、時刻順に 1 本の流れとして読みます。
【検知と対策】ログは長く保存し、別のサーバーにも送ります（入られたあとに消されても残るように）。時刻は NTP でそろえ、時刻の基準を決めておきます。

## `new-user`

【調べ方】最初のログインの直後から、`sudo:` の行と `useradd` が出した行を時刻順に読みます。管理者が作ったユーザーと混ざらないよう、誰が・どの接続から作ったかを見ます。
【考え方】入った人は、あとからまた入れるように足がかりを作ります。新しいユーザーの追加は、その典型です。
【検知と対策】ユーザーの追加・`sudo` の利用・`authorized_keys` の変更を監査ログ（auditd など）に残して通知します。見つけたら、そのユーザーと、入られたアカウントの鍵・パスワードを無効にし、同じ時刻以降の変更を洗い出して元に戻します。

## English

# Tracing an SSH brute-force attack — write-up

Read this after you capture a flag. The site shows it only to people who captured that flag.
It does not contain the answers. Compare what you found in the logs with the reasoning here.

### `attacker-ip`

[How to investigate] Count `Failed password` lines per source IP (`grep`, then `awk`, then `sort | uniq -c`). Compare the sources with the most failures against the `Accepted` lines. A source whose failures turn into a success is the one to suspect.
[Reasoning] A brute-force attack looks like a pile of failures with a success mixed in. You tell it apart from legitimate use, such as the maintenance staff who always log in from one IP, by the number of failures and by what comes before the success.
[Detection and defense] Alert when failures from one source pile up in a short time (and block it temporarily, for example with fail2ban). Stop password logins and allow keys only, and narrow who can get in with `PermitRootLogin no` and `AllowUsers`.

### `compromised-user`

[How to investigate] Read the account name from the `Accepted password for <user> from <IP>` line of the suspect IP.
[Reasoning] Brute force tends to land on accounts that are unused or kept for maintenance and have weak passwords. Also check what the account was for.
[Detection and defense] Enable shared or maintenance accounts only while they are needed, and set rules for their keys and password strength. Alert on successful logins to accounts that are not normally used.

### `first-login`

[How to investigate] Collect the suspect IP's `Accepted` lines across both rotated logs and take the earliest. Confirm that the server clock is UTC.
[Reasoning] Once you know when the intrusion began, you can list everything after it (new users, commands run) as the scope of the damage. Even when the logs are split, read them as one timeline.
[Detection and defense] Keep logs for a long time and ship them to another server, so they survive even if the intruder deletes them. Sync clocks with NTP and decide on one time standard.

### `new-user`

[How to investigate] From just after the first login, read the `sudo:` lines and the lines `useradd` wrote in time order. To avoid mixing it up with a user an admin created, check who created it and from which connection.
[Reasoning] An intruder builds a foothold to get back in later. Adding a new user is a typical one.
[Detection and defense] Record user creation, `sudo` use and `authorized_keys` changes in an audit log (such as auditd) and alert on them. When you find it, disable that user and the compromised account's keys and password, then find and revert every change made after that time.
