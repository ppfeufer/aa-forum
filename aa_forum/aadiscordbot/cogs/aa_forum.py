"""
AA-Forum cog for `allianceauth-discordbot`
https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import urllib.parse
from functools import reduce
from operator import or_

# Third Party
from aadiscordbot.app_settings import get_site_url
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

# Alliance Auth
from allianceauth.services.modules.discord.models import DiscordUser

# AA Forum
from aa_forum.constants import SEARCH_STOPWORDS
from aa_forum.models import Board, Message


class AaForum(commands.Cog):
    """
    A series of Time tools
    """

    @classmethod
    def show_search_results(cls, auth_user: User, search_term: str = None):
        """
        Return search results for the users search term
        :return:
        """

        embed = Embed(title="Forum Search")
        embed.colour = Color.blue()

        search_params = {"q": search_term}
        forum_search_url = (
            get_site_url()
            + reverse("aa_forum:search_results")
            + "?"
            + urllib.parse.urlencode(search_params)
        )

        querywords = search_term.split()
        search_phrase_terms = [
            word for word in querywords if word.lower() not in SEARCH_STOPWORDS
        ]

        boards = (
            Board.objects.user_has_access(auth_user)
            .distinct()
            .values_list("pk", flat=True)
        )

        search_results = (
            Message.objects.filter(
                reduce(
                    or_,
                    [
                        Q(message_plaintext__icontains=search_term)
                        for search_term in search_phrase_terms
                    ],
                ),
                topic__board__pk__in=boards,
            )
            .select_related(
                "user_created",
                "user_created__profile__main_character",
                "topic",
                "topic__first_message",
                "topic__board",
                "topic__board__category",
            )
            .order_by("-time_modified")
            .distinct()[:5]
        )

        if search_results.count() == 0:
            embed.add_field(
                name="Search Results",
                value="Nothing fount for your search phrase.",
                inline=False,
            )
        else:
            post_content = "\n"

            for forum_post in search_results:
                message_link = get_site_url() + reverse(
                    "aa_forum:forum_message",
                    kwargs={
                        "category_slug": forum_post.topic.board.category.slug,
                        "board_slug": forum_post.topic.board.slug,
                        "topic_slug": forum_post.topic.slug,
                        "message_id": forum_post.pk,
                    },
                )

                message_excerpt = forum_post.excerpt(50)

                post_content += (
                    f"**[{forum_post.topic.subject}]({message_link})**\n"
                    f"{message_excerpt}\n\n"
                )

            post_content += f"\n**All search results:** {forum_search_url}"

            embed.add_field(
                name=f'Search Results for "{search_term}"',
                value=post_content,
                inline=False,
            )

        return embed

    @commands.slash_command(
        name="forum_search",
        guild_ids=[int(settings.DISCORD_GUILD_ID)],
        pass_context=True,
    )
    async def forum_search_slash(self, ctx, *, search_term: str = None):
        """
        Returns search results from the forum
        :param ctx:
        :param search_term:
        :return:
        """

        await ctx.trigger_typing()

        if search_term is None:
            return await ctx.respond("You need to pass a search term to me :-)")

        try:
            discord_user = ctx.author.id
            discord_user_object = DiscordUser.objects.filter(uid=discord_user).get()
            auth_user = discord_user_object.user
        except DiscordUser.DoesNotExist:
            return await ctx.respond("You don't seem to have access to our forum!")
        else:
            return await ctx.respond(
                embed=self.show_search_results(
                    auth_user=auth_user, search_term=search_term
                )
            )


def setup(bot):
    """
    Set up the cog
    :param bot:
    """

    if bot.get_cog("AaForum") is None:
        # Load our `time` extension
        bot.add_cog(AaForum(bot))
