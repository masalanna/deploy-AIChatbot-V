
import datetime
import pythoncom
import win32com.client
from zoneinfo import ZoneInfo


def schedule_meeting(
    subject: str,
    date_input: str,
    start_time_input: str,
    duration: int | str,
    attendees_input: str,
) -> dict:
    try:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application")
        meeting = outlook.CreateItem(1)  # 1 = olAppointmentItem

        # Parse duration — accept both int and "30 minutes" string
        if isinstance(duration, str):
            duration = int(duration.split()[0])

        # Build timezone-aware datetime
        tz             = ZoneInfo("Asia/Kolkata")
        start_datetime = datetime.datetime.strptime(
            f"{date_input} {start_time_input}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=tz)

        # Attendee list
        attendees = [e.strip() for e in attendees_input.split(",") if e.strip()]

        # Populate meeting item
        meeting.Subject       = subject
        meeting.Start         = start_datetime
        meeting.Duration      = duration
        meeting.Location      = "Microsoft Teams Meeting"
        meeting.Body          = (
            "This meeting has been scheduled via Softdel Virtual Assistant.\n\n"
            "A Teams link will be included automatically by Outlook."
        )
        meeting.MeetingStatus = 1  # 1 = olMeeting (enables recipients)

        for email in attendees:
            meeting.Recipients.Add(email)

        meeting.Save()
        meeting.Send()

        return {
            "success": True,
            "message": "✅ Teams meeting scheduled successfully!",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Failed to schedule meeting: {e}",
        }

    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    print("📅 Outlook Teams Scheduler — CLI Test\n")
    result = schedule_meeting(
        subject          = input("Meeting subject: "),
        date_input       = input("Date (YYYY-MM-DD): "),
        start_time_input = input("Start time (HH:MM, 24h): "),
        duration         = int(input("Duration (minutes): ")),
        attendees_input  = input("Attendee emails (comma-separated): "),
    )
    print(result["message"])
