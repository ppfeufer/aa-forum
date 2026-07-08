"""
Tests for aa_forum.helper.discord_messages
"""

# Standard Library
from types import SimpleNamespace
from unittest.mock import patch

# AA Forum
from aa_forum import __version__
from aa_forum.app_settings import (
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
    DISCORDPROXY_TIMEOUT,
)
from aa_forum.constants import APP_NAME_VERBOSE_USERAGENT, GITHUB_URL
from aa_forum.helper.discord_messages import (
    _aadiscordbot_send_private_message,
    _dhooks_lite_user_agent,
    _discordproxy_send_private_message,
    send_new_personal_message_notification,
)
from aa_forum.tests import BaseTestCase


class TestDhooksLiteUserAgent(BaseTestCase):
    """
    Test the _dhooks_lite_user_agent helper function to ensure it constructs the UserAgent object correctly and returns it.
    """

    def test_constructor_called_with_expected_values(self):
        """
        Ensure UserAgent is constructed with the expected name, url and version

        :return:
        :rtype:
        """

        with patch("aa_forum.helper.discord_messages.UserAgent") as MockUA:
            ua = _dhooks_lite_user_agent()

            MockUA.assert_called_once_with(
                name=APP_NAME_VERBOSE_USERAGENT, url=GITHUB_URL, version=__version__
            )
            self.assertIs(ua, MockUA.return_value)

    def test_returns_user_agent_instance_when_not_patched(self):
        """
        Ensure the function returns an object (UserAgent instance) when called

        :return:
        :rtype:
        """

        ua = _dhooks_lite_user_agent()

        # We expect some object back; at minimum it should not be None
        self.assertIsNotNone(ua)


class TestAAdiscordbotSendPrivateMessage(BaseTestCase):
    """
    Tests for _aadiscordbot_send_private_message
    """

    def test_sends_embed_when_installed_and_embed_true(self):
        """
        Ensure send_message is called with an embed when embedding is requested

        :return:
        :rtype:
        """

        with patch(
            "aa_forum.helper.discord_messages.allianceauth_discordbot_installed",
            return_value=True,
        ):
            with patch("aadiscordbot.tasks.send_message") as mock_send:
                with patch("discord.Embed") as MockDiscordEmbed:
                    _aadiscordbot_send_private_message(
                        user_id=42,
                        level="info",
                        title="T",
                        message="M",
                        embed_message=True,
                    )

                    MockDiscordEmbed.assert_called_once()
                    mock_send.assert_called_once_with(
                        user_id=42, embed=MockDiscordEmbed.return_value
                    )

    def test_sends_plain_message_when_installed_and_embed_false(self):
        """
        Ensure send_message is called with a plain message when embed_message is False

        :return:
        :rtype:
        """

        with patch(
            "aa_forum.helper.discord_messages.allianceauth_discordbot_installed",
            return_value=True,
        ):
            with patch("aadiscordbot.tasks.send_message") as mock_send:
                with patch("discord.Embed"):
                    _aadiscordbot_send_private_message(
                        user_id=7,
                        level="info",
                        title="Hello",
                        message="Body",
                        embed_message=False,
                    )

                    mock_send.assert_called_once_with(
                        user_id=7, message="**Hello**\n\nBody"
                    )

    def test_logs_when_not_installed(self):
        """
        Ensure a debug log is emitted when allianceauth-discordbot is not available

        :return:
        :rtype:
        """

        with patch(
            "aa_forum.helper.discord_messages.allianceauth_discordbot_installed",
            return_value=False,
        ):
            with patch(
                "aa_forum.helper.discord_messages.logger.debug"
            ) as mock_logger_debug:
                _aadiscordbot_send_private_message(
                    user_id=1, level="info", title="T", message="M"
                )

                self.assertTrue(mock_logger_debug.called)
                called_kwargs = mock_logger_debug.call_args.kwargs
                msg = called_kwargs.get("msg", "")
                self.assertIn("allianceauth-discordbot is not available", str(msg))


class TestDiscordproxySendPrivateMessage(BaseTestCase):
    """
    Tests for _discordproxy_send_private_message
    """

    def test_sends_embed_via_discordproxy_when_embed_true(self):
        """
        Ensure discordproxy client is constructed and embed sent when embed_message is True

        :return:
        :rtype:
        """

        with patch("discordproxy.client.DiscordClient") as MockClient:
            with patch("discordproxy.discord_api_pb2.Embed") as MockEmbed:
                _discordproxy_send_private_message(
                    user_id=10,
                    level="info",
                    title="Hi",
                    message="Body",
                    embed_message=True,
                )

                MockClient.assert_called_once_with(
                    target=f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}",
                    timeout=DISCORDPROXY_TIMEOUT,
                )
                MockClient.return_value.create_direct_message.assert_called_once_with(
                    user_id=10, embed=MockEmbed.return_value
                )

    def test_sends_content_via_discordproxy_when_embed_false(self):
        """
        Ensure discordproxy client sends plain content when embed_message is False

        :return:
        :rtype:
        """

        with patch("discordproxy.client.DiscordClient") as MockClient:
            _discordproxy_send_private_message(
                user_id=11,
                level="info",
                title="Hello",
                message="Text",
                embed_message=False,
            )

            MockClient.return_value.create_direct_message.assert_called_once_with(
                user_id=11, content="**Hello**\n\nText"
            )

    def test_falls_back_to_aadiscordbot_when_discordproxy_raises(self):
        """
        Ensure _aadiscordbot_send_private_message is invoked when discordproxy raises DiscordProxyException

        :return:
        :rtype:
        """

        with patch("discordproxy.client.DiscordClient") as MockClient:
            with patch("discordproxy.exceptions.DiscordProxyException", new=Exception):
                MockClient.return_value.create_direct_message.side_effect = Exception(
                    "boom"
                )

                with patch(
                    "aa_forum.helper.discord_messages._aadiscordbot_send_private_message"
                ) as mock_aadiscord:
                    _discordproxy_send_private_message(
                        user_id=12,
                        level="info",
                        title="T",
                        message="M",
                        embed_message=False,
                    )

                    mock_aadiscord.assert_called_once_with(
                        user_id=12,
                        level="info",
                        title="T",
                        message="M",
                        embed_message=False,
                    )


