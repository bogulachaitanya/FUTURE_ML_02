import smtplib
from email.mime.text import MIMEText
import pandas as pd
import os
import sqlite3
import subprocess
from flask import Flask, render_template, request, send_file,redirect
from flask import session, redirect, url_for
import joblib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "support_ticket_secret"
# Load ML files
category_model = joblib.load("models/category_model.pkl")
priority_model = joblib.load("models/priority_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

# Dataset
df = pd.read_csv("data/tickets.csv")

model_accuracy = 54.55
dataset_size = len(df)
report_file = "reports/ticket_report.csv"
most_common_category = "N/A"
category_percentage = 0

if os.path.exists(report_file):
    report_df = pd.read_csv(report_file)
    if len(report_df) > 0:
        top_category = report_df["Category"].value_counts()
        most_common_category = top_category.idxmax()
        category_percentage = round((top_category.max() / len(report_df)) * 100, 2)

if os.path.exists(report_file):
    analyzed_count = len(pd.read_csv(report_file))
else:
    analyzed_count = 0
critical_count = 0
if os.path.exists(report_file):
    report_df = pd.read_csv(report_file)
    if "Priority" in report_df.columns:
        critical_count = len(report_df[report_df["Priority"] == "Critical"])

total_tickets = len(df)

billing_count = len(df[df["category"] == "Billing"])
account_count = len(df[df["category"] == "Account"])
technical_count = len(df[df["category"] == "Technical"])
general_count = len(df[df["category"] == "General Query"])

ticket_counter = 1000
history = []

def send_ticket_email(
    ticket_id,
    category,
    priority,
    confidence,
    timestamp
):

    sender = "chpurush5@gmail.com"

    app_password = os.getenv("EMAIL_PASSWORD")

    receiver = "chpurush5@gmail.com"

    body = f"""
New Ticket Generated

Ticket ID: {ticket_id}

Category: {category}

Priority: {priority}

Confidence: {confidence}%

Timestamp: {timestamp}
"""

    msg = MIMEText(body)

    msg["Subject"] = "New Support Ticket"

    msg["From"] = sender

    msg["To"] = receiver

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        sender,
        app_password
    )

    server.send_message(msg)

    server.quit()

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["user"] = username

            return redirect("/admin")

        else:

            error = "Invalid Username or Password"

    return render_template(
        "login.html",
        error=error
    )
