import argparse
import json

from .tweet import post_tweet, get_tweets_by_ids
from .config import (
    get_credential,
    prompt_for_credentials,
    show_config,
)
from .twitterapi_io import login_user
from .storage.importer import import_archive
from .user import (
    get_user_by_id, get_users_by_ids,
    get_user_by_username, get_users_by_usernames,
)


def _has_required_credentials(keys: tuple[str, ...]) -> bool:
    return all(get_credential(key) for key in keys)


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="TwitterAPI.io CLI - Post tweets from the command line")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Auth subcommand
    auth_parser = subparsers.add_parser("auth", help="Authentication and credential management")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)

    auth_config_parser = auth_subparsers.add_parser("config", help="Configure authentication")
    auth_config_parser.add_argument("--show", action="store_true", help="Show current configuration")

    auth_login_parser = auth_subparsers.add_parser("login", help="Authenticate via TwitterAPI.io login_v2")
    auth_login_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    auth_whoami_parser = auth_subparsers.add_parser("whoami", help="Show configured user info")
    auth_whoami_parser.add_argument("--username", type=str, help="Override username")
    auth_whoami_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    # Tweet subcommand
    tweet_parser = subparsers.add_parser('tweet', help='Post a tweet')
    tweet_parser.add_argument('--text', type=str, help='Tweet text to post (optional if media provided)', default="")
    tweet_parser.add_argument('--media', type=str, help='Path to media file (optional)')
    tweet_parser.add_argument('--reply-to', dest='reply_to', type=str, help='Tweet ID or URL to reply to (optional)')
    
    # Get tweets subcommand
    get_parser = subparsers.add_parser('get', help='Get tweets by ID')
    get_parser.add_argument('ids', nargs='+', help='Tweet IDs to retrieve (space separated)')
    get_parser.add_argument('--json', action='store_true', help='Output raw JSON response')
    get_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple', 
                           help='Output format (simple or detailed)')
    
    # User lookup subcommand
    user_parser = subparsers.add_parser('user', help='Look up user information')
    user_parser.add_argument('identifiers', nargs='+', 
                            help='User IDs or usernames to look up (usernames can have @ prefix)')
    user_parser.add_argument('--by-id', action='store_true', 
                            help='Force lookup by ID (default: auto-detect based on format)')
    user_parser.add_argument('--by-username', action='store_true', 
                            help='Force lookup by username (default: auto-detect based on format)')
    user_parser.add_argument('--json', action='store_true', 
                            help='Output raw JSON response')
    user_parser.add_argument('--format', choices=['simple', 'detailed', 'full'], default='simple',
                            help='Output format (simple, detailed, or full)')

    # Import archive subcommand
    import_parser = subparsers.add_parser(
        'import-archive',
        help='Import a Twitter Community Archive into a SQLite database',
    )
    import_parser.add_argument('--username', type=str, help='Archive username')
    import_parser.add_argument('--url', type=str, help='Full archive.json URL')
    import_parser.add_argument('--path', type=str, help='Path to a local archive.json file')
    import_parser.add_argument(
        '--db',
        type=str,
        default=None,
        help='Database URL (default: ~/.local/share/birdapp/birdapp.db)',
    )
    import_parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for inserts (default: 1000)',
    )
    import_parser.add_argument('--json', action='store_true', help='Output raw JSON result')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle auth command
    if args.command == "auth":
        if args.auth_command == "config":
            if args.show:
                show_config()
            else:
                prompt_for_credentials()
        elif args.auth_command == "login":
            required_keys = (
                "TWITTERAPI_IO_API_KEY",
                "TWITTERAPI_IO_USERNAME",
                "TWITTERAPI_IO_EMAIL",
                "TWITTERAPI_IO_PASSWORD",
                "TWITTERAPI_IO_PROXY",
            )
            if not _has_required_credentials(required_keys):
                print("TwitterAPI.io credentials are not configured. Run `birdapp auth config`.")
                return

            try:
                result = login_user()
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print("✅ Login successful. Login cookie saved.")
            except Exception as e:
                print(f"❌ Error during login: {str(e)}")
        else:
            username = args.username or get_credential("TWITTERAPI_IO_USERNAME")
            if not username:
                print("No username configured. Run `birdapp auth config` or pass --username.")
                return
            try:
                success, result = get_user_by_username(username)
                if not success:
                    print(f"❌ Failed to get user info: {result}")
                elif args.json:
                    print(json.dumps(result, indent=2))
                else:
                    if isinstance(result, dict):
                        format_users_output(result, "full")
                    else:
                        print(f"❌ Failed to get user info: {result}")
            except Exception as e:
                print(f"❌ Error getting user info: {str(e)}")
        return
    
    # Handle tweet command
    if args.command == 'tweet':
        # Validate arguments
        if not args.text.strip() and not args.media:
            print("Error: Cannot post empty tweet without media")
            exit(1)
        
        # Post the tweet
        try:
            success, message = post_tweet(
                text=args.text,
                media_path=args.media,
                reply_to=args.reply_to
            )
            
            if success:
                print(f"✅ Successfully posted tweet: {message}")
            else:
                print(f"❌ Failed to post tweet: {message}")
                
        except Exception as e:
            print(f"❌ Error posting tweet: {str(e)}")
    
    # Handle get command
    if args.command == 'get':
        try:
            success, result = get_tweets_by_ids(args.ids)
            
            if success:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    if isinstance(result, dict):
                        format_tweets_output(result, args.format)
                    else:
                        print(f"❌ Failed to get tweets: {result}")
            else:
                print(f"❌ Failed to get tweets: {result}")
                
        except Exception as e:
            print(f"❌ Error getting tweets: {str(e)}")
    
    # Handle user command
    if args.command == 'user':
        try:
            # Determine if we're looking up by ID or username
            identifiers = args.identifiers
            
            # Auto-detect type if not forced
            if not args.by_id and not args.by_username:
                # Check if all identifiers look like IDs (all digits) or usernames
                all_digits = all(ident.isdigit() for ident in identifiers)
                if all_digits:
                    by_id = True
                else:
                    by_id = False
            else:
                by_id = args.by_id
            
            # Perform the lookup
            if len(identifiers) == 1:
                # Single user lookup
                if by_id:
                    success, result = get_user_by_id(identifiers[0])
                else:
                    success, result = get_user_by_username(identifiers[0])
            else:
                # Multiple users lookup
                if by_id:
                    success, result = get_users_by_ids(identifiers)
                else:
                    success, result = get_users_by_usernames(identifiers)
            
            if success:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    if isinstance(result, dict):
                        format_users_output(result, args.format)
                    else:
                        print(f"❌ Failed to get user(s): {result}")
            else:
                print(f"❌ Failed to get user(s): {result}")
                
        except Exception as e:
            print(f"❌ Error getting user(s): {str(e)}")

    # Handle import-archive command
    if args.command == 'import-archive':
        try:
            username = args.username
            if not username and not args.url and not args.path:
                username = get_credential("TWITTERAPI_IO_USERNAME")
            result = import_archive(
                args.db,
                username=username,
                url=args.url,
                path=args.path,
                batch_size=args.batch_size,
            )
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                total = sum(result.values())
                print(f"✅ Imported {total} rows")
                for key, value in result.items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"❌ Error importing archive: {str(e)}")