class TestSendNewPersonalMessageNotification(BaseTestCase):
    """
    Tests for send_new_personal_message_notification
    """

    def test_uses_discordproxy_when_available_and_recipient_opted_in(self):
        """
        Ensure discordproxy path is used when installed and recipient opted-in

        :return:
        :rtype:
        """

        with (
            patch("aa_forum.helper.user.get_user_profile") as mock_get_profile,
            patch("aa_forum.helper.user.get_main_character_from_user") as mock_get_main,
            patch(
                "aa_forum.helper.discord_messages.prepare_message_for_discord",
                return_value="PREP",
            ),
            patch(
                "aa_forum.helper.discord_messages.reverse_absolute", return_value="URL"
            ),
            patch(
                "aa_forum.helper.discord_messages.discordproxy_installed",
                return_value=True,
            ),
            patch(
                "aa_forum.helper.discord_messages._discordproxy_send_private_message"
            ) as mock_proxy,
        ):

            mock_get_profile.return_value = SimpleNamespace(
                discord_dm_on_new_personal_message=True
            )
            mock_get_main.side_effect = ["SenderMain", "RecipientMain"]

            message = SimpleNamespace(
                recipient=SimpleNamespace(discord=SimpleNamespace(uid="999")),
                sender=SimpleNamespace(),
                subject="Subj",
                message="body",
            )

            send_new_personal_message_notification(message=message, embed_message=True)

            mock_proxy.assert_called_once()
            called = mock_proxy.call_args.kwargs
            self.assertEqual(called.get("user_id"), 999)
            self.assertEqual(called.get("level"), "info")
            # title is a fixed DM title; the subject and prepared message are inside the message body
            self.assertIn("Subj", called.get("message"))
            self.assertIn("PREP", called.get("message"))

    def test_falls_back_to_aadiscordbot_when_discordproxy_unavailable(self):
        """
        Ensure aadiscordbot path is used when discordproxy not available

        :return:
        :rtype:
        """

        with (
            patch("aa_forum.helper.user.get_user_profile") as mock_get_profile,
            patch("aa_forum.helper.user.get_main_character_from_user") as mock_get_main,
            patch(
                "aa_forum.helper.discord_messages.prepare_message_for_discord",
                return_value="PREP",
            ),
            patch(
                "aa_forum.helper.discord_messages.reverse_absolute", return_value="URL"
            ),
            patch(
                "aa_forum.helper.discord_messages.discordproxy_installed",
                return_value=False,
            ),
            patch(
                "aa_forum.helper.discord_messages._aadiscordbot_send_private_message"
            ) as mock_aadiscord,
        ):

            mock_get_profile.return_value = SimpleNamespace(
                discord_dm_on_new_personal_message=True
            )
            mock_get_main.side_effect = ["S", "R"]

            message = SimpleNamespace(
                recipient=SimpleNamespace(discord=SimpleNamespace(uid="123")),
                sender=SimpleNamespace(),
                subject="X",
                message="body",
            )

            send_new_personal_message_notification(message=message, embed_message=False)

            mock_aadiscord.assert_called_once()
            called = mock_aadiscord.call_args.kwargs
            self.assertEqual(called.get("user_id"), 123)
            self.assertEqual(called.get("embed_message"), False)

    def test_does_nothing_when_recipient_not_opted_in_or_no_discord(self):
        """
        Ensure no external senders are called when user not opted in or has no discord attr

        :return:
        :rtype:
        """

        with (
            patch("aa_forum.helper.user.get_user_profile") as mock_get_profile,
            patch(
                "aa_forum.helper.discord_messages._aadiscordbot_send_private_message"
            ) as mock_aadiscord,
            patch(
                "aa_forum.helper.discord_messages._discordproxy_send_private_message"
            ) as mock_proxy,
        ):

            # not opted in
            mock_get_profile.return_value = SimpleNamespace(
                discord_dm_on_new_personal_message=False
            )

            message = SimpleNamespace(
                recipient=SimpleNamespace(),
                sender=SimpleNamespace(),
                subject="S",
                message="M",
            )

            send_new_personal_message_notification(message=message)

            self.assertFalse(mock_aadiscord.called)
            self.assertFalse(mock_proxy.called)
