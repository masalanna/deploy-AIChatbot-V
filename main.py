
import os
import uuid
import sqlite3

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

import rag_engine
import intent_router
import memory_manager

load_dotenv()

_SCHEDULER_BACKEND = os.getenv("SCHEDULER_BACKEND", "smtp").lower()

if _SCHEDULER_BACKEND == "win":
    try:
        from scheduler_win import schedule_meeting
        print("[main] 📅 Scheduler: Outlook/win32com")
    except ImportError:
        print("[main] ⚠️  win32com not available — using SMTP")
        from scheduler_portable import schedule_meeting
else:
    from scheduler_portable import schedule_meeting
    print("[main] 📧 Scheduler: SMTP")


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "softdel-sva-2025")

def init_db():
    conn = sqlite3.connect("scheduler.db")
    c    = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            mobile           TEXT NOT NULL,
            email            TEXT NOT NULL,
            meeting_date     TEXT NOT NULL,
            meeting_time     TEXT NOT NULL,
            meeting_duration TEXT NOT NULL,
            created_at       TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
init_db()
rag_engine.initialize()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data       = request.get_json(silent=True) or {}
    user_input = data.get("user_input", "").strip()

    if not user_input:
        return jsonify({"response": "Please type a message.", "show_form": False})

    # ── Session ID ─────────────────────────────────────────────────────
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]

    print(f"[chat] session={session_id[:8]}... | input='{user_input}'")

    # ── Route ──────────────────────────────────────────────────────────
    result = intent_router.route(user_input, session_id)
    intent = result["intent"]

    print(f"[chat] intent={intent}")

    # Casual / pricing / action — response already built by router
    if intent in ("casual", "pricing", "action"):
        return jsonify({
            "response":  result["response"],
            "show_form": result.get("show_form", False),
        })

    # Knowledge — call RAG engine
    # result["query"] is already normalized + context-resolved
    # result["is_followup"] tells rag_engine to use deeper retrieval + expand prompt
    answer = rag_engine.get_answer(
        result["query"],
        session_id,
        is_followup=result.get("is_followup", False),
    )

    return jsonify({"response": answer, "show_form": False})


@app.route("/submit_schedule", methods=["POST"])
def submit_schedule():
    data = request.get_json(silent=True) or {}

    try:
        name     = data["name"]
        mobile   = data["mobile"]
        email    = data["email"]
        date     = data["date"]
        time     = data["time"]
        duration = data.get("duration", "30")

        # Call scheduler
        result = schedule_meeting(
            subject          = f"Call with {name}",
            date_input       = date,
            start_time_input = time,
            duration         = duration,
            attendees_input  = email,
        )

        print(f"[schedule] result={result}")

        # Save to DB only on success
        if result.get("success"):
            conn = sqlite3.connect("scheduler.db")
            c    = conn.cursor()
            c.execute(
                """INSERT INTO meetings
                   (name, mobile, email, meeting_date, meeting_time, meeting_duration)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, mobile, email, date, time, str(duration)),
            )
            conn.commit()
            conn.close()

        return jsonify(result)

    except KeyError as e:
        return jsonify({"success": False, "message": f"Missing field: {e}"})
    except Exception as e:
        print(f"[schedule] error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."})


@app.route("/clear_session", methods=["POST"])
def clear_session_endpoint():
    """Clear conversation history for the current session."""
    if "session_id" in session:
        memory_manager.clear_session(session["session_id"])
        session.pop("session_id", None)
        return jsonify({"success": True, "message": "Session cleared."})
    return jsonify({"success": False, "message": "No active session."})


@app.route("/session_info", methods=["GET"])
def session_info_endpoint():
    """Return current session debug info."""
    if "session_id" in session:
        return jsonify(memory_manager.get_session_info(session["session_id"]))
    return jsonify({
        "session_id": None, "question_count": 0,
        "topics_discussed": [], "conversation_length": 0,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
