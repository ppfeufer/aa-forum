"""
Generate a bunch of fake topics and messages in existing boards for development.

Shortcuts:
- Topic.objects.all().delete()
- from aa_forum.scripts import fake_messages;fake_messages.run()
"""

# Standard Library
import datetime as dt
import random
from unittest.mock import patch

# Third Party
from faker import Faker

# Django
from django.contrib.auth.models import User
from django.utils.timezone import now

# AA Forum
from aa_forum.models import Board, Message, Topic

MIN_TOPICS_PER_BOARD = 3
MAX_TOPICS_PER_BOARD = 20
MIN_MESSAGES_PER_TOPIC = 2
MAX_MESSAGES_PER_TOPIC = 35
MESSAGE_DATETIME_HOURS_INTO_PAST = 240
MESSAGE_DATETIME_MINUTES_OFFSET = 2
NEW_MESSAGE_DATETIME = now() - dt.timedelta(hours=MESSAGE_DATETIME_HOURS_INTO_PAST)


def message_datetime() -> dt.datetime:
    """
    Return random datetime between now and x hours into the past.
    """

    global MESSAGE_DATETIME_MINUTES_OFFSET

    message_datetime = NEW_MESSAGE_DATETIME + dt.timedelta(
        minutes=MESSAGE_DATETIME_MINUTES_OFFSET
    )

    MESSAGE_DATETIME_MINUTES_OFFSET += 2

    return message_datetime


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
        topics = []

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
            with patch("django.utils.timezone.now", new=message_datetime):
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

                    topic._update_message_references()

            print(f"Updating {len(boards)} boards...")

            for board in boards:
                board._update_message_references()

    print("DONE")
