import logging

import boto3

from msc.constants import EMAIL_SENDER

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    recipient: str,
    template: str,
    params: dict,
):
    try:
        with open(f"msc/templates/{template}.html", "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError as err:
        logger.error("File not found")
    except Exception as err:
        logger.error(f"An error occured: {err}")

    html_content = _build_email_template(
        params=params,
        html=html_content,
    )

    ses_client = boto3.client("ses")

    email_message = {
        "Subject": {"Data": subject},
        "Body": {"Html": {"Data": html_content}},
    }

    # send the email
    response = ses_client.send_email(
        Source=EMAIL_SENDER,
        Destination={
            "ToAddresses": [recipient],
            "BccAddresses": [EMAIL_SENDER],
        },
        Message=email_message,
    )


def _build_email_template(params: dict, html: str) -> str:
    for key, value in params.items():
        html = html.replace(f"%%{key}%%", str(value))
    return html
