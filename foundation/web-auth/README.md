# Web とログインの記録

## シナリオ

株式会社サンプルは、取引先向けの会員ポータル `portal.example.co.jp` を運営しています。
2026 年 10 月 6 日の午後、会員の 1 人から「登録メールアドレスが勝手に変わっている」と問い合わせがありました。

あなたは Web サーバー（nginx）のアクセスログ、ポータルのアプリが出す認証ログ、それにポータルが返す
HTTP 応答ヘッダーを保存したものを受け取りました。誰がどうやってアカウントに入り、何をしたのかを
記録から確かめ、あわせてポータルの Cookie の設定に弱いところがないかも見てください。

## 証拠ファイル

コンテナの中では `/evidence` にあります。

| ファイル | 内容 |
|---|---|
| `access.log` | nginx のアクセスログ（combined 形式）。時刻は日本時間（`+0900`） |
| `auth.jsonl` | ポータルの認証ログ。1 行が 1 つの JSON。`time` は UTC（末尾の `Z`）、`event` は `login.success` / `login.failure` / `logout` / `password.reset_requested` |
| `response_headers.txt` | ポータルの各ページが返した HTTP 応答ヘッダー（`curl -si` で採取）。Cookie の値はダミーです |

## 設問

| # | フラグ名 | 点 | 問い | 答えの形 |
|---|---|---|---|---|
| 1 | `spray-source` | 10 | 認証ログで、ログインに失敗したアカウント名（`username`）の種類がいちばん多い送信元 IP アドレスは？ | `4P{<IPアドレス>}` 例: `4P{192.0.2.1}` |
| 2 | `sprayed-account` | 20 | 設問 1 の送信元からのログインが 1 回だけ成功しています。そのアカウント名は？ | `4P{<アカウント名>}` 認証ログの表記どおり 例: `4P{a.example}` |
| 3 | `weak-cookie` | 20 | `response_headers.txt` の `Set-Cookie` のうち、`Secure` 属性も `HttpOnly` 属性も付いていない Cookie の名前は？ | `4P{<Cookie名>}` 例: `4P{example_cookie}` |
| 4 | `after-login` | 30 | 設問 2 のログイン成功の後、同じ送信元 IP アドレスが送った `POST` リクエストのうち、`/api/login` 以外のもののパスは？ | `4P{<パス>}` `/` から始まり、クエリ文字列なし 例: `4P{/api/example}` |

## ヒント

1. まず `head -3 auth.jsonl` でイベントの形を見ます。`jq` の `select()` で失敗のイベントだけを取り出し、送信元とアカウント名の組にしてから数えます。失敗の「回数」が多いことと、試した「アカウントの種類」が多いことは別のことです。
2. 設問 1 の送信元に絞り、結果が成功のイベントを探します。
3. `grep -i '^set-cookie' response_headers.txt` で Cookie を並べ、`;` の後ろに並ぶ属性を 1 つずつ見ます。片方だけ欠けているものもあります。
4. `access.log` を送信元 IP で `grep` し、`POST` の行を見ます。認証ログは UTC、アクセスログは日本時間（9 時間進んでいる）なので、ログイン成功の時刻を合わせてから前後を見比べましょう。

## 片付け

```bash
docker compose down -v
```

## English

# Web and Login Records

## Scenario

Sample Corp. runs `portal.example.co.jp`, a member portal for its business partners. On the afternoon of
6 October 2026 a member reported that "the registered e-mail address changed without my doing".

You receive the web server's (nginx) access log, the authentication log written by the portal application,
and a saved set of HTTP response headers returned by the portal. Work out from the records who got into
which account, how, and what they did, and check the portal's cookie settings for weaknesses.

## Evidence

Inside the container the files are under `/evidence`.

| File | What it is |
|---|---|
| `access.log` | nginx access log (combined format). Times are Japan time (`+0900`) |
| `auth.jsonl` | Portal authentication log, one JSON object per line. `time` is UTC (trailing `Z`); `event` is `login.success` / `login.failure` / `logout` / `password.reset_requested` |
| `response_headers.txt` | HTTP response headers returned by the portal's pages (captured with `curl -si`). Cookie values are dummies |

## Questions

| # | Flag name | Points | Question | Answer format |
|---|---|---|---|---|
| 1 | `spray-source` | 10 | In the authentication log, which source IP address failed to log in to the largest number of distinct accounts (`username`)? | `4P{<IP address>}` e.g. `4P{192.0.2.1}` |
| 2 | `sprayed-account` | 20 | Exactly one login from the source in question 1 succeeded. Which account? | `4P{<account>}` as written in the log, e.g. `4P{a.example}` |
| 3 | `weak-cookie` | 20 | Among the `Set-Cookie` headers in `response_headers.txt`, which cookie has neither the `Secure` nor the `HttpOnly` attribute? | `4P{<cookie name>}` e.g. `4P{example_cookie}` |
| 4 | `after-login` | 30 | After the successful login in question 2, the same source IP address sent one `POST` request other than `/api/login`. What is its path? | `4P{<path>}` starting with `/`, without a query string, e.g. `4P{/api/example}` |

## Hints

1. Start with `head -3 auth.jsonl` to see what an event looks like. Use `jq`'s `select()` to keep only the failures, turn them into source/account pairs, then count. Many failed *attempts* is not the same as many different *accounts*.
2. Narrow down to the source from question 1 and look for a successful outcome.
3. List the cookies with `grep -i '^set-cookie' response_headers.txt` and read the attributes after each `;`. Some cookies lack only one of the two.
4. `grep` the access log for the source IP address and look at the `POST` lines. The authentication log is UTC and the access log is Japan time (9 hours ahead), so line up the time of the successful login before comparing.

## Clean up

```bash
docker compose down -v
```
