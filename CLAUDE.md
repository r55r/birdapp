## 概要

日本語で応答して下さい。

Birdappは、TwitterAPI.ioを使ってツイートの投稿や管理を行うCLIです。

関連スクリプト:
- `birdapp/main.py` (CLIエントリポイント)
- `birdapp/__main__.py` (python -m 実行入口)
- `birdapp/twitterapi_io.py` (TwitterAPI.io APIクライアント)
- `birdapp/tweet.py` (ツイート操作)
- `birdapp/media.py` (メディアアップロード)
- `birdapp/user.py` (ユーザー検索)
- `birdapp/storage/importer.py` (アーカイブ取り込み)
- `tests/` (pytestテスト)

## 開発セットアップ

このリポジトリは依存管理に `uv` を使用します。

```bash
uv sync --dev
```

## CLIの実行

```bash
uv run birdapp --help
```

## 検証 (Pythonエラーチェック)

編集後は以下を実行してください。

```bash
uv run python -m compileall birdapp tests
uv run ruff check .
uv run ty check birdapp
uv run pytest
```

特定ファイルだけを編集した場合は、範囲を絞って実行できます。

```bash
uv run ruff check birdapp/path/to_file.py
uv run ty check birdapp/path/to_file.py
uv run pytest tests/test_auth_cli.py
```

また、編集後はcode simpliferエージェントでコードをリファクタして下さい。
認証情報をコミットに含めないでください。