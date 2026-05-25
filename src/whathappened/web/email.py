from threading import Thread


class Mail:
    def send(self, *args, **kwargs):
        raise NotImplementedError("{args}, {kwargs}")


class Message:
    def __init__(self, *args, **kwargs): ...


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
