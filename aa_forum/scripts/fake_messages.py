"""
Fake some messages
"""

from faker import Faker

from django.utils import timezone

from aa_forum.models import Boards, Messages, Topics


def run():
    """
    Create some random topics and messages
    """

    fake = Faker()

    # Add some topics
    boards = Boards.objects.all()
    if boards.count() > 0:
        for board in boards:
            time_posted = timezone.now()

            for _ in range(25):
                topic = Topics()
                topic.board = board
                topic.user_started_id = 2
                topic.user_updated_id = 2
                topic.time_modified = time_posted
                topic.subject = fake.sentence()
                topic.save()

                message = Messages()
                message.topic = topic
                message.board = board
                message.time_posted = time_posted
                message.time_modified = time_posted
                message.user_created_id = 2
                message.message = f"<p>{fake.sentence()}</p>"
                message.save()

    # Add some messages to topics
    topics = Topics.objects.all()
    if topics.count() > 0:
        for topic in topics:
            Messages.objects.bulk_create(
                [
                    Messages(
                        message=f"<p>{fake.sentence()}</p>",
                        time_posted=time_posted,
                        time_modified=time_posted,
                        board_id=topic.board_id,
                        topic_id=topic.id,
                        user_created_id=2,
                    )
                    for _ in range(25)
                ]
            )
