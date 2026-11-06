# サーバーの設定を直して点検を通す

## シナリオ

株式会社サンプルの会員制 Web サービスの Web サーバー `web01` を点検したところ、社内の Linux ベースライン（下の表）に合わない設定がいくつも見つかりました。
あなたはブルーの担当として、`web01` の設定一式の写し（`/evidence/server/`）を直し、点検スクリプト `audit.py` を通します。

点検は 4 つの分野に分かれていて、分野の項目が**すべて**通ると、その分野のフラグが出ます。
項目には 2 種類あります。

- **弱いところ**: ベースラインに合わない設定が残っていないか
- **壊さない**（`*` の付いた項目）: 直したせいで、要る機能が止まっていないか。設定を消せば弱いところは消えますが、サービスも止まります

直す前に、台帳（`inventory/staff.csv`）でだれが在籍していて、だれに何を許すかを確かめてください。台帳は正しいものとして扱い、直しません。

## 始め方

```bash
docker compose up -d
docker compose exec analyst bash
cp -r /evidence/server ~/server        # 直すのは写しのほう（/evidence は読み取り専用）
python3 /evidence/audit.py ~/server    # 何が通らないかを見る
vi ~/server/ssh/sshd_config            # 直して、また流す
```

ホーム（`~`）はコンテナを止めると消えます。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `server/ssh/sshd_config`・`sshd_config.d/` | sshd の設定 |
| `server/sudoers`・`sudoers.d/` | sudo の設定 |
| `server/group` | グループと、その補助メンバー（4 列目） |
| `server/sysctl.d/` | カーネルのパラメーター |
| `server/nginx/nginx.conf`・`sites-enabled/members.conf` | Web サーバーの設定 |
| `server/permissions.txt` | 主なファイルの権限の書き出し（`モード 持ち主 グループ パス`）。権限は、この表の値を直す |
| `inventory/staff.csv` | 人の台帳。在籍か、SSH で入ってよいか（`ssh`）、管理者の sudo を持ってよいか（`sudo`） |
| `audit.py` | 点検スクリプト。`--en` で英語の出力 |

## 設定の効き方

`audit.py` は、本物のサーバーと同じ決まりで「効いている値」を読みます。

- **sshd**: `Include` はその行の位置で読み込む。同じ項目が何度出てきても、**最初に**出てきた値が効く
- **sysctl**: `sysctl.d/*.conf` を名前の順に読み、**後から**出てきた値が効く。ベースラインの値は、既定値に頼らず設定ファイルに書く
- **sudo**: `sudoers.d` の中で、名前に `.` を含むファイルと `~` で終わるファイルは読まれない
- **nginx**: `ssl_protocols` や `add_header` は、内側（`location`・`server`）に 1 つでも書いてあれば、外側（`http`・`server`）の値を**受け継がない**

## ベースライン

