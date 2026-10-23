# 4peiron-labs

[4peiron.dev](https://4peiron.dev/security/) のセキュリティトラックで使うラボです。
どのラボも、架空の会社「株式会社サンプル」を舞台に、設問の答えを `4P{...}` の形のフラグとして
サイトに提出します。

- **どのラボも、あなたの PC の中だけで動きます。** ホストのポートは開けず、外のネットワークにもつながりません。
- いまあるのは、どのトラックも**調査型のラボ**です。ログ・設定などの証拠を読み取り専用で読みます。コンテナはネットワークにつながらず、**攻撃する標的はありません。**
- **ラボで使った手順を、ほかの機器やサービスに向けてはいけません。**
- 登場するドメイン・IP アドレス・会社・人物・認証情報はすべて架空です（`example.com`、文書用の IP アドレス帯）。
- 使う前に、サイトの「法律と倫理」コースと、ラボ利用の同意を読んでください。

ラボを作るときの決まりは [docs/rules.md](docs/rules.md) にあります。CI（`tools/check_labs.py`）が、
どのラボもその決まりを守っているかを確かめます。

## 使い方

Docker が入った自分の PC で動かします。

```bash
git clone https://github.com/KustomApe/4peiron-labs.git
cd 4peiron-labs/blue/ssh-bruteforce   # 例
docker compose up -d
docker compose exec analyst bash      # /evidence に証拠があります
```

終わったら片付けます。

```bash
docker compose down -v
```

設問とヒントは各ラボの `README.md` にあります。

## ラボの一覧

| トラック | ディレクトリ |
|---|---|
| 基礎 | `foundation/linux-audit`, `foundation/network-logs`, `foundation/web-auth` |
| ブルー | `blue/ssh-bruteforce`, `blue/web-incident`, `blue/windows-timeline` |
| レッド | `red/surface-inventory`, `red/webapp-findings`, `red/access-review`, `red/ad-review`, `red/report-triage` |
| パープル | `purple/exercise-review`, `purple/detection-tuning`, `purple/coverage-map`, `purple/fp-triage` |

### レッドとパープルのラボの形

- **レッド**は、守る側に頼まれた事前点検です。架空の資産台帳・DNS ゾーン・設定の書き出し・診断の記録などを読み、弱いところを見つけて優先度をつけます。
- **パープル**は、同じ架空の事案を、攻撃側の記録と守る側のログ（テレメトリ・アラート・検知ルール）の両方から読み、検知できた所・できなかった所を突き合わせます。

練習用の標的を同じ PC の中に置くラボの決まりは [docs/rules.md](docs/rules.md) に用意してありますが、まだ 1 台もありません。作るかどうかは、必要になったときに別に決めます。

## English

Labs for the security track on [4peiron.dev](https://4peiron.dev/security/), set at the fictional
Sample Corp. You submit the answers on the site as `4P{...}` flags.

- **Every lab runs only inside your own PC.** No host ports are opened and nothing connects to outside networks.
- Every lab so far, in every track, is an **investigation lab**: you read logs and configuration as read-only evidence, the container has no network access, and **there is no target to attack.**
- Red labs are a pre-assessment requested by the defenders: you read fictional asset lists, DNS zones, config exports and assessment logs, find the weak spots and rank them.
- Purple labs have you read the same fictional incident from both the attacker's record and the defenders' logs, and match what was detected and what was missed.
- Rules for labs with a local practice target are in [docs/rules.md](docs/rules.md), but none exist yet; whether to build one is a separate, later decision.
- **Never point what you do in a lab at any other device or service.**
- Every domain, IP address, company, person and credential is fictional.
- Read the Law and Ethics course and the lab agreement on the site first.
- The rules every lab follows are in [docs/rules.md](docs/rules.md) and are checked in CI.

Run `docker compose up -d` in a lab directory, then `docker compose exec analyst bash`; the evidence
is in `/evidence`. Clean up with `docker compose down -v`. Questions and hints are in each lab's `README.md`.

## License

MIT
