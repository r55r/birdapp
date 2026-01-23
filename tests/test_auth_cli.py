import sys
import unittest
from unittest import mock

from birdapp import main as main_module


class TestAuthCli(unittest.TestCase):
    def test_auth_config_calls_prompt(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "config"]),
            mock.patch("birdapp.main.prompt_for_credentials") as prompt_for_credentials,
        ):
            main_module.main()

        prompt_for_credentials.assert_called_once()

    def test_auth_config_show_calls_show_config(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "config", "--show"]),
            mock.patch("birdapp.main.show_config") as show_config,
        ):
            main_module.main()

        show_config.assert_called_once()

    def test_auth_login_requires_config(self) -> None:
        def fake_get_credential(_: str) -> str | None:
            return None

        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.login_user") as login_user,
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        login_user.assert_not_called()
        printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn("TwitterAPI.io credentials are not configured", printed)

    def test_auth_login_runs_login(self) -> None:
        def fake_get_credential(key: str) -> str | None:
            required = {
                "TWITTERAPI_IO_API_KEY",
                "TWITTERAPI_IO_USERNAME",
                "TWITTERAPI_IO_EMAIL",
                "TWITTERAPI_IO_PASSWORD",
                "TWITTERAPI_IO_PROXY",
            }
            if key in required:
                return "value"
            return None

        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.login_user", return_value={"status": "success"}) as login_user,
        ):
            main_module.main()

        login_user.assert_called_once()

    def test_auth_whoami_calls_user_lookup(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "whoami"]),
            mock.patch("birdapp.main.get_credential", return_value="example"),
            mock.patch(
                "birdapp.main.get_user_by_username",
                return_value=(True, {"users": [{"id": "1", "userName": "example", "name": "Example"}]}),
            ) as get_user_by_username,
            mock.patch("birdapp.main.format_users_output") as format_users_output,
        ):
            main_module.main()

        get_user_by_username.assert_called_once()
        format_users_output.assert_called_once()
