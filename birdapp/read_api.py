from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Callable

from .twitterapi_io import request


def _api_param_to_cli(name: str) -> str:
    parts: list[str] = []
    for ch in name:
        if ch.isupper():
            parts.append("-")
            parts.append(ch.lower())
        else:
            parts.append(ch)
    return "".join(parts).replace("_", "-")


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


@dataclass(frozen=True)
class ParamSpec:
    api_name: str
    description: str
    required: bool = False
    param_type: str = "string"
    default: Any | None = None
    choices: tuple[str, ...] | None = None
    multi: bool = False

    @property
    def cli_name(self) -> str:
        return _api_param_to_cli(self.api_name)

    @property
    def dest(self) -> str:
        return self.cli_name.replace("-", "_")


@dataclass(frozen=True)
class EndpointSpec:
    command: str
    path: str
    description: str
    params: tuple[ParamSpec, ...] = ()
    validator: Callable[[dict[str, Any]], list[str]] | None = None


def _param(
    api_name: str,
    description: str,
    *,
    required: bool = False,
    param_type: str = "string",
    default: Any | None = None,
    choices: tuple[str, ...] | None = None,
    multi: bool = False,
) -> ParamSpec:
    return ParamSpec(
        api_name=api_name,
        description=description,
        required=required,
        param_type=param_type,
        default=default,
        choices=choices,
        multi=multi,
    )


def _validate_user_last_tweets(params: dict[str, Any]) -> list[str]:
    if not params.get("userId") and not params.get("userName"):
        return ["user-id または user-name が必要です"]
    return []


