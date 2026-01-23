# Birdapp: TwitterAPI.io CLIツール

コマンドラインからTwitter/Xにツイートを投稿するためのツールです（TwitterAPI.ioを利用）。

## セットアップ

このリポジトリは依存関係の管理に `uv` パッケージマネージャーを使用しています。`uv` がまだインストールされていない場合は、以下のcurlコマンドでインストールできます：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストールを確認するには：

```bash
uv --version
```

詳細な手順やトラブルシューティングについては、[uvインストールドキュメント](https://astral.sh/uv/)を参照してください。

## インストール

uvを使用してCLIツールをグローバルにインストールできます：

```bash
uv tool install -U git+https://github.com/Promptly-Technologies-LLC/birdapp.git
```

インストール後、以下のように使用できます：

```bash
birdapp auth config
birdapp tweet --text "Hello world!"
```

## 設定

### TwitterAPI.io認証情報の取得

CLIを使用する前に、TwitterAPI.ioのAPIキーを取得してください。ダッシュボードで確認できます。

### 認証情報の設定

設定コマンドを実行して認証情報を設定します：

```bash
birdapp auth config
```

これにより、TwitterAPI.io認証情報の入力を求められ、`~/.config/birdapp/config.json` に安全に保存されます。

必要な項目:
- APIキー
- Proxy（必須）
- Username / Email / Password
- TOTP Secret（2FAを使う場合のみ）

環境変数で上書き可能:
- `TWITTERAPI_IO_API_KEY`
- `TWITTERAPI_IO_PROXY`
- `TWITTERAPI_IO_USERNAME`
- `TWITTERAPI_IO_EMAIL`
- `TWITTERAPI_IO_PASSWORD`
- `TWITTERAPI_IO_TOTP_SECRET`
- `TWITTERAPI_IO_LOGIN_COOKIE`

現在の設定を確認するには（シークレットは表示されません）：

```bash
birdapp auth config --show
```

### ログイン（login_cookie取得）

ツイート投稿やメディア投稿には login_cookie が必要です。以下を実行して保存します：

```bash
birdapp auth login
```

保存された login_cookie を使って投稿が行われます。ユーザー情報を確認する場合は：

```bash
birdapp auth whoami
```

## 使い方

### ツイートの投稿

ツイートを投稿するには：

```bash
birdapp auth login
birdapp tweet --text "ツイート内容をここに入力"
```

メディア付きでツイートを投稿するには：

```bash
birdapp tweet --text "この画像をチェック！" --media /path/to/image.jpg
```

メディアのみのツイート（テキストなし）を投稿するには：

```bash
birdapp tweet --media /path/to/image.jpg
```

### ツイートへの返信

ツイートIDを使用して返信するには：

```bash
birdapp tweet --text "いいポイントですね！" --reply-to 1234567890
```

ツイートURLを使用して返信するには：

```bash
birdapp tweet --text "同意します！" --reply-to "https://x.com/user/status/1234567890"
```

返信にメディアを含めることもできます：

```bash
birdapp tweet --text "これが私の返信です" --media /path/to/image.jpg --reply-to 1234567890
```

### ツイートの取得

IDでツイートを取得するには（一度に最大100件）：

```bash
birdapp get 1234567890
birdapp get 1234567890 9876543210 --format detailed
birdapp get 1234567890 --json
```

### ユーザーの検索

ユーザー名またはIDでユーザーを検索するには（一度に最大100件）：

```bash
birdapp user elonmusk
birdapp user @nasa @spacex
birdapp user 44196397 --by-id
birdapp user elonmusk --format detailed
```

### Twitter Community Archiveからのツイートのインポート

Twitter Community Archiveを通じてツイートを公開共有している場合、アーカイブからダウンロードしてSQLiteデータベースにインポートし、ローカルで検索・分析できます：

```bash
birdapp import-archive --username yourusername
```

既にarchive.jsonファイルをダウンロードしている場合は、ローカルファイルからインポートできます：

```bash
birdapp import-archive --path /path/to/archive.json
```

### ヘルプ

利用可能なすべてのコマンドを確認するには：

```bash
birdapp --help
```

特定のコマンドのヘルプを確認するには：

```bash
birdapp tweet --help
birdapp auth --help
birdapp get --help
birdapp user --help
```
