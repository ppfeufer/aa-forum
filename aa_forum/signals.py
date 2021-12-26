"""
Our signals
"""

# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# AA Forum
from aa_forum.models import Board


@receiver(post_save, sender=Board)
def sync_parent_board_access_to_child_board(sender, instance, **kwargs):
    """
    Keeps the access restrictions in sync between parent boards and their children
    """

    if instance.parent_board:
        parent_board = Board.objects.get(pk=instance.parent_board.pk)

        instance.groups.set(parent_board.groups.all())
    else:
        child_boards = instance.child_boards.all()

        for child_board in child_boards:
            child_board.groups.set(instance.groups.all())
