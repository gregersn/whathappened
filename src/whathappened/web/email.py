"""Email functions."""

from typing import List, Optional, Tuple, Union
from threading import Thread
from flask_mail import Message, Mail
from flask import current_app, Flask

mail = Mail()


def send_async_email(app: Flask, msg: Message):
    """Send an email async."""
    with app.app_context():
        mail.send(msg)


def send_mail(
    subject: str,
    sender: str,
    recipients: Union[List[Union[str, Tuple[str, str]]], None],
    text_body: str,
    html_body: Optional[str] = None,
):
    """Send an email."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body is not None:
        msg.html = html_body
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg),  # pylint: disable=protected-access # type: ignore
    ).start()
