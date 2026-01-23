import argparse
import json

from .tweet import (
    get_tweet_article,
    get_tweet_quotes,
    get_tweet_replies,
    get_tweet_replies_v2,
    get_tweet_retweeters,
    get_tweet_thread_context,
    get_tweets_by_ids,
    search_tweets_advanced,
)
from .config import (
    get_credential,
    prompt_for_credentials,
    show_config,
)
from .storage.importer import import_archive
from .user import (
    get_user_by_id, get_users_by_ids,
    get_user_by_username, get_users_by_usernames,
)
from .read_api import execute_read_command, register_read_subcommands


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="TwitterAPI.io CLI - Twitterデータの管理とクエリ")
    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド", required=True)

    auth_parser = subparsers.add_parser("auth", help="認証と資格情報の管理")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)

    auth_config_parser = auth_subparsers.add_parser("config", help="認証の設定")
    auth_config_parser.add_argument("--show", action="store_true", help="現在の設定を表示")

    auth_whoami_parser = auth_subparsers.add_parser("whoami", help="設定済みユーザー情報を表示")
    auth_whoami_parser.add_argument("--username", type=str, help="ユーザー名を上書き")
    auth_whoami_parser.add_argument("--json", action="store_true", help="JSON形式で出力")
    
    get_parser = subparsers.add_parser('get', help='IDでツイートを取得')
    get_parser.add_argument('ids', nargs='+', help='取得するツイートID（スペース区切り）')
    get_parser.add_argument('--json', action='store_true', help='JSON形式で出力')
    get_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple',
                           help='出力形式（simple または detailed）')

    tweet_parser = subparsers.add_parser('tweet', help='ツイート関連の取得')
    tweet_subparsers = tweet_parser.add_subparsers(dest='tweet_command', required=True)

    tweet_replies_parser = tweet_subparsers.add_parser('replies', help='ツイートのリプライを取得')
    tweet_replies_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_replies_parser.add_argument('--since-time', type=int, help='開始時刻（UNIX秒）')
    tweet_replies_parser.add_argument('--until-time', type=int, help='終了時刻（UNIX秒）')
    tweet_replies_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_replies_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_replies_v2_parser = tweet_subparsers.add_parser('replies-v2', help='ツイートのリプライを取得（V2）')
    tweet_replies_v2_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_replies_v2_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_replies_v2_parser.add_argument(
        '--query-type',
        default='Relevance',
        choices=['Relevance', 'Latest', 'Likes'],
        help='クエリタイプ',
    )
    tweet_replies_v2_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_quotes_parser = tweet_subparsers.add_parser('quotes', help='ツイートの引用を取得')
    tweet_quotes_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_quotes_parser.add_argument('--since-time', type=int, help='開始時刻（UNIX秒）')
    tweet_quotes_parser.add_argument('--until-time', type=int, help='終了時刻（UNIX秒）')
    tweet_quotes_parser.add_argument('--include-replies', type=_parse_bool, help='リプライを含む（true/false）')
    tweet_quotes_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_quotes_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_retweeters_parser = tweet_subparsers.add_parser('retweeters', help='ツイートのリツイートユーザーを取得')
    tweet_retweeters_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_retweeters_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_retweeters_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_thread_parser = tweet_subparsers.add_parser('thread-context', help='ツイートのスレッド情報を取得')
    tweet_thread_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_thread_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_thread_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_article_parser = tweet_subparsers.add_parser('article', help='ツイートIDから記事を取得')
    tweet_article_parser.add_argument('--tweet-id', required=True, help='ツイートID')
    tweet_article_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    tweet_search_parser = tweet_subparsers.add_parser('search', help='ツイートを高度な検索で取得')
    tweet_search_parser.add_argument('--query', required=True, help='検索クエリ')
    tweet_search_parser.add_argument(
        '--query-type',
        default='Latest',
        choices=['Latest', 'Top'],
        help='クエリタイプ',
    )
    tweet_search_parser.add_argument('--cursor', help='ページネーションカーソル')
    tweet_search_parser.add_argument('--json', action='store_true', help='JSON形式で出力')
    
    user_parser = subparsers.add_parser('user', help='ユーザー情報を検索')
    user_parser.add_argument('identifiers', nargs='+',
                            help='検索するユーザーIDまたはユーザー名（@付き可）')
    user_parser.add_argument('--by-id', action='store_true',
                            help='IDで検索（デフォルト: 形式から自動判定）')
    user_parser.add_argument('--by-username', action='store_true',
                            help='ユーザー名で検索（デフォルト: 形式から自動判定）')
    user_parser.add_argument('--json', action='store_true',
                            help='JSON形式で出力')
    user_parser.add_argument('--format', choices=['simple', 'detailed', 'full'], default='simple',
                            help='出力形式（simple, detailed, full）')

    import_parser = subparsers.add_parser(
        'import-archive',
        help='Twitter Community ArchiveをSQLiteデータベースにインポート',
    )
    import_parser.add_argument('--username', type=str, help='アーカイブのユーザー名')
    import_parser.add_argument('--url', type=str, help='archive.jsonの完全なURL')
    import_parser.add_argument('--path', type=str, help='ローカルのarchive.jsonファイルパス')
    import_parser.add_argument(
        '--db',
        type=str,
        default=None,
        help='データベースURL（デフォルト: ~/.local/share/birdapp/birdapp.db）',
    )
    import_parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='一括挿入のバッチサイズ（デフォルト: 1000）',
    )
    import_parser.add_argument('--json', action='store_true', help='JSON形式で出力')

    read_parser = subparsers.add_parser('read', help='TwitterAPI.io GETエンドポイントでデータを取得')
    read_subparsers = read_parser.add_subparsers(dest='read_command', required=True)
    register_read_subcommands(read_subparsers)
    
    args = parser.parse_args()
    
    if args.command == "auth":
        if args.auth_command == "config":
            if args.show:
                show_config()
            else:
                prompt_for_credentials()
        elif args.auth_command == "whoami":
            username = args.username or get_credential("TWITTERAPI_IO_USERNAME")
            if not username:
                print("ユーザー名が未設定です。`birdapp auth config` を実行するか --username を指定してください。")
                return
            try:
                success, result = get_user_by_username(username)
                if not success:
                    print(f"❌ ユーザー情報の取得に失敗: {result}")
                elif args.json:
                    print(json.dumps(result, indent=2))
                else:
                    if isinstance(result, dict):
                        format_users_output(result, "full")
                    else:
                        print(f"❌ ユーザー情報の取得に失敗: {result}")
            except Exception as e:
                print(f"❌ ユーザー情報取得エラー: {str(e)}")
        else:
            print("不明な認証コマンドです")
        return
    
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
                        print(f"❌ ツイートの取得に失敗: {result}")
            else:
                print(f"❌ ツイートの取得に失敗: {result}")
                
        except Exception as e:
            print(f"❌ ツイート取得エラー: {str(e)}")

    if args.command == 'tweet':
        try:
            if args.tweet_command == 'replies':
                success, result = get_tweet_replies(
                    args.tweet_id,
                    since_time=args.since_time,
                    until_time=args.until_time,
                    cursor=args.cursor,
                )
            elif args.tweet_command == 'replies-v2':
                success, result = get_tweet_replies_v2(
                    args.tweet_id,
                    cursor=args.cursor,
                    query_type=args.query_type,
                )
            elif args.tweet_command == 'quotes':
                success, result = get_tweet_quotes(
                    args.tweet_id,
                    since_time=args.since_time,
                    until_time=args.until_time,
                    include_replies=args.include_replies,
                    cursor=args.cursor,
                )
            elif args.tweet_command == 'retweeters':
                success, result = get_tweet_retweeters(args.tweet_id, cursor=args.cursor)
            elif args.tweet_command == 'thread-context':
                success, result = get_tweet_thread_context(args.tweet_id, cursor=args.cursor)
            elif args.tweet_command == 'article':
                success, result = get_tweet_article(args.tweet_id)
            elif args.tweet_command == 'search':
                success, result = search_tweets_advanced(
                    args.query,
                    query_type=args.query_type,
                    cursor=args.cursor,
                )
            else:
                print("不明なツイートコマンドです")
                return

            if success:
                if args.json:
                    print(json.dumps(result))
                else:
                    print(json.dumps(result, indent=2))
            else:
                print(f"❌ ツイート取得に失敗: {result}")
        except Exception as e:
            print(f"❌ ツイート取得エラー: {str(e)}")

    if args.command == 'user':
        try:
            identifiers = args.identifiers
            if args.by_id or args.by_username:
                by_id = args.by_id
            else:
                by_id = all(ident.isdigit() for ident in identifiers)

            if len(identifiers) == 1:
                if by_id:
                    success, result = get_user_by_id(identifiers[0])
                else:
                    success, result = get_user_by_username(identifiers[0])
            else:
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
                        print(f"❌ ユーザーの取得に失敗: {result}")
            else:
                print(f"❌ ユーザーの取得に失敗: {result}")
                
        except Exception as e:
            print(f"❌ ユーザー取得エラー: {str(e)}")

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
                print(f"✅ {total} 件インポートしました")
                for key, value in result.items():
                    print(f"{key}: {value}")
        except Exception as e:
            print(f"❌ アーカイブインポートエラー: {str(e)}")

    if args.command == 'read':
        try:
            success, result = execute_read_command(args)
            if success:
                if args.json:
                    print(json.dumps(result))
                else:
                    print(json.dumps(result, indent=2))
            else:
                print(f"❌ データの取得に失敗: {result}")
        except Exception as e:
            print(f"❌ データ取得エラー: {str(e)}")