def format_tweets_output(data: dict, format_type: str):
    """Format and display tweet data"""
    if 'tweets' not in data:
        print("No tweets found")
        return

    tweets = data['tweets']

    for tweet in tweets:
        author = tweet.get('author', {}) or {}
        if format_type == 'simple':
            print(f"Tweet ID: {tweet.get('id', 'unknown')}")
            print(f"Author: @{author.get('userName', 'unknown')} ({author.get('name', 'Unknown')})")
            print(f"Text: {tweet.get('text', '')}")
            print(f"Created: {tweet.get('createdAt', 'unknown')}")
            print("-" * 50)
        else:  # detailed
            print(f"Tweet ID: {tweet.get('id', 'unknown')}")
            print(f"Author: @{author.get('userName', 'unknown')} ({author.get('name', 'Unknown')})")
            print(f"Text: {tweet.get('text', '')}")
            print(f"Created: {tweet.get('createdAt', 'unknown')}")
            print(f"Language: {tweet.get('lang', 'unknown')}")
            if tweet.get("url"):
                print(f"URL: {tweet.get('url')}")

            print(f"Likes: {tweet.get('likeCount', 0)}")
            print(f"Retweets: {tweet.get('retweetCount', 0)}")
            print(f"Replies: {tweet.get('replyCount', 0)}")
            print(f"Quotes: {tweet.get('quoteCount', 0)}")
            print(f"Views: {tweet.get('viewCount', 0)}")

            if author.get("isBlueVerified"):
                print("✓ Blue verified account")

            print("-" * 50)

