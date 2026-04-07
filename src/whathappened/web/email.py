from threading import Thread

from flask import Flask, current_app
from flask_mail import Mail, Message

mail = Mail()


def send_async_email(app: Flask, msg: str):
    with app.app_context():
        mail.send(Message(body=msg))


def send_mail(
    subject: str,
    sender: str,
    recipients: list[str | tuple[str, str]],
    text_body: str,
    html_body: str | None = None,
):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body is not None:
        msg.html = html_body
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()  # pyright: ignore[reportGeneralTypeIssues]
