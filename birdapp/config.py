import os
import json
import getpass
from pathlib import Path
from typing import Dict, Optional

def get_config_path() -> Path:
    """Get the path to the user-level config file."""
    config_dir = Path.home() / ".config" / "birdapp"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Dict[str, str]:
    """Load configuration from the user-level config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(config: Dict[str, str]) -> None:
    """Save configuration to the user-level config file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions (read/write for owner only)
        os.chmod(config_path, 0o600)
    except IOError as e:
        raise RuntimeError(f"Failed to save config: {e}")

def get_credential(key: str) -> Optional[str]:
    """Get a credential from the environment or config file."""
    return os.getenv(key) or load_config().get(key)

def prompt_for_credentials() -> None:
    """Prompt user for TwitterAPI.io credentials and save them."""
    print("TwitterAPI.io CLI Configuration")
    print("===============================")
    print("Please enter your TwitterAPI.io credentials.")
    print("You can get the API key from https://twitterapi.io/")
    print("(Sensitive fields will be hidden as you type)")
    print()

    credentials = load_config()

    credentials["TWITTERAPI_IO_API_KEY"] = getpass.getpass("API Key: ").strip()
    credentials["TWITTERAPI_IO_PROXY"] = getpass.getpass("Proxy (required): ").strip()
    credentials["TWITTERAPI_IO_USERNAME"] = input("Username (without @): ").strip()
    credentials["TWITTERAPI_IO_EMAIL"] = input("Email: ").strip()
    credentials["TWITTERAPI_IO_PASSWORD"] = getpass.getpass("Password: ").strip()
    totp_secret = getpass.getpass("TOTP Secret (optional): ").strip()
    if totp_secret:
        credentials["TWITTERAPI_IO_TOTP_SECRET"] = totp_secret

    required_keys = (
        "TWITTERAPI_IO_API_KEY",
        "TWITTERAPI_IO_PROXY",
        "TWITTERAPI_IO_USERNAME",
        "TWITTERAPI_IO_EMAIL",
        "TWITTERAPI_IO_PASSWORD",
    )
    missing = [key for key in required_keys if not credentials.get(key)]
    if missing:
        print(f"\nError: Missing required fields: {', '.join(missing)}")
        return

    try:
        save_config(credentials)
        config_path = get_config_path()
        print(f"\n✅ Configuration saved to {config_path}")
        print("Next, run `birdapp auth login` to obtain a login cookie.")
    except RuntimeError as e:
        print(f"\n❌ {e}")

def show_config() -> None:
    """Show current configuration (without secrets)."""
    config = load_config()
    if not config:
        print("No configuration found. Run `birdapp auth config` to set up credentials.")
        return

    print("Current configuration:")
    print("  API Key: " + ("Set" if config.get("TWITTERAPI_IO_API_KEY") else "Not set"))
    print("  Proxy: " + ("Set" if config.get("TWITTERAPI_IO_PROXY") else "Not set"))
    print("  Username: " + (config.get("TWITTERAPI_IO_USERNAME") or "Not set"))
    print("  Email: " + ("Set" if config.get("TWITTERAPI_IO_EMAIL") else "Not set"))
    print("  Password: " + ("Set" if config.get("TWITTERAPI_IO_PASSWORD") else "Not set"))
    print("  TOTP Secret: " + ("Set" if config.get("TWITTERAPI_IO_TOTP_SECRET") else "Not set"))
    print("  Login Cookie: " + ("Set" if config.get("TWITTERAPI_IO_LOGIN_COOKIE") else "Not set"))
