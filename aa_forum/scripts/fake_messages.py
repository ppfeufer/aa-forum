"""
Generate a bunch of fake topics and messages in existing boards for development.

Shortcuts:
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
MAX_TOPICS_PER_BOARD = 20
MIN_MESSAGES_PER_TOPIC = 2
MAX_MESSAGES_PER_TOPIC = 35


def random_dt() -> dt.datetime:
    """
    Return random datetime between now and x hours into the past.
    """

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
    board_count = boards.count()
    if board_count > 0:
        topics = list()
        for num, board in enumerate(boards):
            print(f"Generating topics for board {num + 1} / {board_count}")
            for _ in range(
                random.randrange(MIN_TOPICS_PER_BOARD, MAX_TOPICS_PER_BOARD)
            ):
                # Can not bulk create, or we would not get slugs
                topics.append(
                    Topic.objects.create(board=board, subject=fake.sentence())
                )

        # Add some messages to topics
        if topics:
            with patch("django.utils.timezone.now", new=random_dt):
                for num, topic in enumerate(topics):
                    print(f"Generating messages for topic {num + 1} / {len(topics)}")
                    for _ in range(
                        random.randrange(MIN_MESSAGES_PER_TOPIC, MAX_MESSAGES_PER_TOPIC)
                    ):
                        # Can not bulk create, or we would not get first and last
                        # messages
                        Message.objects.create(
                            topic_id=topic.id,
                            message=f"<p>{fake.sentence()}</p>",
                            user_created_id=random.choice(user_ids),
                        )
                    topic.update_last_message()
            print(f"Updating {len(boards)} boards...")
            for board in boards:
                board.update_last_message()

    print("DONE")