| 分野 | 項目 | 決まり |
|---|---|---|
| K | K1〜K6 | `net.ipv4.ip_forward = 0`、`net.ipv4.conf.all.accept_redirects = 0`、`net.ipv4.conf.all.send_redirects = 0`、`net.ipv4.tcp_syncookies = 1`、`kernel.kptr_restrict` は 1 以上、`fs.suid_dumpable = 0` |
| K | K7* | アプリのために `net.core.somaxconn` を 4096 以上に保つ |
| S | S1〜S5 | `PermitRootLogin no`、`PasswordAuthentication no`、`MaxAuthTries` は 4 以下、`X11Forwarding no`、`AllowGroups sshusers`（ほかの許可・拒否の項目は使わない） |
| S | S6* | SSH で入れる人（`sshusers` のメンバー）が、台帳で在籍かつ `ssh` が `yes` の人と同じ |
| A | A1 | パスワード無し（`NOPASSWD`）の sudo は、`deploy` の `/usr/bin/systemctl restart members` だけ |
| A | A2・A3* | 管理者の sudo（コマンドが `ALL`）を持つ人が、台帳で在籍かつ `sudo` が `yes` の人と同じ |
| A | A4* | `deploy` は `/usr/bin/systemctl restart members` を実行できる（デプロイに要る） |
| A | A5 | `Defaults use_pty` |
| A | A6 | `/etc/shadow` は `0640 root shadow`、`/etc/sudoers` と `sudoers.d` の各ファイルは `0440 root root`、SSH のホスト鍵（秘密鍵）は `0600 root root`、`deploy` の `authorized_keys` は `0600 deploy deploy` |
| A | A7 | だれでも書ける（その他に `w`）のは、sticky の付いた `/tmp` だけ |
| W | W1〜W3 | `server_tokens off`、効いている `ssl_protocols` は `TLSv1.2` と `TLSv1.3` だけ、`autoindex` はどこも `on` にしない |
| W | W4 | HSTS（`Strict-Transport-Security`、`max-age` は 31536000 以上）が、443 のどの `location` の応答にも付く |
| W | W5 | 「.」で始まるファイル（`/.env`・`/.git/config` など）を、正規表現の `location` で拒む（`deny all;` か `return 404;`） |
| W | W6* | 443 で `/`（`http://127.0.0.1:8000` へ中継）と `/static/` を返し、80 は `https://$host$request_uri` へ 301 で転送する |

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. カーネルとネットワークの設定（K）を直し、点検を通す | `kernel-params` | 10 | `audit.py` が K に出したフラグ。`4P{hk-…}` の形 |
| 2. SSH の設定（S）を直し、点検を通す | `ssh-config` | 20 | `audit.py` が S に出したフラグ。`4P{hs-…}` の形 |
| 3. アカウント・sudo・権限（A）を直し、点検を通す | `accounts-sudo` | 30 | `audit.py` が A に出したフラグ。`4P{ha-…}` の形 |
| 4. Web サーバーと TLS の設定（W）を直し、点検を通す | `web-tls` | 30 | `audit.py` が W に出したフラグ。`4P{hw-…}` の形 |

## ヒント

1. 同じパラメーターが複数のファイルに書かれていないかを探します（`grep -r accept_redirects ~/server/sysctl.d`）。後から読まれるファイルの値が効きます。性能のための調整は、ファイルごと消すと K7 が通らなくなります。
2. `sshd_config` の 1 行目の `Include` が先に読まれるので、`sshd_config.d/` の値が勝ちます。だれが入れるかは、`sshusers` のメンバーを台帳と突き合わせて決めます。退職した人や、入る必要の無い人が残っていないか、入れるべき人が抜けていないかを見ます。
3. 管理者の sudo は、`%ops` のようなグループ経由でも付きます。`group` のメンバーと `sudoers.d` の各ファイルの両方を見ます。
4. `/uploads/` の `location` には自分の `add_header` があるので、`server` に書いた HSTS は受け継がれません。`ssl_protocols` も `http` と `server` の両方に書かれています。

## 片付け

```bash
docker compose down -v
```

## English

# Fix the server configuration and pass the audit

### Scenario

An audit of `web01`, the web server for Sample Corp's members-only service, found several settings that do not
meet the company's Linux baseline (table below). As the blue-team owner, you fix a copy of `web01`'s configuration
(`/evidence/server/`) until the audit script `audit.py` passes.

The audit has four areas, and each area prints its flag only when **every** item in it passes. There are two kinds of items.

- **Weaknesses**: settings that do not meet the baseline
- **Don't break it** (items marked `*`): features that must keep working after your fix. Deleting a setting can remove a weakness and take the service down with it

Before fixing anything, check the staff list (`inventory/staff.csv`) for who is still employed and what each person
may do. Treat the staff list as correct and leave it alone.

### Getting started

```bash
docker compose up -d
docker compose exec analyst bash
cp -r /evidence/server ~/server             # fix the copy (/evidence is read-only)
python3 /evidence/audit.py ~/server --en    # see what fails
vi ~/server/ssh/sshd_config                 # fix it and run again
```

Your home directory (`~`) is wiped when the container stops.

### Evidence

| File | Contents |
|---|---|
| `server/ssh/sshd_config`, `sshd_config.d/` | sshd configuration |
| `server/sudoers`, `sudoers.d/` | sudo configuration |
| `server/group` | Groups and their supplementary members (fourth field) |
| `server/sysctl.d/` | Kernel parameters |
| `server/nginx/nginx.conf`, `sites-enabled/members.conf` | Web server configuration |
| `server/permissions.txt` | Permissions of key files (`mode owner group path`). Fix permissions by editing this table |
| `inventory/staff.csv` | The staff list: employed or not, may log in over SSH (`ssh`), may have full sudo (`sudo`) |
| `audit.py` | The audit script. Add `--en` for English output |

