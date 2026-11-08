# 検知ルールを書いて確かめる

## シナリオ

あなたは株式会社サンプルの SOC（ブルー）で、会員制 Web サービス（`members.example`）の検知を任されました。
サーバーは Web の `web01`・`web02` と、DB の `db01` の 3 台です。
最初の検知セットとして 4 本のルールを書くことになり、仕様（下の「ルールの仕様」）までは決まっています。

ルールは「イベントのリストを受け取り、鳴らすキーの集合を返す」Python の関数として書きます。
書いたら `check.py` で 2 段階のテストを流します。

1. **単体テスト**: `tests/` の手作りの例。鳴るべき例（陽性）と、似ているが鳴ってはいけない例（陰性）
2. **バックテスト**: 2026-10-19〜11-01 の 2 週間分の実ログ（`events.jsonl`）。この中には、拾うべき出来事と、拾ってはいけない紛らわしい出来事が混ざっています

単体テストが全部通っても、バックテストで見逃しや誤検知が出ることがあります。手作りの例は、書いた人が思いついた形のログでしかないからです。
**両方が通ったルールだけ**、`check.py` がフラグを出します。

時刻はすべて UTC です。

## 始め方

```bash
docker compose up -d
docker compose exec analyst bash
cp /evidence/rules_template.py ~/rules.py
vi ~/rules.py                          # 4 つの関数を書く
python3 /evidence/check.py ~/rules.py      # 4 本とも確かめる
python3 /evidence/check.py ~/rules.py D2   # 1 本だけ
```

ホーム（`~`）はコンテナを止めると消えます。書いたルールを残したいときは、画面の中身を手元にコピーしておきます。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `events.jsonl` | 3 台の 2 週間分のイベント。1 行 1 件。`source` で種類が分かれる |
| `exceptions.json` | 登録済みの例外。どのルールの・どの条件を・いつからいつまで除くか |
| `probe_paths.txt` | Web の探りに使われやすいパスの一覧（D3 で使う） |
| `tests/d1.json` … `d4.json` | 単体テスト。入力のイベントと、鳴るべきキー |
| `rules_template.py` | ルールのひな形 |
| `check.py` | 単体テストとバックテストを流し、合格したらフラグを出す |

`events.jsonl` のイベントの形:

| `source` | 主なフィールド |
|---|---|
| `sshd` | `result`（`success` / `failure`）、`user`、`src_ip`。失敗には `reason`（`bad_password` / `invalid_user` / `bad_key`）、成功には `method` |
| `sudo` | `user`、`run_as`、`command` |
| `auditd` | `op`（`read` / `write` / `attr`）、`path`、`exe`、`user`。`attr` は権限や持ち主の変更 |
| `web` | `client_ip`、`method`、`path`（クエリを含まない）、`query`、`status`、`user_agent` |

どのイベントにも `id`・`time`・`host`・`source` があります。

## ルールの仕様

| ルール | 関数 | 返すキー | 鳴らす条件 |
|---|---|---|---|
| D1 | `d1_ssh_burst` | 送信元の IP アドレス | 同じ送信元から、SSH ログインの失敗が **5 分以内に 5 回以上**。失敗の理由は問わない。ホストをまたいで数える。1 回目と 5 回目のちょうど 5 分差は含む |
| D2 | `d2_sudoers_change` | イベントの `id` | `auditd` の `write` か `attr` で、パスが `/etc/sudoers` そのもの、または `/etc/sudoers.d/` の**下**のファイル。D2 の例外に当たるものは除く |
| D3 | `d3_web_probe` | 送信元の IP アドレス | 同じ送信元が、`probe_paths.txt` のパスを **10 分以内に 3 種類以上**。D3 の例外に当たるリクエストは数えない。1 つ目からちょうど 10 分後は含む |
| D4 | `d4_remote_sudo` | `sudo` のイベントの `id` | SSH ログインの**成功**のあと 10 分以内（ちょうど 10 分は含む）に、**同じ人が同じホストで**実行した `sudo`。ただしログインの送信元が社内（`10.0.0.0/8`）なら鳴らさない |

