# 通信ログを読む

## シナリオ

株式会社サンプルの小さな営業所では、端末がつながるネットワークの通信を Zeek というソフトで記録しています。
Zeek はパケットそのものではなく「誰が・いつ・どこへ・どれだけ」通信したかを表にして残します。

ある朝、ファイアウォールの担当者から「夜中に営業所から見慣れない宛先へ大きな通信が出ていたようだ」と
連絡がありました。あなたは 2026 年 9 月 15 日（日本時間）1 日分の Zeek のログを受け取り、何が起きていたのかを
調べることになりました。

営業所の端末は `10.20.30.0/24` にあり、`10.20.30.2` が社内の DNS サーバーです。センサーは端末のセグメントを
見ているので、DNS の問い合わせは「端末 → 10.20.30.2」として記録されています。

## 証拠ファイル

コンテナの中では `/evidence` にあります。

| ファイル | 内容 |
|---|---|
| `conn.log` | Zeek の接続ログ。1 行が 1 つの通信（TCP の接続や UDP のやり取り） |
| `dns.log` | Zeek の DNS ログ。1 行が 1 つの問い合わせと応答 |

どちらもタブ区切りのテキストです。`#` で始まる行は見出しで、`#fields` の行に列の名前が並んでいます。
`ts` は UNIX 時刻（1970-01-01 からの秒数、UTC）です。conn.log の `id.orig_h` は通信を始めた側、`id.resp_h` は
受けた側、`orig_bytes` は始めた側が送ったバイト数、`resp_bytes` は受けた側が送り返したバイト数です。

## 設問

| # | フラグ名 | 点 | 問い | 答えの形 |
|---|---|---|---|---|
| 1 | `beacon-host` | 10 | ほかのどの端末も問い合わせないドメインを、1 台の端末だけがほぼ一定の間隔で一日中問い合わせ続けています。その端末の IP アドレスは？ | `4P{<IPアドレス>}` 例: `4P{192.168.1.23}` |
| 2 | `beacon-interval` | 20 | 設問 1 の問い合わせは何秒おきですか。 | `4P{<秒数>}` 秒の整数（小数点以下は四捨五入） 例: `4P{60}` |
| 3 | `upload-dest` | 30 | 社内（`10.20.30.0/24`）の端末から始まり社外の IP アドレスへ向かった通信について、`orig_bytes` を「宛先 IP アドレスと宛先ポートの組」ごとに合計します。合計がいちばん大きい組は？ | `4P{<IPアドレス>:<ポート>}` 例: `4P{192.0.2.1:21}` |

## ヒント

1. まず列の並びを `grep '^#fields' dns.log` で確かめます。`grep -v '^#' dns.log | awk -F'\t' '{print $3, $10}' | sort | uniq -c | sort -rn | head` のように、「問い合わせ元とドメインの組」ごとに数えると、目立つ組が見えてきます。数が多いだけなら人気のサイトかもしれません。問い合わせ元が 1 台だけかどうかも確かめましょう。
2. 設問 1 で見つけた組の `ts` を並べて、となり合う行の差を `awk` で計算してみましょう。`date -u -d @1789398000` で UNIX 時刻を読める日時に直せます。
3. `orig_bytes`（送った量）と `resp_bytes`（受け取った量）を取り違えないように注意します。ダウンロードが多いだけの通信は対象外です。宛先が `10.` で始まる社内向けの通信も外します。`awk` の連想配列（例: `sum[$5":"$6] += $10`）を使うと、組ごとの合計を出せます。

## 片付け

```bash
docker compose down -v
```

## English

# Reading Network Logs

## Scenario

A small Sample Corp. branch office records the traffic on its client network with Zeek. Zeek does not keep
the packets; it keeps tables of who talked to whom, when, and how much.

One morning the firewall team reports that "something at the branch sent a lot of data to an unfamiliar
destination overnight". You receive one day of Zeek logs for 15 September 2026 (Japan time) and are asked
to find out what happened.

The branch's machines are in `10.20.30.0/24`, and `10.20.30.2` is the internal DNS server. The sensor watches
the client segment, so DNS lookups appear as "client → 10.20.30.2".

## Evidence

Inside the container the files are under `/evidence`.

| File | What it is |
|---|---|
| `conn.log` | Zeek connection log. One line per connection (a TCP connection or a UDP exchange) |
| `dns.log` | Zeek DNS log. One line per query and its answer |

Both are tab-separated text. Lines starting with `#` are headers; the `#fields` line names the columns.
`ts` is UNIX time (seconds since 1970-01-01, UTC). In conn.log, `id.orig_h` is the side that started the
connection, `id.resp_h` the side that answered, `orig_bytes` the bytes the originator sent and `resp_bytes`
the bytes sent back.

## Questions

| # | Flag name | Points | Question | Answer format |
|---|---|---|---|---|
| 1 | `beacon-host` | 10 | One client keeps querying a domain that no other client queries, at an almost fixed interval, all day. What is that client's IP address? | `4P{<IP address>}` e.g. `4P{192.168.1.23}` |
| 2 | `beacon-interval` | 20 | How many seconds apart are the queries from question 1? | `4P{<seconds>}` whole seconds, rounded to the nearest integer, e.g. `4P{60}` |
| 3 | `upload-dest` | 30 | Take the connections started by a client in `10.20.30.0/24` to an external IP address and add up `orig_bytes` per pair of destination IP address and destination port. Which pair has the largest total? | `4P{<IP address>:<port>}` e.g. `4P{192.0.2.1:21}` |

## Hints

1. Check the column order first with `grep '^#fields' dns.log`. Counting per pair of client and domain, for example `grep -v '^#' dns.log | awk -F'\t' '{print $3, $10}' | sort | uniq -c | sort -rn | head`, makes outliers stand out. A high count alone may just mean a popular site; also check whether only one client asks for that domain.
2. List the `ts` values of the pair you found and compute the difference between neighbouring lines with `awk`. `date -u -d @1789398000` turns a UNIX time into a readable date.
3. Do not mix up `orig_bytes` (sent) and `resp_bytes` (received); large downloads do not count. Leave out destinations starting with `10.`, which are internal. An `awk` associative array (e.g. `sum[$5":"$6] += $10`) gives you a total per pair.

## Clean up

```bash
docker compose down -v
```
