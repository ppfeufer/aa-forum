"""Generate a bunch of fake topics and messages in existing boards for development.

shortcuts:
- Topic.objects.all().delete()
- from aa_forum.scripts import fake_messages;fake_messages.run()
"""

import datetime as dt
import random
from unittest.mock import patch

from faker import Faker

from django.contrib.auth.models import User
from django.utils.timezone import now

from aa_forum.models import Board, Message, Topic

MAX_MESSAGE_HOURS_INTO_PAST = 1000
MIN_TOPICS_PER_BOARD = 3
MAX_TOPICS_PER_BOARD = 25
MIN_MESSAGES_PER_TOPIC = 2
MAX_MESSAGES_PER_TOPIC = 25


def random_dt() -> dt.datetime:
    """Return random datetime between now and x hours into the past."""
    return now() - dt.timedelta(
        hours=random.randint(0, MAX_MESSAGE_HOURS_INTO_PAST),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


def run():
    """
    Create some random topics and messages
    """

    fake = Faker()
    user_ids = list(User.objects.values_list("id", flat=True))

    # Add some topics
    boards = Board.objects.all()
    print(boards)
    if boards.count() > 0:
        topics = list()
        for board in boards:
            for _ in range(
                random.randrange(MIN_TOPICS_PER_BOARD, MAX_TOPICS_PER_BOARD)
            ):
                # can not bulk create, or we would not get slugs
                topics.append(
                    Topic.objects.create(board=board, subject=fake.sentence())
                )

        # Add some messages to topics
        if topics:
            with patch("django.utils.timezone.now", new=random_dt):
                for topic in topics:
                    for _ in range(
                        random.randrange(MIN_MESSAGES_PER_TOPIC, MAX_MESSAGES_PER_TOPIC)
                    ):
                        # can not bulk create, or we would not get first and last messages
                        Message.objects.create(
                            topic_id=topic.id,
                            message=f"<p>{fake.sentence()}</p>",
                            user_created_id=random.choice(user_ids),
                        )
