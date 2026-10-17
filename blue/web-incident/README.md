# Web サーバーの侵入を時系列にする

## シナリオ

あなたは株式会社サンプルのセキュリティ担当です。
コーポレートサイト `www.example.co.jp`（nginx + PHP）のアップロード用ディレクトリに、見覚えのない PHP ファイルがあると開発者から報告がありました。

nginx のアクセスログ 4 日分（2026-09-16〜09-19）、エラーログ 2 日分、Web ルート（`/var/www/html`）のファイル一覧を預かりました。
ファイル一覧はサーバーを止める前に取ったもので、パス・サイズ・更新時刻・SHA-256 だけが入っています。ファイルの中身はありません。

サーバーの時計は日本時間（`+0900`）です。答えの時刻は UTC に直してください。
編集担当者は事務所（`192.0.2.10`）から管理画面に入り、記事用の画像をアップロードします。

## 証拠ファイル

| ファイル | 中身 |
|---|---|
| `access.log.3.gz` | 09-16 のアクセスログ（gzip。`zcat` か `zgrep` で読めます） |
| `access.log.2.gz` | 09-17 のアクセスログ（gzip） |
| `access.log.1` | 09-18 のアクセスログ |
| `access.log` | 09-19 のアクセスログ |
| `error.log.1` | 09-18 のエラーログ |
| `error.log` | 09-19 のエラーログ |
| `webroot_listing.csv` | Web ルートのファイル一覧（`path,size,mtime,sha256`） |

## 設問

| 設問 | サイトのフラグ名 | 点 | 答えの形 |
|---|---|---|---|
| 1. アップロードされた不審なファイルの名前は？ | `upload-file` | 10 | ディレクトリを除いたファイル名。`4P{example.php}` の形 |
| 2. そのファイルをアップロードした IP アドレスが、ログに初めて現れた時刻は？ | `first-seen` | 20 | UTC、秒まで。`4P{2026-01-02T03:04:05}` の形 |
| 3. そのファイルへのリクエストは、4 日分のアクセスログに全部で何件ありますか？ | `file-requests` | 20 | 送信元・メソッドを問わない件数。`4P{12}` の形 |
| 4. アップロードした IP とは別に、そのファイルへアクセスした IP アドレスは？ | `second-ip` | 30 | `4P{192.0.2.1}` の形 |

## ヒント

1. `uploads/` の下にあるのはふつう画像や PDF です。拡張子で絞り込みます。
2. ファイルの更新時刻とほぼ同じ時刻の `POST /admin/upload.php` を探すと、送信元がわかります。その IP の最初の行の時刻を UTC に直します。
3. gzip のファイルも忘れずに数えます。`zcat -f access.log* | grep ...` のようにまとめて読めます。
4. 答え 3 で数えた行の送信元を `sort | uniq -c` で並べます。エラーログにも手がかりがあります。

## 片付け

```bash
docker compose down -v
```

## English

# Building a timeline of a web server intrusion

### Scenario

You are on Sample Corp.'s security team. A developer found an unfamiliar PHP file in the upload directory of
the corporate site `www.example.co.jp` (nginx + PHP).

You were handed four days of nginx access logs (2026-09-16 to 09-19), two days of error logs, and a file listing
of the web root (`/var/www/html`). The listing was taken before the server was shut down and holds only path,
size, modification time and SHA-256. File contents are not included.

The server clock is Japan time (`+0900`). Convert answer times to UTC.
Editors log in to the admin panel from the office (`192.0.2.10`) and upload images for articles.

### Evidence

| File | Contents |
|---|---|
| `access.log.3.gz` | Access log for 09-16 (gzip; read with `zcat` or `zgrep`) |
| `access.log.2.gz` | Access log for 09-17 (gzip) |
| `access.log.1` | Access log for 09-18 |
| `access.log` | Access log for 09-19 |
| `error.log.1` | Error log for 09-18 |
| `error.log` | Error log for 09-19 |
| `webroot_listing.csv` | Web root file listing (`path,size,mtime,sha256`) |

### Questions

| Question | Flag name | Points | Answer format |
|---|---|---|---|
| 1. What is the name of the suspicious uploaded file? | `upload-file` | 10 | File name without directories: `4P{example.php}` |
| 2. When did the IP address that uploaded it first appear in the logs? | `first-seen` | 20 | UTC to the second: `4P{2026-01-02T03:04:05}` |
| 3. How many requests for that file are in the four days of access logs? | `file-requests` | 20 | Count of all sources and methods: `4P{12}` |
| 4. Apart from the uploading IP, which IP address accessed the file? | `second-ip` | 30 | `4P{192.0.2.1}` |

### Hints

1. `uploads/` normally holds images and PDFs. Filter by extension.
2. Find the `POST /admin/upload.php` at about the file's modification time to get the source. Convert the time of that IP's first line to UTC.
3. Do not forget the gzip files. `zcat -f access.log* | grep ...` reads them all at once.
4. List the sources of the lines you counted in question 3 with `sort | uniq -c`. The error log has clues too.

### Clean up

```bash
docker compose down -v
```