def _user_field(user: dict, *keys: str, default: object = None) -> object:
    """Get a field from user dict, trying multiple key names."""
    for key in keys:
        val = user.get(key)
        if val is not None:
            return val
    return default


def format_users_output(data: dict, format_type: str):
    """Format and display user data"""
    if 'users' not in data:
        print("No users found")
        return

    users = data['users']
    if isinstance(users, dict):
        users = [users]

    for user in users:
        username = _user_field(user, 'screen_name', 'userName', default='unknown')
        followers = _user_field(user, 'followers_count', 'followers', default=0)
        following = _user_field(user, 'following_count', 'friends_count', 'following', default=0)
        tweets = _user_field(user, 'statuses_count', 'statusesCount', default=0)
        likes = _user_field(user, 'favourites_count', 'favouritesCount', default=0)
        media = _user_field(user, 'media_tweets_count', 'mediaCount', default=0)
        created = _user_field(user, 'created_at', 'createdAt')
        profile_img = _user_field(user, 'profile_image_url_https', 'profilePicture')
        banner_img = _user_field(user, 'profile_banner_url', 'coverPicture')
        can_dm = _user_field(user, 'can_dm', 'canDm')

        if format_type == 'simple':
            print(f"User ID: {user.get('id', 'unknown')}")
            print(f"Username: @{username}")
            print(f"Name: {user.get('name', 'Unknown')}")
            if user.get('description'):
                print(f"Bio: {user.get('description', '')[:100]}...")
            print("-" * 50)

        elif format_type == 'detailed':
            print(f"User ID: {user.get('id', 'unknown')}")
            print(f"Username: @{username}")
            print(f"Name: {user.get('name', 'Unknown')}")

            if user.get('description'):
                print(f"Bio: {user.get('description')}")

            if created:
                print(f"Joined: {created}")

            if user.get('location'):
                print(f"Location: {user.get('location')}")

            if user.get('url'):
                print(f"Profile URL: {user.get('url')}")

            print(f"Followers: {followers:,}")
            print(f"Following: {following:,}")
            print(f"Tweets: {tweets:,}")
            print(f"Likes: {likes:,}")
            print(f"Media: {media:,}")

            if user.get('isBlueVerified'):
                print("✓ Blue verified account")
            if user.get('verifiedType'):
                print(f"Verified type: {user.get('verifiedType')}")
            if can_dm is True:
                print("✓ DMs enabled")

            print("-" * 50)

        else:  # full
            print("=== User Profile ===")
            print(f"User ID: {user.get('id', 'unknown')}")
            print(f"Username: @{username}")
            print(f"Name: {user.get('name', 'Unknown')}")

            if user.get('description'):
                print(f"\nBio: {user.get('description')}")

            if created:
                print(f"\nAccount created: {created}")

            if user.get('location'):
                print(f"Location: {user.get('location')}")

            if user.get('url'):
                print(f"Profile URL: {user.get('url')}")

            if profile_img:
                print(f"Profile image: {profile_img}")

            if banner_img:
                print(f"Banner image: {banner_img}")

            print("\n=== Metrics ===")
            print(f"Followers: {followers:,}")
            print(f"Following: {following:,}")
            print(f"Tweets: {tweets:,}")
            print(f"Likes: {likes:,}")
            print(f"Media: {media:,}")

            status_items = []
            if user.get('isBlueVerified'):
                status_items.append("✓ Blue verified")
            if user.get('verifiedType'):
                status_items.append(f"Verified type: {user.get('verifiedType')}")
            if can_dm is True:
                status_items.append("DMs enabled")
            if user.get('isTranslator') is True:
                status_items.append("Translator")

            if status_items:
                print("\n=== Account Status ===")
                print(" | ".join(status_items))

            print("=" * 50)

if __name__ == "__main__":
    main()
