"""
Fake some messages
"""

from faker import Faker

from aa_forum.models import Messages


def run():
    """
    Create some random messages for topic id 1
    """

    fake = Faker()

    Messages.objects.bulk_create(
        [
            Messages(message=fake.sentence(), board_id=1, topic_id=1, user_created_id=2)
            for _ in range(100)
        ]
    )
