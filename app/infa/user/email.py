from datetime import timedelta
from typing import Optional

from app.email.sendinblue_service import SendinblueService
from celery_worker import celery, logger
from app.config import config
from app.infa.security.security_service import create_access_token
from celery_worker import celery_delay
from app.domain.enum import AuthGrantType
from app.shared.utils.general import get_prefix_email_subject

sendinlbue_service = SendinblueService()


@celery.task(serializer="pickle", ignore_result=True)
def send_register_email(mail_to: str, password: str):
    try:
        logger.info("Send register confirmation to #email {}".format(mail_to))
        if not config["EMAIL_ENABLED"]:
            return False

        sendinblue_service = sendinlbue_service
        sendinblue_service.send_register_email(mail_to=mail_to, password=password)
    except Exception as ex:
        logger.exception(ex)


@celery.task(serializer="pickle", ignore_result=True)
def send_forgot_email(mail_to: str, password: str):
    try:
        logger.info("Send forgot email password to #email {}".format(mail_to))
        if not config["EMAIL_ENABLED"]:
            return False

        sendinblue_service = sendinlbue_service
        sendinblue_service.send_forgot_email(mail_to=mail_to, password=password)
    except Exception as ex:
        logger.exception(ex)


@celery.task(serializer="pickle", ignore_result=True)
def send_confirm_email(email: str, id: str):
    token = create_access_token(
        data={"sub": email, "id": id}, expires_delta=timedelta(days=2)
    )
    html_content = f"""
        <div style='font-family: "Lato","Helvetica Neue",helvetica,sans-serif;'>
        <h1 style="font-weight: 600; font-size: 18px;">Confirm Email</h1>
        <p style="font-size: 16px;">Please confirm your email <a href='#'>({email})</a> by clicking the button below. This link will expire in 48 hours.</p>
        <a href="/token={token}" style="font-size:16px; font-weight: 600;border-radius:5px;padding: 8px 15px; color: white; background: #791FF4; text-decoration: unset;">Confirm</a>
        </div>
    """
    sendinlbue_service._send(
        sender=config["EMAIL_SENDER"],
        emails_to=[email],
        subject="Confirm Email",
        text_content=html_content,
    )


# region send verify code email
@celery.task(serializer="pickle", ignore_result=True)
def send_verfify_code_task(
    email: str, code: int, name: str, domain: Optional[str] = None
):
    subject = get_prefix_email_subject(
        subject="Verify your Tubekick account - Here's your verification code 📬",
        domain=domain,
    )
    sendinlbue_service._send(
        sender=config["EMAIL_SENDER"],
        emails_to=[email],
        subject=subject,
        name=name,
    )


def send_verify_code(
    email: str, code: int, id: str, name: str, domain: Optional[str] = None
) -> str:
    token = create_access_token(
        data={
            "sub": email,
            "grant_type": AuthGrantType.VERIFY_CODE.value,
            "id": id,
        },
        expires_delta=timedelta(hours=24),
    )
    if config["ENVIRONMENT"] and config["ENVIRONMENT"] != "local":
        send_verfify_code_task(
            email=email,
            code=code,
            domain=domain,
            name="ACMO",
        )

    return token


# endregion


# region send reset password email
@celery.task(serializer="pickle", ignore_result=True)
def send_reset_password_task(
    email: str,
    id: str,
    name: str,
    domain: Optional[str] = config["USER_CONFIRM_EMAIL_URL"],
):
    subject = get_prefix_email_subject(
        subject="Reset your Tubekick password - Your password reset link is here 🔒",
        domain=domain,
    )
    token = create_access_token(
        data={"sub": email, "id": id, "grant_type": AuthGrantType.RESET_PASSWORD.value},
        expires_delta=timedelta(hours=int(config["EXPIRES_RESET_TOKEN_IN_HOURS"])),
    )
    link = f"{domain}/auth/reset-password?token={token}"
    sendinlbue_service._send(
        sender=config["EMAIL_SENDER"],
        emails_to=[email],
        subject=subject,
        template_id=config["USER_RESET_PASSWORD_EMAIL_TEMPLATE"],
        params=dict(name=name, link=link),
    )


def send_reset_password(email: str, id: str, name: str, domain: Optional[str] = None):
    if config["ENVIRONMENT"] and config["ENVIRONMENT"] != "local":
        celery_delay(
            send_reset_password_task,
            email=email,
            id=id,
            name=name,
            domain=domain,
        )(task_id="send_confirm_email_to_{}".format(email))


# endregion


# region send user welcome email
@celery.task(serializer="pickle", ignore_result=True)
def send_user_welcome_email_task(email: str, name: str, domain: Optional[str] = None):
    subject = get_prefix_email_subject(
        subject="Welcome to the Tubekick Reseller Platform!", domain=domain
    )
    sendinlbue_service._send(
        sender=config["EMAIL_SENDER"],
        emails_to=[email],
        subject=subject,
        name=name,
        text_content="welcome to ACMO"
    )


def send_welcome_email(email: str, name: str, domain: Optional[str] = None):
    if config["ENVIRONMENT"] and config["ENVIRONMENT"] != "local":
        send_user_welcome_email_task(
            email=email,
            domain=domain,
            name=name,
        )


# endregion


# region send topup balance success
@celery.task(serializer="pickle", ignore_result=True)
def send_user_top_up_confirm_email_task(
    email: str,
    name: str,
    amount: float,
    transaction_id: str,
    date: str,
    new_balance: float,
    domain: Optional[str] = None,
):
    subject = get_prefix_email_subject(
        subject="We have topped up your Tubekick Wallet!", domain=domain
    )
    sendinlbue_service._send(
        sender=config["EMAIL_SENDER"],
        emails_to=[email],
        subject=subject,
        template_id=config["USER_TOP_UP_CONFIRM_EMAIL_TEMPLATE"],
        params=dict(
            name=name,
            amount="%.2f" % amount,
            transaction_id=transaction_id[-7:].upper(),
            date=date,
            new_balance="%.2f" % new_balance,
        ),
    )


def send_user_top_up_confirm(
    email: str,
    name: str,
    amount: float,
    transaction_id: str,
    date: str,
    new_balance: float,
    domain: Optional[str] = None,
):
    if config["ENVIRONMENT"] and config["ENVIRONMENT"] != "local":
        celery_delay(
            send_user_top_up_confirm_email_task,
            email=email,
            name=name,
            amount=amount,
            transaction_id=transaction_id,
            date=date,
            new_balance=new_balance,
            domain=domain,
        )(task_id="send_user_top_up_confirm_email_to_{}".format(email))


# endregion
