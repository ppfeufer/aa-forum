from ..models import Message


def create_message(**kwargs):
    if "message" not in kwargs:
        kwargs["message"] = "dummy text"
    return Message.objects.create(**kwargs)
