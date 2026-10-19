# ルールを直して確かめる

## シナリオ

あなたは株式会社サンプルの SOC（ブルー）で、検知ルールの担当をしています。
ラボの Linux（`lab-lnx01`・`lab-web01`）に当てているルールが 5 本あり、平常時のアラートが多すぎるという声が上がっています。
同僚がチューニングの案を 4 つ出してくれましたが、入れる前に、**本当に直るのか・何かを見落とすようにならないか**を確かめる必要があります。

そこで、平常時の 7 日分（2026-09-28〜10-04）のイベントと、2026-10-07 にレッドと行った検証の日のイベントに、ルールを当ててみます。
検証の手順は `W01`〜`W05` で、レッドはコマンドの末尾に `# px:W03` のような目印を付けました。テレメトリはコマンドラインをそのまま記録しています。

### ルールの読み方

`rules.json` のルールは、次の決まりで当たります。

- `conditions` の条件が**すべて**合えば当たる
- ただし `exceptions` の条件のうち**どれか 1 つ**でも合えば、そのイベントでは鳴らない（例外）
- 条件は `{"field": …, "op": …, "value": …}`。`op` は `equals`（一致）・`in`（`value` の一覧のどれかと一致）・`contains`（含む）・`startswith`（で始まる）・`endswith`（で終わる）。大文字と小文字は区別する
- イベントにその `field` が無ければ、その条件は合わない

`tuning.json` の案は、それぞれ 1 本のルールに例外を 1 つ足すものです。

時刻はすべて UTC です。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `rules.json` | いま当てている検知ルール 5 本 |
| `tuning.json` | チューニングの案 4 つ（どのルールに、どの例外を足すか） |
| `baseline.jsonl` | 平常時 7 日分のイベント（プロセスの起動 `process` と、ファイルの書き込み `file`） |
| `exercise.jsonl` | 検証の日のイベント。ふだんの動きも混ざっている |
| `exercise_steps.csv` | 検証の手順と ATT&CK の技術 ID |

調査用のコンテナには `python3` と `jq` が入っています。決まりのとおりに当てる小さなスクリプトを書くと確実です。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. いまのルールのまま平常時のイベントに当てると、アラートがいちばん多いルールは？ | `noisiest-rule` | 10 | ルール ID。`4P{R100}` の形 |
| 2. 検証の手順のうち、いまのルールのどれにも当たらないものは？ | `uncaught-step` | 20 | 手順の ID。`4P{W00}` の形 |
| 3. チューニングの案のうち、いま検知できている検証の手順まで鳴らなくしてしまうものは？ | `bad-exception` | 20 | 案の ID。`4P{P0}` の形 |
| 4. 3 の案を除いた残りの案をすべて入れると、平常時 7 日分のアラートは全部で何件になる？ | `remaining-alerts` | 30 | 件数。`4P{100}` の形 |

## ヒント

1. ルールごとに、`baseline.jsonl` の何行に当たるかを数えます。例外も忘れずに当てます。
2. `exercise.jsonl` で、どれかのルールに当たったイベントの目印を集め、`exercise_steps.csv` の手順と比べます。プロセスのイベントだけでなく、ファイルのイベントにも書き込んだプロセスのコマンドラインが付いています。
3. 案ごとに、その例外を足す前と後で、検証の日のイベントのうち目印の付いたものが鳴るかどうかを比べます。平常時のノイズを消すつもりの例外が、攻撃の形にも合ってしまうことがあります。
4. 例外は「足す」もので、ルールにもともとある例外も残ります。1 本のルールに 2 つの案が入ることもあります。

## 片付け

```bash
docker compose down -v
```

## English

# Fix the rules, then prove it

### Scenario

You look after detection rules in Sample Corp's SOC (blue). Five rules run against the lab Linux hosts
(`lab-lnx01`, `lab-web01`), and people complain that they raise too many alerts on normal days.
A colleague has proposed four tuning changes. Before rolling them out you need to check that they really
help and that nothing starts slipping through.

So you replay the rules over seven normal days of events (2026-09-28 to 10-04) and over the events from the
test day on 2026-10-07, when red ran steps `W01` to `W05`. Red ended each command with a marker such as
`# px:W03`, and the telemetry records the command line as is.

#### How rules work

A rule in `rules.json` fires as follows.

- It fires when **all** of its `conditions` match.
- But if **any one** of its `exceptions` matches, it does not fire for that event.
- A condition is `{"field": …, "op": …, "value": …}`. `op` is `equals`, `in` (equals any value in the list),
  `contains`, `startswith` or `endswith`. Matching is case-sensitive.
- If the event has no such `field`, the condition does not match.

Each proposal in `tuning.json` adds one exception to one rule.

All times are UTC.

### Evidence

| File | Contents |
|---|---|
| `rules.json` | The five detection rules in use |
| `tuning.json` | Four tuning proposals (which rule, which exception to add) |
| `baseline.jsonl` | Seven normal days of events (process starts `process` and file writes `file`) |
| `exercise.jsonl` | Events from the test day, mixed with normal activity |
| `exercise_steps.csv` | The test steps and their ATT&CK technique IDs |

The analyst container has `python3` and `jq`. A small script that applies the rules exactly as described is the safest way.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Running the current rules over the normal days, which rule raises the most alerts? | `noisiest-rule` | 10 | The rule ID: `4P{R100}` |
| 2. Which test step matches none of the current rules? | `uncaught-step` | 20 | The step ID: `4P{W00}` |
| 3. Which proposal would also silence a test step that is detected today? | `bad-exception` | 20 | The proposal ID: `4P{P0}` |
| 4. With every proposal except the one in 3 applied, how many alerts do the seven normal days raise in total? | `remaining-alerts` | 30 | The count: `4P{100}` |

### Hints

1. For each rule, count how many lines of `baseline.jsonl` it matches. Apply the exceptions too.
2. Collect the markers of the `exercise.jsonl` events that some rule matches, and compare them with the steps in `exercise_steps.csv`. File events also carry the command line of the process that wrote the file.
3. For each proposal, compare whether the marked test-day events fire before and after adding its exception. An exception meant to remove normal noise can also fit the shape of an attack.
4. Exceptions are added; the rule's existing exceptions stay. One rule may receive two proposals.

### Clean up

```bash
docker compose down -v
```