@app.route("/", methods=["GET", "POST"])
def home():

    global ticket_counter

    category = None
    priority = None
    confidence = None
    confidence_color = "red"
    ticket_id = None
    timestamp = None
    category_icon = None

    if request.method == "POST":

        ticket = request.form["ticket"]

        ticket_vectorized = vectorizer.transform([ticket])

        # ML Prediction
        category = category_model.predict(ticket_vectorized)[0]
        priority = priority_model.predict(ticket_vectorized)[0]

        # Critical Ticket Detection
        urgent_keywords = [
            "server down",
            "website down",
            "database crash",
            "database crashed",
            "system hacked",
            "security breach",
            "all users affected",
            "payment failure",
            "service unavailable",
            "critical issue"
        ]

        ticket_lower = ticket.lower()

        for keyword in urgent_keywords:
            if keyword in ticket_lower:
                priority = "Critical"
                break

        # Confidence
        confidence = round(
            max(category_model.predict_proba(ticket_vectorized)[0]) * 100,
            2
        )
        if confidence >= 80:
            confidence_color = "green"
        elif confidence >= 50:
            confidence_color = "orange"
        else:
            confidence_color = "red"

        # Ticket ID
        ticket_counter += 1
        ticket_id = f"TKT-{ticket_counter}"

        # Timestamp
        timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        # Icons
        icon_map = {
            "Billing": "💳",
            "Account": "🔐",
            "Technical": "🛠️",
            "General Query": "❓"
        }

        category_icon = icon_map.get(category, "📄")

        # History
        history.insert(0, {
            "ticket_id": ticket_id,
            "category": category,
            "priority": priority
        })

        history[:] = history[:5]

        # Report Generation
        report_data = pd.DataFrame([{
            "Ticket ID": ticket_id,
            "Category": category,
            "Priority": priority,
            "Confidence": confidence,
            "Timestamp": timestamp
        }])

        report_path = "reports/ticket_report.csv"

        if os.path.exists(report_path):

            old_df = pd.read_csv(report_path)

            report_data = pd.concat(
                [old_df, report_data],
                ignore_index=True
            )

        report_data.to_csv(
            report_path,
            index=False
        )
        # Save to SQLite Database
        conn = sqlite3.connect("support_tickets.db")
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO tickets(ticket_id,category,priority,confidence,timestamp,status)VALUES (?, ?, ?, ?, ?, ?)""",
            (ticket_id, category, priority, confidence, timestamp, "Open")
        )
        conn.commit()
        conn.close()

        try:send_ticket_email(ticket_id,category,priority,confidence,timestamp)
        
        except:pass
      

    return render_template(
        "index.html",
        category=category,
        priority=priority,
        confidence=confidence,
        ticket_id=ticket_id,
        timestamp=timestamp,
        category_icon=category_icon,
        total_tickets=total_tickets,
        billing_count=billing_count,
        account_count=account_count,
        technical_count=technical_count,
        general_count=general_count,
        model_accuracy=model_accuracy,
        dataset_size=dataset_size,
        analyzed_count=analyzed_count,
        most_common_category=most_common_category,
category_percentage=category_percentage,
critical_count=critical_count,
confidence_color=confidence_color,
        history=history
    )


@app.route("/download-report")
def download_report():

    report_path = "reports/ticket_report.csv"

    if os.path.exists(report_path):
        return send_file(
            report_path,
            as_attachment=True
        )

    return "No report available"

@app.route("/search", methods=["POST"])
def search():

    keyword = request.form["keyword"]

    report_path = "reports/ticket_report.csv"

    results = []

    if os.path.exists(report_path):

        df_search = pd.read_csv(report_path)

        results = df_search[
            df_search["Category"].astype(str).str.contains(
                keyword,
                case=False,
                na=False
            )
            |
            df_search["Ticket ID"].astype(str).str.contains(
                keyword,
                case=False,
                na=False
            )
        ].to_dict("records")

    return render_template(
        "search_results.html",
        keyword=keyword,
        results=results
    )
@app.route("/tickets")
def view_tickets():

    conn = sqlite3.connect(
        "support_tickets.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        ORDER BY id DESC
        """
    )

    tickets = cursor.fetchall()

    conn.close()

    return render_template(
        "tickets.html",
        tickets=tickets
    )
@app.route("/delete/<int:id>")
def delete_ticket(id):

    conn = sqlite3.connect(
        "support_tickets.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tickets
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/tickets")
@app.route("/update-status/<int:id>/<status>")
def update_status(id, status):

    conn = sqlite3.connect(
        "support_tickets.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status=?
        WHERE id=?
        """,
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect("/tickets")
@app.route("/admin")
def admin_dashboard():
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect(
        "support_tickets.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tickets"
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE priority='Critical'"
    )
    critical = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Open'"
    )
    open_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='In Progress'"
    )
    in_progress = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Resolved'"
    )
    resolved = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Closed'"
    )
    closed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COUNT(*)
        FROM tickets
        GROUP BY category
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    top_category = cursor.fetchone()

    conn.close()

    return render_template(
        "admin.html",
        total=total,
        critical=critical,
        open_count=open_count,
        in_progress=in_progress,
        resolved=resolved,
        closed=closed,
        top_category=top_category
    )
@app.route("/export-excel")
def export_excel():

    conn = sqlite3.connect(
        "support_tickets.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM tickets",
        conn
    )

    conn.close()

    file_path = "tickets_export.xlsx"

    df.to_excel(
        file_path,
        index=False
    )

    return send_file(
        file_path,
        as_attachment=True
    )
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")
if __name__ == "__main__":
    app.run()