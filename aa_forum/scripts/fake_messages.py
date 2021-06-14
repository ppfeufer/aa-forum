"""
Fake some messages
"""

import random

from faker import Faker

from django.contrib.auth.models import User
from django.utils import timezone

from aa_forum.models import Boards, Messages, Topics


def run():
    """
    Create some random topics and messages
    """

    fake = Faker()
    user_ids = list(User.objects.values_list("id", flat=True))

    # Add some topics
    boards = Boards.objects.all()
    if boards.count() > 0:
        for board in boards:
            time_posted = timezone.now()

            for _ in range(25):
                user_id = random.choice(user_ids)
                topic = Topics()
                topic.board = board
                topic.user_started_id = user_id
                topic.user_updated_id = user_id
                topic.time_modified = time_posted
                topic.subject = fake.sentence()
                topic.save()

                message = Messages()
                message.topic = topic
                message.board = board
                message.time_posted = time_posted
                message.time_modified = time_posted
                message.user_created_id = user_id
                message.message = f"<p>{fake.sentence()}</p>"
                message.save()

    # Add some messages to topics
    topics = Topics.objects.all()
    if topics.count() > 0:
        for topic in topics:
            user_id = random.choice(user_ids)
            Messages.objects.bulk_create(
                [
                    Messages(
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
