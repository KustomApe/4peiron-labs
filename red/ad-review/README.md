# AD の列挙結果を整理する

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームの一員です。対象は、社内の検証用ドメイン `corp.example` です。
診断の範囲と手順は契約で決まっていて、列挙は情報システム部の立ち会いのもとで済んでいます。
手元には、そのとき書き出したユーザー・グループ・ホストの一覧と、5 日分のログオンの記録（イベント ID 4624）があります。

ドメインにはもうアクセスしません。書き出しだけを読み、攻撃に使われやすい弱点と、階層化（tiering）の決まりに
反する使い方を拾ってください。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `users.json` | ユーザー。有効か（`enabled`）、SPN（`serviceprincipalnames`）、Kerberos の事前認証が要らない設定（`dont_require_preauth`） |
| `groups.json` | グループとその直接のメンバー。`group:` で始まるメンバーは、グループの中のグループ |
| `hosts.csv` | ホストと階層（0・1・2） |
| `tiering_policy.md` | 情報システム部の階層化の決まり |
| `logons.jsonl` | 成功したログオン（4624）。`logon_type` は 2 = 対話型、3 = ネットワーク、5 = サービス、10 = リモートデスクトップ |

調査用のコンテナには `python3` と `jq` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. Kerberos の事前認証が要らない設定になっている、**有効な**アカウントは？ | `no-preauth` | 10 | アカウント名。`4P{name}` の形 |
| 2. `Domain Admins` に、直接または入れ子で入っている**有効な**アカウントは何個？ | `domain-admins-count` | 20 | 個数。`4P{10}` の形 |
| 3. SPN を持つアカウントのうち、Tier 0 にあたる（決まりのグループに直接または入れ子で入っている）ものは？ | `privileged-spn` | 20 | アカウント名。`4P{name}` の形 |
| 4. 階層化の決まりに反して、Tier 0 のアカウントで下の階層の機器にログオンしたのはだれ？ | `tier-violation` | 30 | アカウント名（`CORP\` を除く）。`4P{name}` の形 |

## ヒント

1. 同じ設定でも、無効化されたアカウントは今すぐ使われることはありません。無効なものは、別の指摘（棚卸し）として扱います。
2. グループの中のグループを、たどれるところまで展開します。同じアカウントが何本もの道で入っていても 1 個です。
3. SPN を持つアカウントは、ドメインのだれでもそのサービスのチケットを求められます。そのアカウントが強い権限を持っていると、パスワードの強さが直接の弱点になります。Tier 0 のグループは `tiering_policy.md` にあります。
4. 決まりの対象は、ログオンの種類 2 と 10 だけです。DC は Tier 0 なので、Tier 0 のアカウントが DC にログオンするのは決まりのとおりです。

## 片付け

```bash
docker compose down -v
```

## English

# Making sense of an AD enumeration

### Scenario

You are on a security assessment team under contract with Sample Corp. The target is its internal test domain
`corp.example`. The scope and methods are fixed in the contract, and the enumeration was done with the IT department
present. You have the user, group and host lists exported at the time, plus five days of logon records (event ID 4624).

You do not touch the domain again. Read only the exports and pick out the weaknesses an attacker would reach for,
and any use that breaks the tiering rules.

### Evidence

| File | Contents |
|---|---|
| `users.json` | Users: whether enabled (`enabled`), SPNs (`serviceprincipalnames`), and the "Kerberos pre-authentication not required" setting (`dont_require_preauth`) |
| `groups.json` | Groups and their direct members. A member starting with `group:` is a nested group |
| `hosts.csv` | Hosts and their tier (0, 1, 2) |
| `tiering_policy.md` | The IT department's tiering rules |
| `logons.jsonl` | Successful logons (4624). `logon_type`: 2 = interactive, 3 = network, 5 = service, 10 = remote desktop |

The analyst container has `python3` and `jq`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which **enabled** account does not require Kerberos pre-authentication? | `no-preauth` | 10 | The account name: `4P{name}` |
| 2. How many **enabled** accounts are in `Domain Admins`, directly or through nesting? | `domain-admins-count` | 20 | The count: `4P{10}` |
| 3. Which account with an SPN is Tier 0 (a direct or nested member of the policy's groups)? | `privileged-spn` | 20 | The account name: `4P{name}` |
| 4. Who logged on to a lower-tier machine with a Tier 0 account, against the tiering rules? | `tier-violation` | 30 | The account name without `CORP\`: `4P{name}` |

### Hints

1. A disabled account with the same setting cannot be used right now; treat it as a separate clean-up finding.
2. Expand nested groups as far as they go. An account reachable along several paths still counts once.
3. Anyone in the domain can request a service ticket for an account with an SPN, so if that account is powerful, its password strength becomes the weakness. The Tier 0 groups are listed in `tiering_policy.md`.
4. The rule covers logon types 2 and 10 only. DCs are Tier 0, so Tier 0 accounts logging on to a DC is as intended.

### Clean up

```bash
docker compose down -v
```
