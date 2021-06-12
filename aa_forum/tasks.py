"""
We need some tasks, so here we are ...
"""

from celery import shared_task

from django.contrib.auth.models import User

# from django.core import serializers
# from django.core.paginator import Page

# from aa_forum.models import Messages


@shared_task
def set_messages_read_by_user_in_pagination(object_list, user_id: int):
    """
    Set messages read by user in a pagination context
    :param page_object:
    :type page_object:
    :param user:
    :type user:
    """

    # MessagesReadByUsers = Messages.read_by.through
    # MessagesReadByUsers.objects.bulk_create(
    #     [
    #         MessagesReadByUsers(messages_id=pk, user=user)
    #         for pk in page_object.object_list.values_list("pk", flat=True)
    #     ]
    # )

    user = User.objects.get(pk=user_id)

    # user.aa_forum_read_messages.add(*serializers.deserialize("json", object_list))
    user.aa_forum_read_messages.add(*object_list)