### How settings take effect

`audit.py` reads the effective values by the same rules as a real server.

- **sshd**: an `Include` is read where it appears, and when a keyword appears more than once, **the first** value wins
- **sysctl**: `sysctl.d/*.conf` is read in name order, and **the last** value wins. Write baseline values in a file instead of relying on defaults
- **sudo**: files in `sudoers.d` whose names contain `.` or end in `~` are not read
- **nginx**: if an inner block (`location`, `server`) sets even one `ssl_protocols` or `add_header`, it **does not inherit** the outer (`http`, `server`) values

### Baseline

| Area | Items | Rule |
|---|---|---|
| K | K1–K6 | `net.ipv4.ip_forward = 0`, `net.ipv4.conf.all.accept_redirects = 0`, `net.ipv4.conf.all.send_redirects = 0`, `net.ipv4.tcp_syncookies = 1`, `kernel.kptr_restrict` 1 or more, `fs.suid_dumpable = 0` |
| K | K7* | Keep `net.core.somaxconn` at 4096 or more for the app |
| S | S1–S5 | `PermitRootLogin no`, `PasswordAuthentication no`, `MaxAuthTries` 4 or fewer, `X11Forwarding no`, `AllowGroups sshusers` (no other allow or deny keywords) |
| S | S6* | The people who can log in (members of `sshusers`) are exactly the employed people whose `ssh` is `yes` |
| A | A1 | The only passwordless (`NOPASSWD`) sudo is `deploy` running `/usr/bin/systemctl restart members` |
| A | A2, A3* | The people with full sudo (commands `ALL`) are exactly the employed people whose `sudo` is `yes` |
| A | A4* | `deploy` can run `/usr/bin/systemctl restart members` (deploys need it) |
| A | A5 | `Defaults use_pty` |
| A | A6 | `/etc/shadow` is `0640 root shadow`; `/etc/sudoers` and each file in `sudoers.d` are `0440 root root`; the SSH host private key is `0600 root root`; `deploy`'s `authorized_keys` is `0600 deploy deploy` |
| A | A7 | Nothing is world-writable except `/tmp`, which has the sticky bit |
| W | W1–W3 | `server_tokens off`; the effective `ssl_protocols` is only `TLSv1.2` and `TLSv1.3`; `autoindex` is never `on` |
| W | W4 | HSTS (`Strict-Transport-Security`, `max-age` 31536000 or more) is sent on the response of every `location` on 443 |
| W | W5 | A regex `location` refuses files starting with a dot (`/.env`, `/.git/config` ...) with `deny all;` or `return 404;` |
| W | W6* | Port 443 serves `/` (proxied to `http://127.0.0.1:8000`) and `/static/`, and port 80 redirects with 301 to `https://$host$request_uri` |

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Fix the kernel and network settings (K) and pass the audit | `kernel-params` | 10 | The flag `audit.py` prints for K: `4P{hk-…}` |
| 2. Fix the SSH settings (S) and pass the audit | `ssh-config` | 20 | The flag `audit.py` prints for S: `4P{hs-…}` |
| 3. Fix accounts, sudo and permissions (A) and pass the audit | `accounts-sudo` | 30 | The flag `audit.py` prints for A: `4P{ha-…}` |
| 4. Fix the web server and TLS settings (W) and pass the audit | `web-tls` | 30 | The flag `audit.py` prints for W: `4P{hw-…}` |

### Hints

1. Look for the same parameter in more than one file (`grep -r accept_redirects ~/server/sysctl.d`). The file read last wins. Deleting the performance tuning file as a whole makes K7 fail.
2. The `Include` on the first line of `sshd_config` is read first, so the values in `sshd_config.d/` win. Decide who may log in by matching the members of `sshusers` against the staff list: look for people who left or do not need access, and for people who should have access but are missing.
3. Full sudo can also come through a group such as `%ops`. Check both the members in `group` and every file in `sudoers.d`.
4. The `/uploads/` `location` has its own `add_header`, so it does not inherit the HSTS header set on the `server`. `ssl_protocols` is set in both `http` and `server`.

### Clean up

```bash
docker compose down -v
```
