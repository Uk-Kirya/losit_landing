from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME='no-reply@losplatform.ru',
    MAIL_PASSWORD='35XcbbEsayE5',
    MAIL_FROM='no-reply@losplatform.ru',
    MAIL_PORT=587,
    MAIL_SERVER='connect.smtp.bz',
    MAIL_FROM_NAME='Los—IT',
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


async def send_email(recipient: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
