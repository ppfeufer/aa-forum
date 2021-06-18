"""
Fake some messages

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


def run():
    """
    Create some random topics and messages
    """

    fake = Faker()
    user_ids = list(User.objects.values_list("id", flat=True))

    # Add some topics
    boards = Board.objects.all()
    if boards.count() > 0:
        for board in boards:
            for _ in range(25):
                topic = Topic()
                topic.board = board
                topic.subject = fake.sentence()
                topic.save()

                message = Message()
                message.topic = topic
                message.user_created_id = random.choice(user_ids)
                message.message = f"<p>{fake.sentence()}</p>"
                my_now = now() - dt.timedelta(
                    hours=random.randint(0, 1000), minutes=random.randint(0, 59)
                )
                with patch("django.utils.timezone.now", lambda: my_now):
                    message.save()

    # Add some messages to topics
    topics = Topic.objects.all()
    if topics.count() > 0:
        for topic in topics:
            for _ in range(25):
                my_now = now() - dt.timedelta(
                    hours=random.randint(0, 1000), minutes=random.randint(0, 59)
                )
                with patch("django.utils.timezone.now", lambda: my_now):
                    Message.objects.create(
                        topic_id=topic.id,
                        message=f"<p>{fake.sentence()}</p>",
                        user_created_id=random.choice(user_ids),
                    )