def format_tweets_output(data: dict, format_type: str):
    """Format and display tweet data"""
    if 'tweets' not in data:
        print("ツイートが見つかりません")
        return

    tweets = data['tweets']

    for tweet in tweets:
        author = tweet.get('author', {}) or {}
        print(f"ツイートID: {tweet.get('id', '不明')}")
        print(f"投稿者: @{author.get('userName', '不明')} ({author.get('name', '不明')})")
        print(f"本文: {tweet.get('text', '')}")
        print(f"投稿日時: {tweet.get('createdAt', '不明')}")

        if format_type == 'detailed':
            print(f"言語: {tweet.get('lang', '不明')}")
            if tweet.get("url"):
                print(f"URL: {tweet.get('url')}")
            print(f"いいね: {tweet.get('likeCount', 0)}")
            print(f"リツイート: {tweet.get('retweetCount', 0)}")
            print(f"リプライ: {tweet.get('replyCount', 0)}")
            print(f"引用: {tweet.get('quoteCount', 0)}")
            print(f"表示回数: {tweet.get('viewCount', 0)}")
            if author.get("isBlueVerified"):
                print("✓ Blue認証済みアカウント")

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
        print("ユーザーが見つかりません")
        return

    users = data['users']
    if isinstance(users, dict):
        users = [users]

    for user in users:
        username = _user_field(user, 'screen_name', 'userName', default='不明')
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
            print(f"ユーザーID: {user.get('id', '不明')}")
            print(f"ユーザー名: @{username}")
            print(f"表示名: {user.get('name', '不明')}")
            if user.get('description'):
                print(f"自己紹介: {user.get('description', '')[:100]}...")
            print("-" * 50)

        elif format_type == 'detailed':
            print(f"ユーザーID: {user.get('id', '不明')}")
            print(f"ユーザー名: @{username}")
            print(f"表示名: {user.get('name', '不明')}")

            if user.get('description'):
                print(f"自己紹介: {user.get('description')}")

            if created:
                print(f"登録日: {created}")

            if user.get('location'):
                print(f"場所: {user.get('location')}")

            if user.get('url'):
                print(f"プロフィールURL: {user.get('url')}")

            print(f"フォロワー: {followers:,}")
            print(f"フォロー中: {following:,}")
            print(f"ツイート数: {tweets:,}")
            print(f"いいね数: {likes:,}")
            print(f"メディア数: {media:,}")

            if user.get('isBlueVerified'):
                print("✓ Blue認証済みアカウント")
            if user.get('verifiedType'):
                print(f"認証種別: {user.get('verifiedType')}")
            if can_dm is True:
                print("✓ DM受付中")

            print("-" * 50)

        else:  # full
            print("=== ユーザープロフィール ===")
            print(f"ユーザーID: {user.get('id', '不明')}")
            print(f"ユーザー名: @{username}")
            print(f"表示名: {user.get('name', '不明')}")

            if user.get('description'):
                print(f"\n自己紹介: {user.get('description')}")

            if created:
                print(f"\nアカウント作成日: {created}")

            if user.get('location'):
                print(f"場所: {user.get('location')}")

            if user.get('url'):
                print(f"プロフィールURL: {user.get('url')}")

            if profile_img:
                print(f"プロフィール画像: {profile_img}")

            if banner_img:
                print(f"バナー画像: {banner_img}")

            print("\n=== 統計情報 ===")
            print(f"フォロワー: {followers:,}")
            print(f"フォロー中: {following:,}")
            print(f"ツイート数: {tweets:,}")
            print(f"いいね数: {likes:,}")
            print(f"メディア数: {media:,}")

            status_items = []
            if user.get('isBlueVerified'):
                status_items.append("✓ Blue認証済み")
            if user.get('verifiedType'):
                status_items.append(f"認証種別: {user.get('verifiedType')}")
            if can_dm is True:
                status_items.append("DM受付中")
            if user.get('isTranslator') is True:
                status_items.append("翻訳者")

            if status_items:
                print("\n=== アカウントステータス ===")
                print(" | ".join(status_items))

            print("=" * 50)

if __name__ == "__main__":
    main()
