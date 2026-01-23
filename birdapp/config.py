from __future__ import annotations

import getpass
import json
import os
from pathlib import Path

def get_config_path() -> Path:
    """Get the path to the user-level config file."""
    config_dir = Path.home() / ".config" / "birdapp"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> dict[str, str]:
    """Load configuration from the user-level config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(config: dict[str, str]) -> None:
    """Save configuration to the user-level config file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions (read/write for owner only)
        os.chmod(config_path, 0o600)
    except IOError as e:
        raise RuntimeError(f"Failed to save config: {e}")

def get_credential(key: str) -> str | None:
    """Get a credential from the environment or config file."""
    return os.getenv(key) or load_config().get(key)

def prompt_for_credentials() -> None:
    """Prompt user for TwitterAPI.io credentials and save them."""
    print("TwitterAPI.io CLI 設定")
    print("=====================")
    print("TwitterAPI.ioの認証情報を入力してください。")
    print("APIキーは https://twitterapi.io/ から取得できます。")
    print("（機密フィールドは入力時に非表示になります）")
    print()

    credentials = load_config()

    credentials["TWITTERAPI_IO_API_KEY"] = getpass.getpass("APIキー: ").strip()
    username = input("ユーザー名（任意、@なし）: ").strip()
    if username:
        credentials["TWITTERAPI_IO_USERNAME"] = username

    if not credentials.get("TWITTERAPI_IO_API_KEY"):
        print("\nエラー: 必須フィールドが未入力です: TWITTERAPI_IO_API_KEY")
        return

    try:
        save_config(credentials)
        config_path = get_config_path()
        print(f"\n✅ 設定を保存しました: {config_path}")
    except RuntimeError as e:
        print(f"\n❌ {e}")

def show_config() -> None:
    """Show current configuration (without secrets)."""
    config = load_config()
    if not config:
        print("設定が見つかりません。`birdapp auth config` を実行して認証情報を設定してください。")
        return

    print("現在の設定:")
    print("  APIキー: " + ("設定済み" if config.get("TWITTERAPI_IO_API_KEY") else "未設定"))
    print("  ユーザー名: " + (config.get("TWITTERAPI_IO_USERNAME") or "未設定"))
