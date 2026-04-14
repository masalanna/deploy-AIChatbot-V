
import os
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from dotenv               import load_dotenv

load_dotenv()

# SMTP config from environment
SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
NOTIFY_EMAIL  = os.getenv("NOTIFY_EMAIL",  "")   # internal team inbox


def schedule_meeting(
    subject: str,
    date_input: str,
    start_time_input: str,
    duration: int | str,
    attendees_input: str,
) -> dict:
    # Validate SMTP config
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "success": False,
            "message": (
                "❌ SMTP not configured. "
                "Set SMTP_USER and SMTP_PASSWORD in your .env file."
            ),
        }

    if isinstance(duration, str):
        duration = int(duration.split()[0])

    attendees = [e.strip() for e in attendees_input.split(",") if e.strip()]

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            # ── 1. Attendee confirmation email ────────────────────────
            for attendee in attendees:
                msg = _build_attendee_email(
                    to=attendee,
                    subject=subject,
                    date=date_input,
                    time=start_time_input,
                    duration=duration,
                )
                server.sendmail(SMTP_USER, attendee, msg.as_string())

            # ── 2. Internal team notification ─────────────────────────
            if NOTIFY_EMAIL:
                msg = _build_internal_email(
                    subject=subject,
                    date=date_input,
                    time=start_time_input,
                    duration=duration,
                    attendees=attendees,
                )
                server.sendmail(SMTP_USER, NOTIFY_EMAIL, msg.as_string())

        return {
            "success": True,
            "message": "✅ Meeting confirmation email sent successfully!",
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "❌ SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD.",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Failed to send confirmation: {e}",
        }


# ---------------------------------------------------------------------------
# Email builders
# ---------------------------------------------------------------------------

def _build_attendee_email(
    to: str,
    subject: str,
    date: str,
    time: str,
    duration: int,
) -> MIMEMultipart:
    msg              = MIMEMultipart("alternative")
    msg["Subject"]   = f"Meeting Confirmation: {subject}"
    msg["From"]      = SMTP_USER
    msg["To"]        = to

    plain = textwrap.dedent(f"""\
        Hello,

        Your meeting with Softdel has been scheduled.

        Details:
          Subject  : {subject}
          Date     : {date}
          Time     : {time} (IST)
          Duration : {duration} minutes

        Our team will follow up with a calendar invite shortly.

        Best regards,
        Softdel Virtual Assistant
        www.softdel.com
    """)

    html = f"""\
    <html><body>
    <p>Hello,</p>
    <p>Your meeting with <strong>Softdel</strong> has been confirmed.</p>
    <table border="0" cellpadding="6">
      <tr><td><strong>Subject</strong></td><td>{subject}</td></tr>
      <tr><td><strong>Date</strong></td><td>{date}</td></tr>
      <tr><td><strong>Time</strong></td><td>{time} (IST)</td></tr>
      <tr><td><strong>Duration</strong></td><td>{duration} minutes</td></tr>
    </table>
    <p>Our team will follow up with a calendar invite shortly.</p>
    <p>Best regards,<br>
    <strong>SVA — Softdel Virtual Assistant</strong><br>
    <a href="https://www.softdel.com">www.softdel.com</a></p>
    </body></html>
    """

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))
    return msg


def _build_internal_email(
    subject: str,
    date: str,
    time: str,
    duration: int,
    attendees: list,
) -> MIMEMultipart:
    msg              = MIMEMultipart()
    msg["Subject"]   = f"[SVA] New Meeting Request: {subject}"
    msg["From"]      = SMTP_USER
    msg["To"]        = NOTIFY_EMAIL

    body = textwrap.dedent(f"""\
        New meeting scheduled via Softdel Virtual Assistant.

        Subject    : {subject}
        Date       : {date}
        Time       : {time} (IST)
        Duration   : {duration} minutes
        Attendees  : {', '.join(attendees)}

        Please send a calendar invite to the attendee(s) above.
    """)

    msg.attach(MIMEText(body, "plain"))
    return msg


if __name__ == "__main__":
    print("📧 Portable SMTP Scheduler — CLI Test\n")
    result = schedule_meeting(
        subject          = input("Meeting subject: "),
        date_input       = input("Date (YYYY-MM-DD): "),
        start_time_input = input("Start time (HH:MM, 24h): "),
        duration         = int(input("Duration (minutes): ")),
        attendees_input  = input("Attendee emails (comma-separated): "),
    )
    print(result["message"])
