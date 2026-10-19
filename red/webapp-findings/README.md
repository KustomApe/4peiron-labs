# 診断の記録から所見を拾う

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームの一員です。対象は、通販サイトの**検証環境**です。
契約書と診断範囲（`scope.json`）には双方が署名済みで、診断用の一般会員のアカウント `tester-a`（会員番号 1001）と
`tester-b`（1002）を受け取っています。

診断の 1 日目が終わり、同僚がプロキシに残したリクエストと応答の記録（`proxy_history.jsonl`）が手元にあります。
対象にはもうアクセスしません。この記録だけを読み、報告書に載せる所見を拾ってください。

- 同僚は、入力がどう表示されるかを確かめるため、目印の文字列 `4p"<i>probe7731</i>` をいくつかのパラメータに入れました。
- CSRF の確認では、ふつうに送ったフォームを、`csrf_token` を外して送り直しています（`note` に「トークンなしで送り直し」）。
- 時刻はすべて UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `scope.json` | 診断の範囲。対象のホスト（`in_scope`）、対象外のホスト、診断用のアカウントと会員番号 |
| `proxy_history.jsonl` | プロキシの記録。1 行 1 リクエストで、`id`・送ったアカウント・リクエスト・応答（`status`・`resp_headers`・`resp_body`）・同僚のメモ `note` |

調査用のコンテナには `python3` と `jq` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. 診断の範囲の外にあるホストへ送ってしまったリクエストは？ 報告書とは別に、依頼元へすぐに伝える | `out-of-scope-request` | 10 | リクエストの `id`。`4P{R0000}` の形 |
| 2. 送ったアカウントとは別の会員の持ち物が、`200` で返ってきたリクエストのパスは？ | `idor-path` | 20 | クエリを除いたパス。`4P{/api/v1/items/1}` の形 |
| 3. 目印の文字列が、HTML の中にエスケープされずにそのまま出たパラメータの名前は？ | `reflected-param` | 20 | パラメータ名。`4P{name}` の形 |
| 4. `csrf_token` を外して送り直しても成功した（エラーにならなかった）フォームの送り先のパスは？ | `csrf-endpoint` | 30 | パス。`4P{/path/to}` の形 |

## ヒント

1. `scope.json` の `in_scope` に無いホストを探します。対象外の理由も `scope.json` に書いてあります。
2. JSON の応答には、持ち主の会員番号 `owner_id` が入っています。送ったアカウントの会員番号と比べます。`403` や `404` で断られたものは、正しく塞がっています。
3. エスケープされると `<` は `&lt;` に、`"` は `&quot;` になります。応答の `Content-Type` も見ます。JSON の応答はブラウザが HTML として描かないので、この設問では数えません。
4. 送り直しでも `403` ならトークンを確かめています。CSRF が問題になるのは、ブラウザが自動で付けるクッキーで認証しているときです。`Authorization` ヘッダーで認証する API は、別に考えます。

## 片付け

```bash
docker compose down -v
```

## English

# Picking findings out of an assessment log

### Scenario

You are on a security assessment team under contract with Sample Corp. The target is the **staging environment**
of its online shop. Both sides have signed the contract and the scope (`scope.json`), and you were given two
ordinary member accounts for testing: `tester-a` (member 1001) and `tester-b` (member 1002).

Day one of the assessment is over, and you have the request and response log a colleague's proxy recorded
(`proxy_history.jsonl`). You do not touch the target again. Read only this log and pick out findings for the report.

- To see how input is displayed, your colleague put the marker string `4p"<i>probe7731</i>` into several parameters.
- To check CSRF, your colleague resent ordinary forms with `csrf_token` removed (`note` says so).
- All times are UTC.

### Evidence

| File | Contents |
|---|---|
| `scope.json` | The scope: in-scope hosts (`in_scope`), out-of-scope hosts, test accounts and their member numbers |
| `proxy_history.jsonl` | The proxy log, one request per line: `id`, the account, the request, the response (`status`, `resp_headers`, `resp_body`) and the colleague's `note` |

The analyst container has `python3` and `jq`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which request went to a host outside the scope? You report it to the client at once, separately from the report | `out-of-scope-request` | 10 | The request `id`: `4P{R0000}` |
| 2. What is the path of the request that returned another member's object with `200`? | `idor-path` | 20 | The path without the query: `4P{/api/v1/items/1}` |
| 3. Which parameter put the marker into the HTML without escaping it? | `reflected-param` | 20 | The parameter name: `4P{name}` |
| 4. What is the path of the form that still succeeded when resent without `csrf_token`? | `csrf-endpoint` | 30 | The path: `4P{/path/to}` |

### Hints

1. Look for hosts that are not in `in_scope`. `scope.json` also says why they are out of scope.
2. JSON responses carry the owner's member number `owner_id`. Compare it with the sending account's number. A `403` or `404` means access was correctly refused.
3. Escaping turns `<` into `&lt;` and `"` into `&quot;`. Check the response `Content-Type` too: browsers do not render JSON as HTML, so JSON responses do not count here.
4. A `403` on the resend means the token is checked. CSRF matters when authentication relies on cookies the browser sends automatically; an API authenticated with an `Authorization` header is a different case.

### Clean up

```bash
docker compose down -v
```
