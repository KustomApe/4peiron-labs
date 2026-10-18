# ラボの決まり

このリポジトリのラボは、どれも**受講者自身の PC の中だけで動き、外とはつながらない**ように作ります。
ラボを足したり直したりするときは、この決まりを守ります。compose の設定にかかわる決まりは
[`tools/check_labs.py`](../tools/check_labs.py) が CI で確かめます（表の「CI」が ○ のもの）。

## ラボの形は 2 つ

| 形 | 中身 | ネットワーク |
|---|---|---|
| 調査型 | 架空の会社の証拠（ログ・設定など）を読んで答える | `network_mode: none`（どこにもつながらない） |
| 標的を置くラボ | 調査用のコンテナと、練習用の標的のコンテナを同じ PC の中に置く | 標的と調査用のコンテナだけが入る `internal: true` のネットワーク |

`internal: true` のネットワークは、中のコンテナどうしは通じますが、**外への経路がありません**。
インターネットにも、受講者の家や会社の LAN にも出られず、外からも入れません。

## すべてのラボに共通

| 決まり | CI |
|---|---|
| ホストのポートを開けない（`ports:` を書かない）。受講者の PC の外からも、同じ PC のブラウザからも届かない | ○ |
| `network_mode: host`、`external` のネットワークを使わない | ○ |
| どのサービスも `read_only: true`、`cap_drop: [ALL]`、`security_opt: [no-new-privileges:true]` | ○ |
| `privileged`、`cap_add`、`devices`、ホストの名前空間（`pid: host` など）を使わない | ○ |
| ホストからつなぐのはラボのディレクトリの中だけで、読み取り専用（`:ro`）。Docker のソケットはつながない | ○ |
| `README.md` に日本語と `## English` の両方がある | ○ |
| 登場するドメイン・IP アドレス・会社・人物・認証情報はすべて架空。ドメインは `example.com` `example.co.jp` や `.example` `.test`、IP アドレスは文書用（`192.0.2.0/24` `198.51.100.0/24` `203.0.113.0/24`）かプライベートの帯 | 警告 |
| 片付け方（`docker compose down -v`）を README に書く | |

## 標的を置くラボ

上の共通の決まりに加えて、次を守ります。

- **標的はこのリポジトリのために書いた架空のアプリだけ。** 実在する製品の既知の脆弱性（CVE のあるバージョンなど）を再現したものや、実在の攻撃ツール・マルウェアは持ち込まない
- 弱点は、学ぶことに必要な最小限だけにする。設問で扱わない弱点を残さない
- 標的のイメージはこのリポジトリの `Dockerfile` からビルドする。中身の分からない外のイメージをそのまま標的にしない（`debian` などの公式の土台は使ってよい）
- 標的に入れるデータ（利用者・パスワード・秘密の値）も架空にし、本物に見える個人情報を作らない
- 書き込みが要るときは `tmpfs` か名前付きボリュームにする。`down -v` で消える
- README の最初に、このラボの標的は受講者の PC の中のコンテナだけで、**ラボで使った手順をほかの機器やサービスに向けてはいけない**ことを書く
- 受講者に compose の設定を変えさせる手順（`ports:` を足す、`internal` を外す など）を書かない

## 新しいラボを足すとき

1. 形（調査型か、標的を置くか）を決め、上の決まりに沿って `compose.yaml` を書く
2. `python3 tools/check_labs.py <ラボのディレクトリ>` が通るのを確かめる（Docker が要る）
3. 答えが証拠や標的から 1 つに決まるかは、非公開の 4peiron.dev 側で確かめる（答えはこのリポジトリに置かない）
4. PR のひな形のチェックを埋める

---

## English

Every lab here runs **only inside the learner's own PC and never connects to anything outside it.**

- **Two shapes.** Investigation labs use `network_mode: none`. Labs with a practice target put the
  analyst container and the target on one network marked `internal: true`, which has no route out:
  not to the internet, not to the learner's LAN, and nothing can reach in.
- **For every lab (checked in CI):** no `ports:`; no `network_mode: host` or external networks; every
  service has `read_only: true`, `cap_drop: [ALL]` and `security_opt: [no-new-privileges:true]`; no
  `privileged`, `cap_add`, `devices` or host namespaces; bind mounts only from inside the lab directory
  and read-only; the README has Japanese and an `## English` section. All names, domains, addresses and
  credentials are fictional (warned in CI).
- **For practice targets:** the target is a fictional application written for this repository. No
  reproductions of known vulnerabilities in real products and no real attack tools or malware. Keep the
  weaknesses to what the questions need. Build target images from this repository. Use fictional data.
  The README must say up front that the only target is the container on your own PC, and never tell the
  learner to change the network settings.
