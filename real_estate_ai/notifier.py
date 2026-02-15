import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration (set these in .env file)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

def send_email_alert(lead_data):
    if not SMTP_USER or not SMTP_PASSWORD or not EMAIL_RECEIVER:
        print("Email credentials not set. Skipping email notification.")
        return

    subject = f"High Priority Lead Alert: {lead_data.get('intent_type')} - Score {lead_data.get('lead_score')}"

    body = f"""
    <h2>New High Priority Lead Detected</h2>
    <p><b>Title:</b> {lead_data.get('post_title')}</p>
    <p><b>Intent:</b> {lead_data.get('intent_type')} (Confidence: {lead_data.get('intent_confidence')})</p>
    <p><b>Score:</b> {lead_data.get('lead_score')}</p>
    <p><b>Price:</b> {lead_data.get('price')}</p>
    <p><b>Location:</b> {lead_data.get('location')}</p>
    <p><b>Contact:</b> {lead_data.get('phone')} / {lead_data.get('email')}</p>
    <p><b>Description:</b> {lead_data.get('full_description')}</p>
    <p><b>Source:</b> {lead_data.get('source_platform')}</p>
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email alert sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

def send_daily_summary_report(summary):
    if not SMTP_USER or not SMTP_PASSWORD or not EMAIL_RECEIVER:
        print("Email credentials not set. Skipping daily summary.")
        return

    subject = f"Daily Real Estate Lead Summary - {summary['total']} New Leads"

    body = f"""
    <h2>Daily Lead Summary Report</h2>
    <p><b>Total Leads Found:</b> {summary['total']}</p>
    <p><b>Sellers:</b> {summary['sellers']}</p>
    <p><b>Buyers:</b> {summary['buyers']}</p>
    <p><b>Average Lead Score:</b> {summary['avg_score']:.2f}</p>
    <p>Visit your dashboard to view full details.</p>
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Daily summary sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"Failed to send daily summary: {e}")
