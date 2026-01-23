# Birdapp: TwitterAPI.io CLIツール

コマンドラインからTwitter/Xのツイート取得やユーザー検索、アーカイブ取り込みを行うツールです（TwitterAPI.ioを利用）。

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
birdapp get 1234567890
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

任意:
- Username（auth whoami の既定値）

環境変数で上書き可能:
- `TWITTERAPI_IO_API_KEY`
- `TWITTERAPI_IO_USERNAME`

現在の設定を確認するには（シークレットは表示されません）：

```bash
birdapp auth config --show
```

## 使い方

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

### 取得系エンドポイント（read コマンド）

TwitterAPI.io の GET エンドポイントをまとめて利用できます。全サブコマンドは以下で確認してください：

```bash
birdapp read --help
```

例：

```bash
birdapp read tweet-search --query "AI" --query-type Latest
birdapp read tweet-replies --tweet-id 1846987139428634858
birdapp read user-followers --user-name nasa
birdapp read list-tweets --list-id 1846987139428634858
birdapp read community-info --community-id 1234567890
birdapp read space-detail --space-id 1OdKrBxyz
birdapp read trends --woeid 23424856 --count 30
```

`--json` を指定するとコンパクトな JSON を出力します。

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
birdapp auth --help
birdapp get --help
birdapp user --help
birdapp import-archive --help
```