### 例外の当て方（D2・D3）

`exceptions.json` の 1 件は、`match` のフィールドが**すべて**イベントと等しく、
イベントの時刻が `valid_from` 以上・`valid_until` 以下のときだけ当たります。期限の切れた例外は効きません。

### `probe_paths.txt` の数え方（D3）

- パスは大文字と小文字を区別せずに比べる。比べるのは `path` だけで、`query` は見ない
- 一覧のパスと等しければ、その 1 種類に当たる
- 一覧のパスが `/` で終わるもの（`/.git/` など）は、その下のどのパスも同じ 1 種類として数える（`/.git/HEAD` と `/.git/config` は 2 回とも `/.git/`）
- 同じ種類を何度叩いても 1 種類

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. D1（SSH の失敗の急増）を書き、単体テストとバックテストを通す | `ssh-burst` | 10 | `check.py` が D1 に出したフラグ。`4P{d1-…}` の形 |
| 2. D2（sudoers の変更）を書き、例外も当てて両方のテストを通す | `sudoers-change` | 20 | `check.py` が D2 に出したフラグ。`4P{d2-…}` の形 |
| 3. D3（Web の探り）を書き、両方のテストを通す | `web-probe` | 20 | `check.py` が D3 に出したフラグ。`4P{d3-…}` の形 |
| 4. D4（外から入ってすぐの sudo）を書き、両方のテストを通す | `remote-sudo` | 30 | `check.py` が D4 に出したフラグ。`4P{d4-…}` の形 |

## ヒント

1. 単体テストは通るのにバックテストで見逃すなら、仕様の「失敗の理由は問わない」「ホストをまたいで数える」「ちょうど 5 分は含む」を 1 つずつ見直します。`check.py` が出す見逃しの送信元で `events.jsonl` を絞ると、何が足りないかが見えます。
2. 誤検知に出たイベントの `path` を見ます。`/etc/sudoers` で**始まる**だけのパスはほかにもあります。見逃しが出たら、例外の `valid_until` を確かめます。
3. `/.git/` は 1 種類です。大文字のパスや、`/.git` で始まるだけの別のファイルにも気をつけます。許可した診断の送信元でも、届け出た時間の外なら鳴らします。
4. ログインと sudo を、人とホストの両方でつなぎます。10 分の境目と、社内の送信元の判定（`ipaddress` が使えます）を確かめます。1 回のログインのあとに sudo が 2 回あれば、どちらも鳴らします。

## 片付け

```bash
docker compose down -v
```

## English

# Write detection rules, then prove them

### Scenario

You work in Sample Corp's SOC (blue) and have been given detection for the members-only web service
(`members.example`). It runs on three servers: the web servers `web01` and `web02`, and the database `db01`.
The first detection set is four rules, and their specification (below) has already been agreed.

You write each rule as a Python function that takes a list of events and returns the set of keys it alerts on.
Then `check.py` runs two kinds of tests.

1. **Unit tests**: hand-made examples in `tests/` — events that must alert (positive) and similar ones that must not (negative)
2. **Backtest**: two weeks of real logs, 2026-10-19 to 11-01 (`events.jsonl`). It contains events you must catch and confusing ones you must not

A rule can pass every unit test and still miss or over-alert in the backtest, because hand-made examples only
cover the shapes their author thought of. `check.py` prints a flag **only for a rule that passes both**.

All times are UTC.

### Getting started

```bash
docker compose up -d
docker compose exec analyst bash
cp /evidence/rules_template.py ~/rules.py
vi ~/rules.py                                   # write the four functions
python3 /evidence/check.py ~/rules.py --en      # check all four
python3 /evidence/check.py ~/rules.py D2 --en   # just one
```

Your home directory (`~`) is wiped when the container stops. Copy your rules out from the screen if you want to keep them.

### Evidence

