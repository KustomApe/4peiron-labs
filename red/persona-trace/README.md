# 公開情報から露出を洗い出す

## シナリオ

あなたは株式会社サンプルと契約したセキュリティ診断チームの一員です。今回の依頼は**ソーシャルエンジニアリングへの耐性評価**です。
攻撃者が社員の公開情報から何を組み立てられるかを洗い出し、露出を減らす提案につなげます。

対象は、**本人の書面の同意を得た**社員の港 ひかりさんです。依頼書（`scope.md`）のとおり、範囲は保存しておいた公開ページのデータだけです。
本人や関係者に連絡したり、どこかにログインしたりはしません。登場する人・会社・サービスはすべて架空です。

**ここで使う手順を、実在の人に向けてはいけません。** 同意と依頼の無い人を調べることは、このラボの外ではつきまといやプライバシーの侵害になりえます。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `scope.md` | 依頼書の抜粋。目的・対象者・範囲・報告先 |
| `chirp/hikari_mnt/` | 短文 SNS「Chirp」のプロフィール（`profile.json`）・アイコン（`avatar.jpg`）・投稿（`posts.jsonl`。時刻は UTC） |
| `snapgallery/<アカウント>/` | 写真共有サービス「Snapgallery」で見つかった、港さんらしいアカウント 3 つ。プロフィール・アイコン・写真・投稿の一覧 |
| `devhub/hikari-mnt/` | コード共有サービス「DevHub」のプロフィールと、公開リポジトリのコミットログ |
| `corp-site/` | 株式会社サンプルのサイトから保存したプレスリリースと採用ページ |

調査用のコンテナには `exiftool`・`python3`・`jq`・`sha256sum` が入っています。

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. Snapgallery の 3 つのアカウントのうち、Chirp の `hikari_mnt` と同じ人のものは？ | `other-account` | 10 | アカウント名。`4P{name.example}` の形 |
| 2. そのアカウントの写真のうち、撮影地点の位置情報が残っている 1 枚は、どこで撮られた？ | `photo-location` | 20 | 緯度と経度を 10 進の度で、小数第 3 位まで（四捨五入）。`4P{12.345,123.456}` の形 |
| 3. Chirp の投稿を日本時間に直すと、平日（月〜金）にいちばん投稿が多いのは何時台？ | `active-hour` | 20 | 0〜23 の数。`4P{7}` の形 |
| 4. 株式会社サンプルの社員のメールアドレスは、名前をどう並べた形？ | `email-format` | 30 | 名を `given`、姓を `family` と書いて、区切りの記号も含めて答える。`4P{family-given}` の形 |

## ヒント

1. 名前の似たアカウントは見た目で決めず、アイコンの画像を `sha256sum` で比べます。
2. `exiftool -n` を使うと、緯度・経度が 10 進の度で出ます。写真を全部見て、位置情報が残っているものを探します。
3. `created_at` は UTC です。日本時間は UTC より 9 時間進んでいます。日付が変わる投稿もあるので、曜日は日本時間に直してから決めます。
4. コミットログの `Author:` と、プレスリリースの問い合わせ先を見比べます。`recruit@` のような窓口のアドレスは個人のものではありません。

## 片付け

```bash
docker compose down -v
```

## English

# Mapping an employee's public footprint

### Scenario

You are on a security assessment team under contract with Sample Corp. This engagement is a **social engineering resilience assessment**:
list what an attacker could assemble from an employee's public information, and use it to propose how to reduce that exposure.

The subject is Hikari Minato, an employee who has **given written consent**. As the engagement letter (`scope.md`) says, the scope is
only the public pages saved in this folder. You do not contact the subject or anyone else, and you do not log in anywhere. Every person,
company and service here is fictional.

**Never point these techniques at a real person.** Researching someone without consent and a mandate can amount to stalking or a privacy
violation outside this lab.

### Evidence

| File | Contents |
|---|---|
| `scope.md` | Excerpt of the engagement letter: purpose, subject, scope and who receives the report |
| `chirp/hikari_mnt/` | The profile (`profile.json`), avatar (`avatar.jpg`) and posts (`posts.jsonl`, timestamps in UTC) on the microblog "Chirp" |
| `snapgallery/<account>/` | Three accounts on the photo-sharing service "Snapgallery" that might be Minato's: profile, avatar, photos and post list |
| `devhub/hikari-mnt/` | The profile on the code-sharing service "DevHub" and the commit log of the public repositories |
| `corp-site/` | A press release and the careers page saved from Sample Corp.'s website |

The analyst container has `exiftool`, `python3`, `jq` and `sha256sum`.

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. Which of the three Snapgallery accounts belongs to the same person as `hikari_mnt` on Chirp? | `other-account` | 10 | The account name: `4P{name.example}` |
| 2. One photo on that account still carries the location where it was taken. Where was it taken? | `photo-location` | 20 | Latitude and longitude in decimal degrees, rounded to 3 decimal places: `4P{12.345,123.456}` |
| 3. Converting the Chirp posts to Japan time, which hour of the day has the most posts on weekdays (Monday to Friday)? | `active-hour` | 20 | A number from 0 to 23: `4P{7}` |
| 4. How do Sample Corp. email addresses arrange an employee's name? | `email-format` | 30 | Write the given name as `given` and the family name as `family`, including the separator: `4P{family-given}` |

### Hints

1. Don't judge look-alike accounts by eye. Compare the avatar images with `sha256sum`.
2. `exiftool -n` prints latitude and longitude in decimal degrees. Check every photo for one that still has a location.
3. `created_at` is in UTC, and Japan is nine hours ahead. Some posts change date, so decide the weekday after converting to Japan time.
4. Compare the `Author:` lines in the commit log with the press contact. A shared inbox such as `recruit@` is not a personal address.

### Clean up

```bash
docker compose down -v
```
