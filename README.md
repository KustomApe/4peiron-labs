# 4peiron-labs

[4peiron.dev](https://4peiron.dev/security/) のセキュリティトラックで使う**調査型のラボ**です。
どのラボも、架空の会社「株式会社サンプル」のログ・設定・ソースコードなどの証拠を読み、
設問の答えを `4P{...}` の形のフラグとしてサイトに提出します。

- 攻撃するサーバーはありません。コンテナは**ネットワークにつながらず**、証拠は読み取り専用です。
- 登場するドメイン・IP アドレス・会社・人物・認証情報はすべて架空です（`example.com`、文書用の IP アドレス帯）。
- 使う前に、サイトの「法律と倫理」コースと、ラボ利用の同意を読んでください。

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
| レッド | `red/surface-inventory` |

## English

Investigation labs for the security track on [4peiron.dev](https://4peiron.dev/security/).
Each lab hands you fictional evidence from Sample Corp. (logs, configuration, source code) and asks
questions whose answers you submit on the site as `4P{...}` flags.

- There is nothing to attack. The container has **no network access** and the evidence is read-only.
- Every domain, IP address, company, person and credential is fictional.
- Read the Law and Ethics course and the lab agreement on the site first.

Run `docker compose up -d` in a lab directory, then `docker compose exec analyst bash`; the evidence
is in `/evidence`. Clean up with `docker compose down -v`. Questions and hints are in each lab's `README.md`.

## License

MIT
