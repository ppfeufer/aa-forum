"""
Fake some messages
"""

from faker import Faker

from django.utils import timezone

from aa_forum.models import Messages, Topics


def run():
    """
    Create some random messages for topic id 1
    """

    fake = Faker()

    topics = Topics.objects.all()
    time_posted = timezone.now()

    if topics.count() > 0:
        for topic in topics:
            Messages.objects.bulk_create(
                [
                    Messages(
                        message=fake.sentence(),
                        time_posted=time_posted,
                        time_modified=time_posted,
                        board_id=topic.board_id,
                        topic_id=topic.id,
                        user_created_id=2,
                    )
                    for _ in range(25)
                ]
            )
