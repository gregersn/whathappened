from typing import List, Optional
from threading import Thread
from flask_mail import Message, Mail
from flask import current_app, Flask

mail = Mail()


def send_async_email(app: Flask, msg: str):
    with app.app_context():
        mail.send(msg)


def send_mail(
    subject: str,
    sender: str,
    recipients: List[str],
    text_body: str,
    html_body: Optional[str] = None,
):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body is not None:
        msg.html = html_body
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()  # pyright: ignore[reportGeneralTypeIssues]
