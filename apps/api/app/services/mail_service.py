from __future__ import annotations

import logging
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import quote_plus

import boto3
from botocore.config import Config

from app.config import settings

logger = logging.getLogger("app.mail")

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"


def _safe_context(context: dict[str, Any]) -> dict[str, str]:
    return {k: ("" if v is None else str(v)) for k, v in context.items()}


@lru_cache(maxsize=1)
def _ses_client():
    return boto3.client(
        "ses",
        region_name=settings.aws_region,
        config=Config(connect_timeout=2, read_timeout=4, retries={"max_attempts": 2}),
    )


class MailService:
    @staticmethod
    def _format_event_datetime(value: str) -> str:
        try:
            normalized = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            weekday = dt.strftime("%A")
            month = dt.strftime("%B")
            day = dt.day
            year = dt.year
            time_part = dt.strftime("%I:%M %p").lstrip("0")
            zone = dt.tzname() or "UTC"
            return f"{weekday}, {month} {day}, {year} · {time_part} {zone}"
        except ValueError:
            return value

    @staticmethod
    def _default_public_url() -> str:
        origins = settings.cors_origins_list
        if origins:
            return origins[0]
        return "https://www.openmat.app"

    @staticmethod
    def _render(name: str, context: dict[str, Any]) -> str:
        path = TEMPLATE_DIR / name
        raw = path.read_text(encoding="utf-8")
        return Template(raw).safe_substitute(_safe_context(context))

    @staticmethod
    def _from_header() -> str:
        return f"{settings.mail_from_name} <{settings.mail_from_email}>"

    @classmethod
    def send_email(
        cls,
        *,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        cc_emails: list[str] | None = None,
    ) -> bool:
        try:
            destination: dict[str, list[str]] = {"ToAddresses": [to_email]}
            if cc_emails:
                destination["CcAddresses"] = cc_emails

            _ses_client().send_email(
                Source=cls._from_header(),
                Destination=destination,
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
                ReplyToAddresses=[settings.mail_reply_to],
            )
            logger.info("mail.sent", extra={"event": "mail.sent", "to": to_email, "subject": subject})
            return True
        except Exception as exc:  # noqa: BLE001 - external provider failures should be isolated
            logger.exception(
                "mail.failed",
                extra={"event": "mail.failed", "to": to_email, "subject": subject, "error": str(exc)},
            )
            return False

    @classmethod
    def send_booking_confirmation(
        cls,
        *,
        customer_email: str,
        customer_name: str | None,
        deal_title: str,
        starts_at: str,
        location: str,
        booking_number: str,
    ) -> bool:
        context = {
            "customer_name": customer_name or "there",
            "deal_title": deal_title,
            "starts_at": starts_at,
            "starts_at_pretty": cls._format_event_datetime(starts_at),
            "location": location,
            "booking_number": booking_number,
            "manage_booking_url": f"{cls._default_public_url().rstrip('/')}/",
            "view_details_url": f"{cls._default_public_url().rstrip('/')}/",
            "contact_host_url": f"mailto:{settings.mail_reply_to}",
        }
        return cls.send_email(
            to_email=customer_email,
            subject=f"Booking confirmed: {deal_title}",
            html_body=cls._render("booking_confirmation.html", context),
            text_body=cls._render("booking_confirmation.txt", context),
            cc_emails=[settings.mail_from_email],
        )

    @classmethod
    def send_password_reset(cls, *, customer_email: str, reset_url: str) -> bool:
        context = {"reset_url": reset_url}
        return cls.send_email(
            to_email=customer_email,
            subject="Reset your OpenMat password",
            html_body=cls._render("password_reset.html", context),
            text_body=cls._render("password_reset.txt", context),
        )

    @classmethod
    def send_wallet_pass_delivery(
        cls,
        *,
        customer_email: str,
        customer_name: str | None,
        deal_title: str,
        qr_code: str,
    ) -> bool:
        context = {
            "customer_name": customer_name or "there",
            "deal_title": deal_title,
            "qr_code": qr_code,
            "qr_image_url": f"https://api.qrserver.com/v1/create-qr-code/?size=420x420&margin=8&data={quote_plus(qr_code)}",
            "view_pass_url": f"{cls._default_public_url().rstrip('/')}/",
            "download_qr_url": f"{cls._default_public_url().rstrip('/')}/",
            "open_booking_url": f"{cls._default_public_url().rstrip('/')}/",
        }
        return cls.send_email(
            to_email=customer_email,
            subject=f"Your OpenMat pass is ready: {deal_title}",
            html_body=cls._render("wallet_pass_delivery.html", context),
            text_body=cls._render("wallet_pass_delivery.txt", context),
            cc_emails=[settings.mail_from_email],
        )

    @classmethod
    def send_redemption_confirmation(
        cls,
        *,
        customer_email: str | None,
        customer_name: str | None,
        deal_title: str,
        redeemed_at: str,
    ) -> bool:
        if not customer_email:
            return False
        context = {
            "customer_name": customer_name or "there",
            "deal_title": deal_title,
            "redeemed_at": redeemed_at,
            "redeemed_at_pretty": cls._format_event_datetime(redeemed_at),
            "view_booking_url": f"{cls._default_public_url().rstrip('/')}/",
            "support_url": f"mailto:{settings.mail_reply_to}",
        }
        return cls.send_email(
            to_email=customer_email,
            subject=f"Pass redeemed: {deal_title}",
            html_body=cls._render("redemption_confirmation.html", context),
            text_body=cls._render("redemption_confirmation.txt", context),
            cc_emails=[settings.mail_from_email],
        )

    @classmethod
    def send_payout_notification(
        cls,
        *,
        recipient_email: str,
        amount: str,
        payout_date: str,
    ) -> bool:
        context = {
            "amount": amount,
            "payout_date": payout_date,
            "payout_date_pretty": cls._format_event_datetime(payout_date),
            "dashboard_url": f"{cls._default_public_url().rstrip('/')}/dashboard",
            "support_url": f"mailto:{settings.mail_reply_to}",
        }
        return cls.send_email(
            to_email=recipient_email,
            subject="OpenMat payout processed",
            html_body=cls._render("payout_notification.html", context),
            text_body=cls._render("payout_notification.txt", context),
        )

    @classmethod
    def send_onboarding_welcome(
        cls,
        *,
        recipient_email: str | None,
        practitioner_name: str,
    ) -> bool:
        if not recipient_email:
            return False
        context = {
            "practitioner_name": practitioner_name,
            "create_deal_url": f"{cls._default_public_url().rstrip('/')}/dashboard/deals",
            "dashboard_url": f"{cls._default_public_url().rstrip('/')}/dashboard",
            "support_url": f"mailto:{settings.mail_reply_to}",
        }
        return cls.send_email(
            to_email=recipient_email,
            subject="Welcome to OpenMat",
            html_body=cls._render("onboarding_welcome.html", context),
            text_body=cls._render("onboarding_welcome.txt", context),
            cc_emails=[settings.mail_from_email],
        )