| File | Contents |
|---|---|
| `events.jsonl` | Two weeks of events from the three servers, one per line, typed by `source` |
| `exceptions.json` | Registered exceptions: which rule, which conditions, and from when until when |
| `probe_paths.txt` | Paths commonly used to probe web servers (for D3) |
| `tests/d1.json` … `d4.json` | Unit tests: input events and the keys that must alert |
| `rules_template.py` | A starting point for your rules |
| `check.py` | Runs the unit tests and the backtest, and prints a flag on a pass |

Event shapes in `events.jsonl`:

| `source` | Main fields |
|---|---|
| `sshd` | `result` (`success` / `failure`), `user`, `src_ip`. Failures have `reason` (`bad_password` / `invalid_user` / `bad_key`); successes have `method` |
| `sudo` | `user`, `run_as`, `command` |
| `auditd` | `op` (`read` / `write` / `attr`), `path`, `exe`, `user`. `attr` is a permission or ownership change |
| `web` | `client_ip`, `method`, `path` (without the query), `query`, `status`, `user_agent` |

Every event has `id`, `time`, `host` and `source`.

### Rule specification

| Rule | Function | Key returned | Alerts when |
|---|---|---|---|
| D1 | `d1_ssh_burst` | Source IP address | One source has **five or more** failed SSH logins **within five minutes**, for any reason, counted across hosts. Exactly five minutes between the first and fifth counts |
| D2 | `d2_sudoers_change` | Event `id` | An `auditd` `write` or `attr` on `/etc/sudoers` itself or on a file **under** `/etc/sudoers.d/`, unless a D2 exception applies |
| D3 | `d3_web_probe` | Source IP address | One source requests **three or more kinds** of path from `probe_paths.txt` **within ten minutes**. Requests covered by a D3 exception are not counted. Exactly ten minutes after the first counts |
| D4 | `d4_remote_sudo` | Event `id` of the `sudo` | A `sudo` run by **the same person on the same host** within ten minutes (inclusive) after a **successful** SSH login, unless that login came from inside the company (`10.0.0.0/8`) |

#### How exceptions apply (D2, D3)

An entry in `exceptions.json` applies only when **every** field in `match` equals the event's field and the
event's time is at or after `valid_from` and at or before `valid_until`. An expired exception has no effect.

#### Counting `probe_paths.txt` (D3)

- Compare paths case-insensitively, using `path` only, never `query`
- A path equal to an entry counts as that one kind
- An entry ending in `/` (such as `/.git/`) covers every path under it as the same kind (`/.git/HEAD` and `/.git/config` are both `/.git/`)
- Requesting the same kind again does not add a kind

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Write D1 (burst of SSH failures) and pass the unit tests and the backtest | `ssh-burst` | 10 | The flag `check.py` prints for D1: `4P{d1-…}` |
| 2. Write D2 (sudoers changes), apply the exceptions, and pass both tests | `sudoers-change` | 20 | The flag `check.py` prints for D2: `4P{d2-…}` |
| 3. Write D3 (web probing) and pass both tests | `web-probe` | 20 | The flag `check.py` prints for D3: `4P{d3-…}` |
| 4. Write D4 (sudo right after an outside login) and pass both tests | `remote-sudo` | 30 | The flag `check.py` prints for D4: `4P{d4-…}` |

### Hints

1. If the unit tests pass but the backtest misses something, go back through "for any reason", "across hosts" and "exactly five minutes counts" one at a time. Filter `events.jsonl` by the source `check.py` reports as missed to see what is lacking.
2. Look at the `path` of each false positive: other paths also merely start with `/etc/sudoers`. If something is missed, check the exceptions' `valid_until`.
3. `/.git/` is one kind. Watch for upper-case paths and for other files that only start with `/.git`. Even the approved scanner alerts outside its declared window.
4. Join logins and sudo on both the person and the host. Check the ten-minute boundary and how you decide a source is internal (`ipaddress` helps). If two sudo commands follow one login, both alert.

### Clean up

```bash
docker compose down -v
```
