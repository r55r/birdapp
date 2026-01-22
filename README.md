# Birdapp: Twitter/X CLIツール

コマンドラインからTwitter/Xにツイートを投稿するためのツールです。

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

### Twitter API認証情報の取得

CLIを使用する前に、Twitter APIの認証情報を設定する必要があります。そのためには、[Twitter/X開発者アカウントに登録](https://developer.twitter.com/)する必要があります。

ダッシュボードでアプリケーションを作成する必要があります。アプリケーションに「読み取りと書き込み」権限があることを確認してください。開発者ダッシュボードのアプリケーションの「Keys and Tokens」セクションから、以下を生成します：

- APIキー
- APIシークレット
- アクセストークン
- アクセストークンシークレット

### 認証情報の設定

設定コマンドを実行して認証情報を設定します：

```bash
birdapp auth config --oauth1 # または --oauth2
```

これにより、Twitter API認証情報の入力を求められ、`~/.config/birdapp/config.json` に安全に保存されます。

現在の設定を確認するには（シークレットは表示されません）：

```bash
birdapp auth config --show
```

### 認証フロー

BirdappはOAuth1とOAuth2の両方をサポートしています。セキュリティ要件とXアプリの登録方法に基づいて選択してください。

OAuth1:
- 設定完了後、別途ログインステップは不要です。
- アプリのキー/シークレットとユーザーアクセストークン/シークレットをローカルに保存します。
- 設定はシングルアカウント（一度に1セットのトークン）です。

OAuth2（PKCEを使用した認可コード）:
- 別途ログインステップが必要です。
- トークンはユーザーIDごとに保存されます（複数アカウント対応）。
- `auth whoami` は `--user-id` が指定されない限り、最初に保存されたトークンをデフォルトで使用します。
- `X_OAUTH2_CLIENT_SECRET` が設定されている場合、クライアントはコンフィデンシャルとして動作します。それ以外の場合は、パブリックPKCEを使用し、アプリシークレットの保存を避けます。どちらのフローでもユーザー体験は同じですが、アプリをコンフィデンシャルとして登録した場合は、コンフィデンシャルフローを使用する必要があるかもしれません。

### OAuth2（ユーザーコンテキスト）

OAuth2はPKCEを使用した認可コードを使用します。以下の環境変数を設定してください：

- `X_OAUTH2_CLIENT_ID`
- `X_OAUTH2_REDIRECT_URI`（アプリのコールバックURLと一致する必要があります）
- `X_OAUTH2_SCOPES`（オプション、デフォルト: `tweet.read users.read offline.access`）
- `X_OAUTH2_CLIENT_SECRET`（オプション、コンフィデンシャルクライアントの場合のみ）

設定ワークフローで設定できます：

```bash
birdapp auth config --oauth2
```

認証してトークンを保存するには：

```bash
birdapp auth login
```

トークンを確認するには：

```bash
birdapp auth whoami
```

開発用フィクスチャのキャプチャ：

```bash
uv run tests/capture_oauth2_fixtures.py
```

## 使い方

### ツイートの投稿

ツイートを投稿するには：

```bash
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
birdapp user elonmusk --format detailed --fields public_metrics created_at
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