READ_ENDPOINTS: tuple[EndpointSpec, ...] = (
    EndpointSpec(
        command="account-my-info",
        path="/oapi/my/info",
        description="現在のAPIキーのアカウント情報を取得",
    ),
    EndpointSpec(
        command="tweet-filter-rules",
        path="/oapi/tweet_filter/get_rules",
        description="全ツイートフィルタールールを取得",
    ),
    EndpointSpec(
        command="monitor-users",
        path="/oapi/x_user_stream/get_user_to_monitor_tweet",
        description="リアルタイムツイート監視対象ユーザーを取得",
    ),
    EndpointSpec(
        command="tweet-article",
        path="/twitter/article",
        description="ツイートIDで記事を取得",
        params=(
            _param("tweet_id", "記事のツイートID", required=True),
        ),
    ),
    EndpointSpec(
        command="community-all-tweets",
        path="/twitter/community/get_tweets_from_all_community",
        description="全コミュニティからツイートを検索",
        params=(
            _param("query", "キーワードクエリ", required=True),
            _param(
                "queryType",
                "クエリタイプ",
                default="Latest",
                choices=("Latest", "Top"),
            ),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="community-info",
        path="/twitter/community/info",
        description="コミュニティ情報を取得",
        params=(
            _param("community_id", "コミュニティID", required=True),
        ),
    ),
    EndpointSpec(
        command="community-members",
        path="/twitter/community/members",
        description="コミュニティメンバーを取得",
        params=(
            _param("community_id", "コミュニティID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="community-moderators",
        path="/twitter/community/moderators",
        description="コミュニティモデレーターを取得",
        params=(
            _param("community_id", "コミュニティID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="community-tweets",
        path="/twitter/community/tweets",
        description="コミュニティツイートを取得",
        params=(
            _param("community_id", "コミュニティID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="dm-history",
        path="/twitter/get_dm_history_by_user_id",
        description="ユーザーとのDM履歴を取得",
        params=(
            _param("login_cookies", "ログインCookie", required=True),
            _param("user_id", "対象ユーザーID", required=True),
            _param("proxy", "プロキシURL"),
        ),
    ),
    EndpointSpec(
        command="account-detail",
        path="/twitter/get_my_x_account_detail_v3",
        description="ログイン中のXアカウント詳細を取得",
        params=(
            _param("user_name", "ユーザー名", required=True),
        ),
    ),
    EndpointSpec(
        command="list-followers",
        path="/twitter/list/followers",
        description="リストのフォロワーを取得",
        params=(
            _param("list_id", "リストID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="list-members",
        path="/twitter/list/members",
        description="リストのメンバーを取得",
        params=(
            _param("list_id", "リストID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="list-tweets",
        path="/twitter/list/tweets",
        description="リストのツイートを取得",
        params=(
            _param("listId", "リストID", required=True),
            _param("sinceTime", "開始時刻（UNIX秒）", param_type="integer"),
            _param("untilTime", "終了時刻（UNIX秒）", param_type="integer"),
            _param("includeReplies", "リプライを含む（true/false）", param_type="boolean"),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="space-detail",
        path="/twitter/spaces/detail",
        description="スペースの詳細を取得",
        params=(
            _param("space_id", "スペースID", required=True),
        ),
    ),
    EndpointSpec(
        command="trends",
        path="/twitter/trends",
        description="WOEIDでトレンドを取得",
        params=(
            _param("woeid", "WOEID", required=True, param_type="integer"),
            _param("count", "トレンド数", param_type="integer"),
        ),
    ),
    EndpointSpec(
        command="tweet-search",
        path="/twitter/tweet/advanced_search",
        description="ツイートの高度な検索",
        params=(
            _param("query", "検索クエリ", required=True),
            _param(
                "queryType",
                "クエリタイプ",
                default="Latest",
                choices=("Latest", "Top"),
            ),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="tweet-quotes",
        path="/twitter/tweet/quotes",
        description="ツイートの引用を取得",
        params=(
            _param("tweetId", "ツイートID", required=True),
            _param("sinceTime", "開始時刻（UNIX秒）", param_type="integer"),
            _param("untilTime", "終了時刻（UNIX秒）", param_type="integer"),
            _param("includeReplies", "リプライを含む（true/false）", param_type="boolean"),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="tweet-replies",
        path="/twitter/tweet/replies",
        description="ツイートのリプライを取得",
        params=(
            _param("tweetId", "ツイートID", required=True),
            _param("sinceTime", "開始時刻（UNIX秒）", param_type="integer"),
            _param("untilTime", "終了時刻（UNIX秒）", param_type="integer"),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="tweet-replies-v2",
        path="/twitter/tweet/replies/v2",
        description="ツイートのリプライを取得（V2）",
        params=(
            _param("tweetId", "ツイートID", required=True),
            _param("cursor", "ページネーションカーソル"),
            _param(
                "queryType",
                "クエリタイプ",
                default="Relevance",
                choices=("Relevance", "Latest", "Likes"),
            ),
        ),
    ),
    EndpointSpec(
        command="tweet-retweeters",
        path="/twitter/tweet/retweeters",
        description="ツイートのリツイートユーザーを取得",
        params=(
            _param("tweetId", "ツイートID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="tweet-thread-context",
        path="/twitter/tweet/thread_context",
        description="ツイートのスレッドコンテキストを取得",
        params=(
            _param("tweetId", "ツイートID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="tweet-by-ids",
        path="/twitter/tweets",
        description="IDでツイートを取得",
        params=(
            _param("tweet_ids", "ツイートID", required=True, param_type="array", multi=True),
        ),
    ),
    EndpointSpec(
        command="user-batch-ids",
        path="/twitter/user/batch_info_by_ids",
        description="IDで複数ユーザーを一括取得",
        params=(
            _param("userIds", "ユーザーID", required=True, multi=True),
        ),
    ),
    EndpointSpec(
        command="user-follow-relationship",
        path="/twitter/user/check_follow_relationship",
        description="フォロー関係を確認",
        params=(
            _param("source_user_name", "元ユーザー名", required=True),
            _param("target_user_name", "対象ユーザー名", required=True),
        ),
    ),
    EndpointSpec(
        command="user-followers",
        path="/twitter/user/followers",
        description="ユーザーのフォロワーを取得",
        params=(
            _param("userName", "ユーザー名", required=True),
            _param("cursor", "ページネーションカーソル"),
            _param("pageSize", "ページサイズ（20-200）", param_type="integer"),
        ),
    ),
    EndpointSpec(
        command="user-followings",
        path="/twitter/user/followings",
        description="ユーザーのフォロー中を取得",
        params=(
            _param("userName", "ユーザー名", required=True),
            _param("cursor", "ページネーションカーソル"),
            _param("pageSize", "ページサイズ（20-200）", param_type="integer"),
        ),
    ),
    EndpointSpec(
        command="user-info",
        path="/twitter/user/info",
        description="ユーザー名でユーザー情報を取得",
        params=(
            _param("userName", "ユーザー名", required=True),
        ),
    ),
    EndpointSpec(
        command="user-last-tweets",
        path="/twitter/user/last_tweets",
        description="ユーザーの最新ツイートを取得",
        params=(
            _param("userId", "ユーザーID"),
            _param("userName", "ユーザー名"),
            _param("cursor", "ページネーションカーソル"),
            _param("includeReplies", "リプライを含む（true/false）", param_type="boolean"),
        ),
        validator=_validate_user_last_tweets,
    ),
    EndpointSpec(
        command="user-mentions",
        path="/twitter/user/mentions",
        description="ユーザーのメンションを取得",
        params=(
            _param("userName", "ユーザー名", required=True),
            _param("sinceTime", "開始時刻（UNIX秒）", param_type="integer"),
            _param("untilTime", "終了時刻（UNIX秒）", param_type="integer"),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="user-search",
        path="/twitter/user/search",
        description="キーワードでユーザーを検索",
        params=(
            _param("query", "検索キーワード", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="user-verified-followers",
        path="/twitter/user/verifiedFollowers",
        description="認証済みフォロワーを取得",
        params=(
            _param("user_id", "ユーザーID", required=True),
            _param("cursor", "ページネーションカーソル"),
        ),
    ),
    EndpointSpec(
        command="user-about",
        path="/twitter/user_about",
        description="ユーザー名でプロフィール概要を取得",
        params=(
            _param("userName", "ユーザー名", required=True),
        ),
    ),
)


def register_read_subcommands(subparsers: argparse._SubParsersAction) -> None:
    for spec in READ_ENDPOINTS:
        parser = subparsers.add_parser(spec.command, help=spec.description)
        for param in spec.params:
            arg_name = f"--{param.cli_name}"
            kwargs: dict[str, Any] = {"help": param.description}
            if param.required:
                kwargs["required"] = True
            if param.default is not None:
                kwargs["default"] = param.default
            if param.param_type == "integer":
                kwargs["type"] = int
            elif param.param_type == "boolean":
                kwargs["choices"] = ("true", "false")
            if param.choices is not None:
                kwargs["choices"] = param.choices
            if param.multi:
                kwargs["nargs"] = "+"
            parser.add_argument(arg_name, dest=param.dest, **kwargs)
        parser.add_argument("--json", action="store_true", help="JSON形式で出力")
        parser.set_defaults(read_spec=spec)


def _normalize_param_value(param: ParamSpec, value: Any) -> Any:
    if value is None:
        return None

    if param.multi:
        if isinstance(value, str):
            values = [item.strip() for item in value.split(",")]
        else:
            values = [str(item).strip() for item in value]
        values = [item for item in values if item]
        return ",".join(values) if values else None

    if param.param_type == "boolean":
        if isinstance(value, bool):
            return value
        return _parse_bool(str(value))

    if param.api_name in {"userName", "source_user_name", "target_user_name", "user_name"}:
        if isinstance(value, str):
            return value.lstrip("@")

    return value


def _validate_required_params(spec: EndpointSpec, params: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for param in spec.params:
        if not param.required:
            continue
        value = params.get(param.api_name)
        if value is None:
            errors.append(f"{param.cli_name} は必須です")
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(f"{param.cli_name} は必須です")
    return errors


def build_read_params(spec: EndpointSpec, args: argparse.Namespace) -> tuple[dict[str, Any], list[str]]:
    params: dict[str, Any] = {}
    for param in spec.params:
        value = getattr(args, param.dest)
        normalized = _normalize_param_value(param, value)
        if normalized is None:
            continue
        params[param.api_name] = normalized

    errors = _validate_required_params(spec, params)
    if spec.validator:
        errors.extend(spec.validator(params))
    return params, errors


def call_read_endpoint(path: str, params: dict[str, Any]) -> tuple[bool, str | dict[str, Any]]:
    try:
        response = request("GET", path, params=params)
        try:
            payload = response.json()
        except ValueError:
            message = response.text.strip() or response.reason
            return False, f"無効なJSONレスポンス: {message}"
        if response.ok:
            status = payload.get("status")
            if status in (None, "success"):
                return True, payload
        message = payload.get("msg") or payload.get("message") or response.reason
        return False, message
    except Exception as exc:
        return False, f"{path} へのリクエストエラー: {exc}"


def execute_read_command(args: argparse.Namespace) -> tuple[bool, str | dict[str, Any]]:
    spec: EndpointSpec | None = getattr(args, "read_spec", None)
    if spec is None:
        return False, "不明なreadコマンドです"
    params, errors = build_read_params(spec, args)
    if errors:
        return False, "; ".join(errors)
    return call_read_endpoint(spec.path, params)
