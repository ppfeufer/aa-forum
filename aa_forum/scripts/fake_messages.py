"""
Fake some messages
"""

import random

from faker import Faker

from django.contrib.auth.models import User

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
                message.save()

    # Add some messages to topics
    topics = Topic.objects.all()
    if topics.count() > 0:
        for topic in topics:
            Message.objects.bulk_create(
                [
                    Message(
                        message=f"<p>{fake.sentence()}</p>",
                        topic_id=topic.id,
                        user_created_id=random.choice(user_ids),
                    )
                    for _ in range(25)
                ]
            )
