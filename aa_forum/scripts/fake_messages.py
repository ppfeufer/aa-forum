"""
Fake some messages
"""

import random

from faker import Faker

from django.contrib.auth.models import User
from django.utils import timezone

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
            time_posted = timezone.now()

            for _ in range(25):
                user_id = random.choice(user_ids)
                topic = Topic()
                topic.board = board
                topic.user_started_id = user_id
                topic.user_updated_id = user_id
                topic.time_modified = time_posted
                topic.subject = fake.sentence()
                topic.save()

                message = Message()
                message.topic = topic
                message.time_posted = time_posted
                message.time_modified = time_posted
                message.user_created_id = user_id
                message.message = f"<p>{fake.sentence()}</p>"
                message.save()

    # Add some messages to topics
    topics = Topic.objects.all()
    if topics.count() > 0:
        for topic in topics:
            user_id = random.choice(user_ids)
            Message.objects.bulk_create(
                [
                    Message(
                        message=f"<p>{fake.sentence()}</p>",
                        time_posted=time_posted,
                        time_modified=time_posted,
                        board_id=topic.board_id,
                        topic_id=topic.id,
                        user_created_id=user_id,
                    )
                    for _ in range(25)
                ]
            )
