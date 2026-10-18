# 4peiron-labs

[4peiron.dev](https://4peiron.dev/security/) のセキュリティトラックで使うラボです。
どのラボも、架空の会社「株式会社サンプル」を舞台に、設問の答えを `4P{...}` の形のフラグとして
サイトに提出します。

- **どのラボも、あなたの PC の中だけで動きます。** ホストのポートは開けず、外のネットワークにもつながりません。
- いまあるのは**調査型のラボ**です。ログ・設定などの証拠を読み取り専用で読みます。コンテナはネットワークにつながりません。
- これから、練習用の標的を置くラボも足します。標的は同じ PC の中のコンテナだけで、外への経路の無いネットワークでつながります。**ラボで使った手順を、ほかの機器やサービスに向けてはいけません。**
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
| レッド | `red/surface-inventory` |

## English

Labs for the security track on [4peiron.dev](https://4peiron.dev/security/), set at the fictional
Sample Corp. You submit the answers on the site as `4P{...}` flags.

- **Every lab runs only inside your own PC.** No host ports are opened and nothing connects to outside networks.
- The labs so far are **investigation labs**: you read logs and configuration as read-only evidence, and the container has no network access.
- Labs with a practice target are coming. The target is only a container on the same PC, on a network with no route out. **Never point what you do in a lab at any other device or service.**
- Every domain, IP address, company, person and credential is fictional.
- Read the Law and Ethics course and the lab agreement on the site first.
- The rules every lab follows are in [docs/rules.md](docs/rules.md) and are checked in CI.

Run `docker compose up -d` in a lab directory, then `docker compose exec analyst bash`; the evidence
is in `/evidence`. Clean up with `docker compose down -v`. Questions and hints are in each lab's `README.md`.

## License

MIT
